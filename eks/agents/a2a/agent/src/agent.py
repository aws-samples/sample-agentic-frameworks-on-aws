import os
import json
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent, tool
from strands.tools.mcp.mcp_client import MCPClient
from urllib import request
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")

# MCP Tools (Access the remote streamable http MCP Server accesible on WEATHER_MCP_URL)
def get_mcp_tools():
    """Get the list of tools from the MCP server."""
    mcp_url = os.getenv("WEATHER_MCP_URL", f"http://localhost:8080/mcp")
    mcp_client = MCPClient(lambda: streamablehttp_client(mcp_url))
    mcp_client.start()
    return mcp_client.list_tools_sync()

# Import Tools from the Strands Agent SDK Community Tools Package
from strands_tools import current_time


# Agent Definition
def weather_agent():
    agent = Agent(
        description="Helpful agent that assists with weather forecasts, weather alerts, and time/date queries for US locations",
        model=BEDROCK_MODEL_ID,
        system_prompt="""
        Helpful Agent, assists the user on many tasks or questions,
        task like what's the weather forecast in a US City
        task like find weather alerts for a given US State
        task like what's the current time or date
        """,
        tools=[get_mcp_tools(), current_time]
    )
    return agent

def main():
    agent = weather_agent()
    agent("Get today's date and based on this provide the weather forecast for San Francisco in 2 days?")

if __name__ == "__main__":
    main()
