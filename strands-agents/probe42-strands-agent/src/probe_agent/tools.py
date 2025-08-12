import os
import httpx
from strands import tool


@tool
async def search_entities(name_starts_with: str, limit: int = 10) -> dict:
    """Search within the database of all Indian corporates by name.
    
    Args:
        name_starts_with: The prefix of the company/LLP name to search for
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching entities with legal name and identifier
    """
    api_key = os.getenv("PROBE_API_KEY")
    if not api_key:
        return {"status": "error", "content": [{"text": "PROBE_API_KEY environment variable is required"}]}
    
    url = "https://api.probe42.in/probe_data_api/search-entities"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    data = {"nameStartsWith": name_starts_with, "limit": limit}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            formatted_response = {
                "companies": result.get("data", {}).get("companies", []),
                "llps": result.get("data", {}).get("llps", [])
            }
            
            return {"status": "success", "content": [{"text": str(formatted_response)}]}
    except Exception as e:
        return {"status": "error", "content": [{"text": f"Error: {str(e)}"}]}


@tool
async def get_base_details(identifier: str) -> dict:
    """Get essential data points about a corporate entity for verification.
    
    Args:
        identifier: CIN, LLPIN, PAN or GSTIN of the entity
    
    Returns:
        Essential details including legal name, status, and registered address
    """
    api_key = os.getenv("PROBE_API_KEY")
    if not api_key:
        return {"status": "error", "content": [{"text": "PROBE_API_KEY environment variable is required"}]}
    
    url = f"https://api.probe42.in/probe_data_api/entities/{identifier}/base-details"
    headers = {"x-api-key": api_key}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return {"status": "success", "content": [{"text": str(result)}]}
    except Exception as e:
        return {"status": "error", "content": [{"text": f"Error: {str(e)}"}]}


@tool
async def get_kyc_details(identifier: str) -> dict:
    """Fast-track corporate KYC with comprehensive regulatory data.
    
    Args:
        identifier: CIN, LLPIN, PAN or GSTIN of the entity
    
    Returns:
        Comprehensive KYC data including directors, financials, industry segments, and Probe Score
    """
    api_key = os.getenv("PROBE_API_KEY")
    if not api_key:
        return {"status": "error", "content": [{"text": "PROBE_API_KEY environment variable is required"}]}
    
    url = f"https://api.probe42.in/probe_data_api/entities/{identifier}/kyc-details"
    headers = {"x-api-key": api_key}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return {"status": "success", "content": [{"text": str(result)}]}
    except Exception as e:
        return {"status": "error", "content": [{"text": f"Error: {str(e)}"}]}