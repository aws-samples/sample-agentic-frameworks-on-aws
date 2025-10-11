#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.13"
# dependencies = ["a2a-sdk>=0.3.8"]
# ///
"""Simple CLI to send messages to an A2A agent server."""

import argparse
import asyncio
import sys
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient, ClientConfig, ClientFactory
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    TaskStatusUpdateEvent,
    TextPart,
)

async def send_message_to_an_agent(agent_base_url: str, message_text: str) -> str:
    """Send a message to a specific agent and yield the streaming response.

    Args:
        agent_base_url (str): The agent base_url like http://locahost:9000
        message_text (str): The message to send.

    Yields:
        str: The streaming response from the agent.
    """
    async with httpx.AsyncClient(timeout=300) as httpx_client:
        # Get agent card and create client
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=agent_base_url)
        agent_card = await resolver.get_agent_card()

        client = A2AClient(httpx_client, agent_card=agent_card)
        # TODO: A2AClient is deprecated need to change to use ClientFactory
        # config = ClientConfig(httpx_client=httpx_client)
        # factory = ClientFactory(config)
        # client = factory.create(agent_card)
        message = Message(
            kind="message",
            role=Role.user,
            parts=[Part(TextPart(kind="text", text=message_text))],
            message_id=uuid4().hex,
        )

        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4().hex), params=MessageSendParams(message=message)
        )
        async for chunk in client.send_message_streaming(streaming_request):
            if isinstance(
                chunk.root, SendStreamingMessageSuccessResponse
            ) and isinstance(chunk.root.result, TaskStatusUpdateEvent):
                message = chunk.root.result.status.message
                if message:
                    yield message.parts[0].root.text



async def run_streaming_message(agent_url: str, message_text: str) -> str:
    """Wrapper to consume the async generator and return collected response."""
    response_parts = []
    async for text_chunk in send_message_to_an_agent(agent_url, message_text):
        response_parts.append(text_chunk)
        print(text_chunk, end='', flush=True)  # Print streaming chunks as they arrive
    print()  # New line after streaming completes
    return ''.join(response_parts)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Send messages to an A2A agent server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: uv run agent_a2a_cli.py http://localhost:9000 "What\'s the weather in San Francisco"'
    )
    parser.add_argument("agent_url", help="URL of the A2A agent server")
    parser.add_argument("message", help="Message to send to the agent")

    args = parser.parse_args()

    try:
        response = asyncio.run(run_streaming_message(args.agent_url, args.message))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
