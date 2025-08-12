import json
from typing import Any
from mcp.types import TextContent
from ..client import ProbeClient

class BaseTools(ProbeClient):
    def register_tools(self, mcp: Any):
        """Register base details tools."""

        @mcp.tool(description="Get essential data points about a corporate entity for verification")
        async def get_base_details(identifier: str) -> list[TextContent]:
            """
            Get essential data points about a corporate entity, allowing verification of its legitimacy and active status.
            
            Args:
                identifier: CIN, LLPIN, PAN or GSTIN of the entity
            
            Returns:
                Essential details including legal name, status, and registered address
            """
            self.logger.info(f"Getting base details for identifier: {identifier}")
            try:
                response = await self.get_base_details(identifier)
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                self.logger.error(f"Error getting base details: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]