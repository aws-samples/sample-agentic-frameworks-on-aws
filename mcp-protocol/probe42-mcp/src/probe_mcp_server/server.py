#!/usr/bin/env python3
import logging
from fastmcp import FastMCP
from .tools.search import SearchTools
from .tools.base import BaseTools
from .tools.kyc import KYCTools


class ProbeMCPServer:
    def __init__(self):
        self.name = "probe_mcp_server"
        self.mcp = FastMCP(self.name)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        # Initialize tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        search_tools = SearchTools(self.logger)
        base_tools = BaseTools(self.logger)
        kyc_tools = KYCTools(self.logger)
        
        search_tools.register_tools(self.mcp)
        base_tools.register_tools(self.mcp)
        kyc_tools.register_tools(self.mcp)

    def run(self):
        """Run the MCP server."""
        self.mcp.run()


def main():
    server = ProbeMCPServer()
    server.run()