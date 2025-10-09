from strands import tool
from datetime import datetime
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="agent-app/1.0", timeout=10)

@tool(name="get_todays_date", description="Retrieves today's date for accuracy")
def get_todays_date() -> str:
    today = datetime.today().strftime('%Y-%m-%d')
    print(f'> get_todays_date today={today}')
    return today

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
