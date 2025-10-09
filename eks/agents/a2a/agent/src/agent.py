import os
import json
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent, tool
from strands.tools.mcp.mcp_client import MCPClient
from urllib import request
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="agent-app/1.0", timeout=10)
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# Strands Agent SDK Community Tools Package
from strands_tools import current_time

# Custom Python Tool
@tool
def geocode_location(location: str) -> dict:
    """Convert a location string to latitude and longitude coordinates.
    Args:
        location: Name of the location (city, address, etc.)
    Returns:
        Dictionary with latitude and longitude
    """
    try:
        location_data = geolocator.geocode(location)
        if location_data:
            return {
                "latitude": round(location_data.latitude, 4),
                "longitude": round(location_data.longitude, 4),
                "address": location_data.address
            }
        return {"error": "Location not found"}
    except Exception as e:
        return {"error": str(e)}

# MCP Tools
def get_mcp_tools():
    mcp_url = os.getenv("WEATHER_MCP_URL", f"http://localhost:8080/mcp")
    mcp_client = MCPClient(lambda: streamablehttp_client(mcp_url))
    mcp_client.start()
    return mcp_client.list_tools_sync()

# Agent Definition
def get_agent():
    agent = Agent(
        name="Agent",
        description="Agent with skills like get the weather forecast up to 7 days in US City, current time or date, and convert a US City or Address to coordinates",
        model=BEDROCK_MODEL_ID,
        system_prompt="""
        You are a helpful Assistant, you assist the user on any task or question,
        task like convert a US location(city, address, etc.) to latitude and longitude coordinates
        task like what's the weather forecast in a US City or Address location
        task like find weather alerts for a given US State
        task like what's the current time or date
        """,
        tools=[current_time, geocode_location, get_mcp_tools()]
    )
    return agent

def main():
    agent = get_agent()
    agent("What's the weather forecast for San Francisco two days from now?")

if __name__ == "__main__":
    main()
