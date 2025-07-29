import os
from typing import Any
import argparse
import httpx
from mcp.server.fastmcp import FastMCP
from geopy.geocoders import Nominatim

# Initialize FastMCP server
mcp = FastMCP("weather")

# Initialize geocoder
geolocator = Nominatim(user_agent="weather-app", timeout=10)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

def format_forecast(period: dict) -> str:
    """Format a forecast period into a readable string."""
    return f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""

async def geocode_location(location: str) -> dict:
    """Convert a location name to latitude and longitude coordinates.

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

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get weather forecast for a location.

    Args:
        location: Name of the location (city, address, etc.)
    """
    latitude_longitude = await geocode_location(location)
    if "error" in latitude_longitude:
        return latitude_longitude["error"]
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude_longitude['latitude']},{latitude_longitude['longitude']}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods:
        forecast = format_forecast(period)
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


def main():
    """Main entry point for the weather MCP server."""
    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="streamable-http",
        help="Transport method to use (default: streamable-http)"
    )

    args = parser.parse_args()

    print(f"Starting weather MCP server with transport: {args.transport}")
    mcp.settings.port = int(os.getenv("MCP_PORT", "8080"))
    mcp.settings.host = '0.0.0.0'
    mcp.run(transport=args.transport)

if __name__ == "__main__":
    main()
