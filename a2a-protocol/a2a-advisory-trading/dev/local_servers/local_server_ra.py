import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime

current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(root_dir))

from config import setup_paths
setup_paths()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from iac.agents.risk_assessment.main.main import RiskAssessmentAgent
from a2a.types import Task, AgentCard, AgentSkill, AgentCapabilities, AgentProvider, Message, TaskStatus, Artifact, TaskState

load_dotenv()

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/.well-known/agent.json")
async def agent_card():
    risk_skill = AgentSkill(
        id="risk-evaluation",
        name="Risk Evaluation",
        description="Performs comprehensive risk assessments for financial instruments and markets, analyzing potential threats, vulnerabilities, and risk factors.",
        tags=["finance", "risk", "analysis", "trading", "aws"],
        examples=[
            "Evaluate the risks in the oil and gas sector given current market conditions.",
            "Assess the risk factors for emerging market investments.",
        ],
        inputModes=["text"],
        outputModes=["text"]
    )
    agent_card = AgentCard(
        name="RiskAssessmentAgent",
        description="Provides detailed risk evaluations and assessments using Amazon Bedrock foundation models.",
        url="http://localhost:8001/message/send",
        provider=AgentProvider(
            organization="AWS Sample Agentic Team",
            url="https://aws.amazon.com/bedrock/"
        ),
        version="1.0.0",
        documentationUrl="https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,
            stateTransitionHistory=False
        ),
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[risk_skill],
        supportsAuthenticatedExtendedCard=False,
    )
    return JSONResponse(json.loads(agent_card.model_dump_json()))

@app.post("/message/send")
async def handle_task(request: Request):
    try:
        body = await request.body()
        body = body.decode("utf-8") if isinstance(body, bytes) else body
        body_json = json.loads(body)

        # === A2A Envelope Unwrapping ===
        if "method" in body_json and "params" in body_json and "message" in body_json["params"]:
            # A2A envelope present, extract Task dict from envelope
            task_dict = body_json["params"]["message"]
        else:
            task_dict = body_json

        task = Task.model_validate(task_dict)
        agent = RiskAssessmentAgent(
            model_id=os.getenv("BEDROCK_MODEL_ID"),
            region=os.getenv("AWS_REGION"),
        )
        result_task = agent.analyze(task)
        return result_task.model_dump(mode='json')
    except Exception as e:
        try:
            task_id = task.id if 'task' in locals() else str(uuid.uuid4())
            context_id = getattr(task, "contextId", None) if 'task' in locals() else None
        except Exception:
            task_id = str(uuid.uuid4())
            context_id = None

        error_parts = [
            {
                "kind": "text",
                "text": str(e),
                "metadata": {}
            }
        ]

        error_message = Message(
            role="agent",
            parts=error_parts,
            messageId=str(uuid.uuid4()),
            kind="message",
            taskId=task_id,
            contextId=str(context_id),
        )

        status = TaskStatus(
            state=TaskState.failed,
            message=error_message,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        error_artifact = Artifact(
            artifactId=str(uuid.uuid4()),
            parts=error_parts,
            name="Error",
            description="Error encountered during market analysis"
        )

        error_task = Task(
            id=task_id,
            contextId=str(context_id),
            status=status,
            artifacts=[error_artifact],
            kind="task"
        )

        return error_task.model_dump(mode='json')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("local_server_ra:app", host="0.0.0.0", port=8001, reload=True)
