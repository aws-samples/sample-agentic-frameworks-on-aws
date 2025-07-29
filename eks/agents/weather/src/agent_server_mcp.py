"""MCP server implementation for the AI Agent."""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') == '1' else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)

import argparse
from mcp.server.fastmcp import FastMCP
from .agent import create_agent, load_agent_config

# Load agent configuration
agent_name, agent_description, system_prompt = load_agent_config()
logger.info(f"Loaded agent configuration: {agent_name}")

# Initialize FastMCP server with dynamic name
mcp = FastMCP(agent_name)

@mcp.tool(name=agent_name, description=agent_description)
async def query_agent(query: str) -> str:
    # Get agent configuration for server naming
    logger.debug(f"Processing MCP query: {query}")
    agent_instance = create_agent()
    result = str(agent_instance(query))
    logger.debug(f"MCP query result length: {len(result)} characters")
    return result


def mcp_agent():
    """Main entry point for the AI agent MCP server."""
    logger.info("Starting MCP Agent Server")

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Agent MCP Server')
    parser.add_argument(
        '--transport',
        choices=['stdio', 'streamable-http'],
        default='streamable-http',
        help='Transport protocol to use streamable-http(default) or stdio'
    )

    args = parser.parse_args()
    logger.info(f"Using transport: {args.transport}")

    # Run MCP server with specified transport
    mcp.settings.port = int(os.getenv("MCP_PORT", "8080"))
    mcp.settings.host = '0.0.0.0'
    logger.info(f"Starting MCP server on {mcp.settings.host}:{mcp.settings.port}")

    try:
        mcp.run(transport=args.transport)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    mcp_agent()
