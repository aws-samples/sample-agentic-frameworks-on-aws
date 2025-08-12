import json
from typing import Any
from mcp.types import TextContent
from ..client import ProbeClient

class KYCTools(ProbeClient):
    def register_tools(self, mcp: Any):
        """Register KYC tools."""

        @mcp.tool(description="Fast-track corporate KYC with comprehensive regulatory data")
        async def get_kyc_details(identifier: str) -> list[TextContent]:
            """
            Fast-track corporate KYC with regulatory data covering vitals, industry segments, directors, and key financial indicators.
            
            Args:
                identifier: CIN, LLPIN, PAN or GSTIN of the entity
            
            Returns:
                Comprehensive KYC data including directors, financials, industry segments, and Probe Score
            """
            self.logger.info(f"Getting KYC details for identifier: {identifier}")
            try:
                response = await self.get_kyc_details(identifier)
                return [TextContent(type="text", text=json.dumps(response, indent=2))]
            except Exception as e:
                self.logger.error(f"Error getting KYC details: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]