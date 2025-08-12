import os
import httpx
from typing import Dict, Any

class ProbeClient:
    def __init__(self, logger):
        self.logger = logger
        self.api_key = os.getenv("PROBE_API_KEY")
        if not self.api_key:
            raise ValueError("PROBE_API_KEY environment variable is required")
        
        self.base_url = "https://api.probe42.in/probe_data_api"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def search_entities(self, name_starts_with: str, limit: int = 10) -> Dict[str, Any]:
        """Search entities by name prefix."""
        url = f"{self.base_url}/search-entities"
        data = {
            "nameStartsWith": name_starts_with,
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_base_details(self, identifier: str) -> Dict[str, Any]:
        """Get base details for an entity by identifier."""
        url = f"{self.base_url}/entities/{identifier}/base-details"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_kyc_details(self, identifier: str) -> Dict[str, Any]:
        """Get KYC details for an entity by identifier."""
        url = f"{self.base_url}/entities/{identifier}/kyc-details"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()