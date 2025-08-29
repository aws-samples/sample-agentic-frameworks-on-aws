"""A2A server implementation for the AI Agent."""

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

from strands import Agent
from strands.multiagent.a2a import A2AServer
from strands.types.content import Message, Messages
from strands.types.exceptions import ContextWindowOverflowException
from strands.agent.conversation_manager import ConversationManager, SlidingWindowConversationManager
from .agent import create_agent


class MemoryLostConversationManager(SlidingWindowConversationManager):
    """
    A conversation manager that resets the agent's message history to empty array.

    This class extends SlidingWindowConversationManager to inherit the reduce_context method
    but overrides apply_management to completely clear the agent's message history instead
    of using a sliding window approach.
    """

    def apply_management(self, agent: "Agent") -> None:
        """
        Override the apply_management method to reset agent messages to empty array.

        Args:
            _agent: The agent whose message history should be reset
        """
        # Reset the agent's messages to an empty array
        logger.debug("Resetting agent messages to empty array")
        logger.debug(f"Messages before reset: {len(agent.messages)} messages")
        agent.messages = []
        logger.debug("Agent messages reset completed")


def a2a_agent():
    """Start the A2A server for the AI Agent."""
    logger.info("Starting A2A Agent Server")

    try:
        strands_agent = create_agent(conversation_manager=MemoryLostConversationManager())
        logger.info("Agent instance created successfully")

        port = os.getenv("A2A_PORT", "9000")
        hosting_http_url = os.getenv("A2A_URL", "0.0.0.0")


        strands_a2a_agent = A2AServer(
            agent=strands_agent,
            port=int(port),
            http_url=hosting_http_url
        )
        logger.info("A2A Server wrapper created successfully")

        logger.info(f"Starting A2A server on port {port}")

        strands_a2a_agent.serve()
    except Exception as e:
        logger.error(f"Failed to start A2A server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    a2a_agent()
