from strands import Agent, tool
from strands_tools.a2a_client import A2AClientToolProvider
from strands.multiagent.a2a import A2AServer
from fastapi import FastAPI
import uvicorn
import logging
import sys
import os
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if (os.getenv("DEBUG", "").lower() in ("1", "true", "yes")) else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)


# A2A Client as Agent Tool
@tool
def a2a_remote_agent_interface(request: str) -> str:
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
        """,
        tools=[a2a_remote_agent_interface]
    )
    return agent

# Restful API server for multi-agent, useful when exposing using AWS Network Load Balancer
def run_restapi_server():
    """Start the FastAPI server"""
    app = FastAPI()

    @app.get("/healthz")
    async def health_check():
        return {"status": "healthy"}

    @app.post("/prompt")
    async def handle_prompt(request: dict) -> dict:
        agent = travel_agent()
        result = agent(request["text"])
        return {"text": str(result)}

    port = int(os.getenv("FASTAPI_PORT", "3000"))
    logger.info(f"AI Agent FastAPI server on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

# A2A Server for multi-agent, useful when exposing using AWS Network Load Balancer
def run_a2a_server():
    """Start the A2A server"""
    port = int(os.getenv("A2A_PORT", "9001"))
    http_url = os.getenv("A2A_URL", f"http://localhost:{port}")
    agent = travel_agent()
    server = A2AServer(
        agent=agent,
        port=port,
        host="0.0.0.0",
        http_url=http_url
    )
    try:
        logger.info(f"A2A AgentCard on http://localhost:{port}/.well-known/agent-card.json")
        logger.info(f"A2A Server available on http_url:{http_url}")
        logger.info("Press Ctrl+C to stop the server")
        server.serve()
    except KeyboardInterrupt:
        logger.info("\nShutting down A2A server...")
        server.stop()

def main():
    agent = travel_agent()
    agent("Hello, what can you help me with?")

if __name__ == "__main__":
    main()


# This is how you call the server using curl
# curl -s -X POST http://localhost:3000/prompt -H "Content-Type: application/json" -d '{"text":"Plan me a for the next 3 days a vacation in Las Vegas"}' | jq -r .text

