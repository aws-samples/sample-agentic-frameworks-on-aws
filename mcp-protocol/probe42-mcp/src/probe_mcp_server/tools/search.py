import json
from typing import Any
from mcp.types import TextContent
from ..client import ProbeClient

class SearchTools(ProbeClient):
    def register_tools(self, mcp: Any):
        """Register search-related tools."""

        @mcp.tool(description="Search within the database of all Indian corporates by name")
        async def search_entities(name_starts_with: str, limit: int = 10) -> list[TextContent]:
            """
            Search within the database of all Indian corporates by name.
            
            Args:
                name_starts_with: The prefix of the company/LLP name to search for
                limit: Maximum number of results to return (default: 10)
            
            Returns:
                List of matching entities with legal name and identifier
            """
            self.logger.info(f"Searching entities with prefix: {name_starts_with}")
            try:
                response = await self.search_entities(name_starts_with, limit)
                
                # Format the response
                formatted_response = {
                    "companies": response.get("data", {}).get("companies", []),
                    "llps": response.get("data", {}).get("llps", [])
                }
                
                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]
            except Exception as e:
                self.logger.error(f"Error searching entities: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]