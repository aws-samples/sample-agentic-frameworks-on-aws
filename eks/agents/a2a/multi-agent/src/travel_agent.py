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


@tool
def weather_agent_provider(request: str) -> str:
    """Handle Weather agent connection using a2aclienttoolprovider
       Helpful agent that assists with weather forecasts, weather alerts, and time/date queries for US locations

    Args:
        request (str): The request to send to the weather agent
    Returns:
        str: Response from the weather agent
    Raises:
        Exception: If weather agent connection fails
    """
    weather_agent_a2a_url = os.getenv("WEATHER_A2A_SERVER_URL", f"http://localhost:9000")
     # Initialize provider with memory agent URL
    provider = A2AClientToolProvider(known_agent_urls=[weather_agent_a2a_url])
    logger.debug(f"Initialized weather agent provider: {provider}")
    # Get available tools from provider
    tools = provider.tools
    logger.info(f"Available weather agent tools: {[tool.tool_name for tool in tools]}")
    # Create agent with tools and system prompt
    agent = Agent(
        model=BEDROCK_MODEL_ID,
        tools=tools,
        system_prompt="You are a weather agent interface. Discover agents and tools you can use",
        callback_handler=None
    )
    try:
        # Send request and get response
        logger.info(f"Weather agent received request: {request[:200]}...")
        response = agent(request)
        return str(response)

    except Exception as e:
        logger.error(f"Weather agent operation failed: {e}")
        raise Exception(f"Failed to process weather agent request: {str(e)}")


def travel_agent() -> Agent:
    agent = Agent(
        model=BEDROCK_MODEL_ID,
        description="""
        Trip advisor agent that recommends activities based on location, current date/time,
        and weather conditions. Coordinates with weather and location agents to provide personalized recommendations.
        """,
        system_prompt="""
        Always check agents available to see if there's one that can help answer the user's question
        As trip advisor you can recommend fun activities to the user in a city
        You can only help the user as a Trip Advisor, and can provide the following services like user location, current date, and weather forecast
        Use one of the agents to get the users location if they don't provide one
        Use one of the agents to get weather information
        Use one of the agents to get current time or date
        Always Check the weather forecast when providing appropriate activity recommendations
        Take into account weather conditions when suggesting an outdoor activity
        Recommend things to bring like umbrella, suncreen lotion, hat, boots, attire based on weather conditions
        """,
        tools=[weather_agent_provider]
    )
    return agent

# Restful API server for multi-agent, useful when exposing using AWS Network Load Balancer
def run_restapi_server():
    """Start the FastAPI server"""
    app = FastAPI()
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
    #agent("How can you help me?")
    agent("I'm visting Las Vegas this week")
    #weather_agent_provider("What's the weather like in Atlanta?")

if __name__ == "__main__":
    main()


# This is how you call the server using curl
# curl -s -X POST http://localhost:3000/prompt -H "Content-Type: application/json" -d '{"text":"Plan me a for the next 3 days a vacation in Las Vegas"}' | jq -r .text

