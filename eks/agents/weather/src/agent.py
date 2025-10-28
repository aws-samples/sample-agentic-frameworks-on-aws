"""Agent module for providing AI assistant functionality."""

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

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.agent.conversation_manager import ConversationManager
from strands.session.session_manager import SessionManager
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands.tools.mcp.mcp_agent_tool import MCPAgentTool
from strands.types.content import Messages
from . import agent_tools

# Default MCP configuration when mcp.json is not found
DEFAULT_MCP_CONFIG = """{
  "mcpServers": {
    "weather-mcp-stdio": {
      "command": "uvx",
      "args": [
        "--from",
        ".",
        "--directory",
        "mcp-servers/weather-mcp-server",
        "mcp-server",
        "--transport",
        "stdio"
      ]
    }
  }
}"""


def load_agent_config(config_file: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Load agent configuration from agent.md file.

    Args:
        config_file: Optional path to config file. If None, uses AGENT_CONFIG_FILE env var or default agent.md

    Returns:
        Tuple[str, str, str]: (name, description, system_prompt)

    Raises:
        FileNotFoundError: If no configuration file is found
        ValueError: If configuration file is missing required sections
    """
    # Get agent config file path from parameter, environment variable, or use default
    if config_file is None:
        # Try multiple locations for the config file
        current_dir = os.path.dirname(__file__)

        # Location 1: Check if AGENT_CONFIG_FILE is set
        if os.getenv("AGENT_CONFIG_FILE"):
            config_file = os.getenv("AGENT_CONFIG_FILE")
        else:
            # Location 2: Try project root (development mode - src/ is in project)
            project_root = os.path.dirname(current_dir)
            dev_config = os.path.join(project_root, "agent.md")

            # Location 3: Try /app/ directory (container mode - installed package)
            container_config = "/app/agent.md"

            # Location 4: Try current working directory
            cwd_config = os.path.join(os.getcwd(), "agent.md")

            if os.path.exists(dev_config):
                config_file = dev_config
            elif os.path.exists(container_config):
                config_file = container_config
            elif os.path.exists(cwd_config):
                config_file = cwd_config
            else:
                # Default to project root for error message
                config_file = dev_config

    if config_file is None or not os.path.exists(config_file):
        logger.warning(f"Agent config file not found at {config_file}")
        # Try fallback to cloudbot.md in multiple locations
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(current_dir)

        fallback_locations = [
            os.path.join(project_root, "cloudbot.md"),  # Development mode
            "/app/cloudbot.md",                         # Container mode
            os.path.join(os.getcwd(), "cloudbot.md")    # Current working directory
        ]

        fallback_config = None
        for location in fallback_locations:
            if os.path.exists(location):
                fallback_config = location
                break

        if fallback_config:
            logger.info(f"Using fallback configuration: {fallback_config}")
            config_file = fallback_config
        else:
            raise FileNotFoundError(f"No agent configuration file found. Please provide either {config_file} or set AGENT_CONFIG_FILE environment variable.")

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the markdown content
        name = _extract_section(content, "Agent Name")
        description = _extract_section(content, "Agent Description")
        system_prompt = _extract_section(content, "System Prompt")

        if not name or not description or not system_prompt:
            raise ValueError(f"Agent configuration file {config_file} is missing required sections: Agent Name, Agent Description, or System Prompt")

        return name.strip(), description.strip(), system_prompt.strip()

    except Exception as e:
        logger.error(f"Error reading agent config file {config_file}: {str(e)}")
        raise


def _extract_section(content: str, section_name: str) -> Optional[str]:
    """
    Extract a section from markdown content.

    Args:
        content: The markdown content
        section_name: The section header to look for

    Returns:
        Optional[str]: The section content or None if not found
    """
    # Pattern to match ## Section Name followed by content until next ## or end
    pattern = rf"##\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


# Load agent configuration
agent_name, agent_description, system_prompt = load_agent_config()


# Cache for MCP tools to avoid reloading on every create_agent() call
_mcp_tools_cache = None




def create_agent(messages: Optional[Messages]=None,
                 conversation_manager: Optional[ConversationManager] = None,
                 session_manager: Optional[SessionManager] = None
    ) -> Agent:
    """
    Create and return an Agent instance with dynamically loaded MCP tools.

    Returns:
        Agent: A configured AI assistant agent with tools from enabled MCP servers
    """
    model_id = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
    bedrock_model = BedrockModel(model_id=model_id)

    try:
        # Load and combine tools from all enabled MCP servers (cached)
        mcp_tools = _get_cached_mcp_tools()

        # Create the agent with configuration from agent.md
        agent = Agent(
            name=agent_name,
            agent_id= 'weather_agent',
            description=agent_description,
            model=bedrock_model,
            session_manager=session_manager,
            system_prompt=system_prompt,
            tools=[agent_tools]+mcp_tools,
            messages=messages,
            conversation_manager=conversation_manager
        )

        return agent

    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        # Return a fallback agent when MCP client fails
        fallback_agent = Agent(
            model=bedrock_model,
            system_prompt="""I am an AI Assistant, but I'm currently experiencing technical difficulties accessing my tools.
I apologize for the inconvenience. Please try again later or contact support if the issue persists.""",
            tools=[],
        )
        return fallback_agent


def _get_cached_mcp_tools() -> List[Any]:
    """Get MCP tools from cache or load them if not cached."""
    global _mcp_tools_cache
    if _mcp_tools_cache is None:
        _mcp_tools_cache = _load_mcp_tools_from_config()
    return _mcp_tools_cache


def _load_mcp_tools_from_config() -> List[Any]:
    """
    Load MCP tools from all enabled servers defined in mcp.json.

    Returns:
        List[Any]: Combined list of tools from all enabled MCP servers
    """
    # Try multiple locations for the MCP config file
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(current_dir)

    config_locations = [
        os.path.join(project_root, "mcp.json"),     # Development mode
        "/app/mcp.json",                            # Container mode
        os.path.join(os.getcwd(), "mcp.json")       # Current working directory
    ]

    config_path = None
    for location in config_locations:
        if os.path.exists(location):
            config_path = location
            break

    # Default to first location for error message if none found
    if config_path is None:
        config_path = config_locations[0]

    if not os.path.exists(config_path):
        logger.warning(f"MCP configuration file not found at {config_path}, using default configuration")
        try:
            config = json.loads(DEFAULT_MCP_CONFIG)
        except Exception as e:
            logger.error(f"Error parsing default MCP configuration: {str(e)}")
            return []
    else:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error reading MCP configuration: {str(e)}")
            return []

    mcp_servers = config.get("mcpServers", {})
    all_tools: List[MCPAgentTool] = []

    for server_name, server_config in mcp_servers.items():
        if server_config.get("disabled", False):
            logger.info(f"Skipping disabled MCP server: {server_name}")
            continue

        try:
            logger.info(f"Loading tools from MCP server: {server_name}")
            mcp_client = _create_mcp_client_from_config(server_name, server_config)
            mcp_client.start()
            tools = mcp_client.list_tools_sync()
            all_tools.extend(tools)
            logger.info(f"Loaded {len(tools)} tools from {server_name}")
        except Exception as e:
            logger.error(f"Error loading tools from MCP server {server_name}: {str(e)}")
            continue

    logger.info(f"Total tools loaded: {len(all_tools)}")
    # Log the tools at debug level
    for tool in all_tools:
        logger.info(f"Tool: {tool.tool_name} - {tool.tool_spec['description']}")
    return all_tools


def _create_mcp_client_from_config(server_name: str, server_config: Dict[str, Any]) -> MCPClient:
    """
    Create an MCP client based on server configuration.

    Args:
        server_name: Name of the MCP server
        server_config: Configuration dictionary for the server

    Returns:
        MCPClient: Configured MCP client

    Raises:
        ValueError: If server configuration is invalid
    """
    # Check if it's a URL-based server (streamable-http)
    if "url" in server_config:
        url = server_config["url"]
        logger.debug(f"Creating streamable-http MCP client for {server_name} at {url}")
        return MCPClient(
            lambda: streamablehttp_client(url)
        )

    # Check if it's a command-based server (stdio)
    elif "command" in server_config and "args" in server_config:
        command = server_config["command"]
        args = server_config["args"]
        env = server_config.get("env", {})

        if env:
            logger.debug(f"Creating stdio MCP client for {server_name} with command: {command} {' '.join(args)} and env vars: {list(env.keys())}")
        else:
            logger.debug(f"Creating stdio MCP client for {server_name} with command: {command} {' '.join(args)}")

        return MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command=command,
                    args=args,
                    env=env if env else None
                )
            )
        )

    else:
        raise ValueError(f"Invalid MCP server configuration for {server_name}: must have either 'url' or both 'command' and 'args'")



if __name__ == "__main__":
    # Test the agent functionality
    agent = create_agent()
    response = agent("Hello, how can you help me?")
    logger.info(f"Test response: {response}")
