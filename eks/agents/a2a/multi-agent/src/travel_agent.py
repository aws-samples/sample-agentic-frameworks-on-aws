from strands import Agent, tool
from strands_tools.a2a_client import A2AClientToolProvider
from strands.multiagent.a2a import A2AServer
import uvicorn
from fastapi import FastAPI
import logging
import sys
import os
from src.challenge.hotel_agent import hotel_agent_as_tool

BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if (os.getenv("DEBUG", "").lower() in ("1", "true", "yes")) else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)

# Import Tools from the Strands Agent SDK Community Tools Package
from strands_tools import current_time


# A2A Client as Agent Tool
@tool
def weather_agent_as_tool(request: str) -> str:
    """Handle A2A agent connection using A2AClientToolProvider
       Helpful agent that assists with weather forecasts, weather alerts, and time/date queries for US locations
       Leverage tools like: get up to next 7 days weather forecast US city, get weather alert for US state, get current date

    Args:
        request (str): The natural language request to send to the AI Agent
    Returns:
        str: Response from the agent
    Raises:
        Exception: If agent connection fails
    """
    remote_agent_a2a_url = os.getenv("WEATHER_A2A_SERVER_URL", f"http://localhost:9000")
    a2a_tool_provider = A2AClientToolProvider(known_agent_urls=[remote_agent_a2a_url])
    tools = a2a_tool_provider.tools
    logger.info(f"Available remote A2A agent tools: {[tool.tool_name for tool in tools]}")

    agent = Agent(
        model=BEDROCK_MODEL_ID,
        tools=tools,
        system_prompt="You are a agent interface. Discover agents and tools you can use",
        callback_handler=None
    )
    try:
        logger.info(f"Agent received request: {request[:200]}...")
        response = agent(request)
        return str(response)

    except Exception as e:
        logger.error(f"remote a2a agent interface operation failed: {e}")
        raise Exception(f"Failed to process remote a2a agent request: {str(e)}")


def travel_agent() -> Agent:
    agent = Agent(
        model=BEDROCK_MODEL_ID,
        description="""
        Trip advisor agent that recommends activities based on location, current date/time,
        and weather conditions. Coordinates with weather and location agents to provide personalized recommendations.
        """,
        system_prompt="""
        Always check available agents to see if there's one that can help answer the user's question
        As a trip advisor, you can recommend fun activities to the user in a city
        You can only help the user as a Trip Advisor and can provide the following services: user location, current date, and weather forecast
        Use one of the agents to get the user's location if they don't provide one
        Use one of the agents to get weather information
        Use one of the agents to get current time or date
        Always check the weather forecast when providing appropriate activity recommendations
        Take into account weather conditions when suggesting outdoor activities
        Recommend things to bring like umbrella, sunscreen lotion, hat, boots, and attire based on weather conditions
        If you have access to hotel agent, recommend hotels based on location and weather conditions
        """,
        tools=[current_time, weather_agent_as_tool]
    )
    return agent

# A2A Server for multi-agent
def run_a2a_server():
    """Start the A2A server"""
    host = os.getenv("A2A_HOST", "0.0.0.0")
    port = int(os.getenv("A2A_PORT", "9000"))
    http_url = os.getenv("A2A_URL", os.getenv("AGENTCORE_RUNTIME_URL", f"http://localhost:{port}"))
    agent = travel_agent()
    app = FastAPI()
    @app.get("/ping")
    def ping():
        return {"status": "healthy"}
    a2a_server = A2AServer(
        agent=agent,
        port=port,
        host=host,
        http_url=http_url,
        serve_at_root=True  # Serves locally at root (/) regardless of remote URL path complexity
    )
    app.mount("/", a2a_server.to_fastapi_app())
    logger.info(f"A2A AgentCard on http://localhost:{port}/.well-known/agent-card.json")
    logger.info(f"A2A Server available on http_url:{http_url}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_a2a_server()
