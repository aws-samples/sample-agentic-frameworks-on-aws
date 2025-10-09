#!/usr/bin/env python3
"""Simple CLI to send messages to an A2A agent server."""

import asyncio
import sys
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.client.client_task_manager import ClientTaskManager
from a2a.types import Message, Part, Role, TextPart, Task
from a2a.utils.message import get_message_text


def extract_text(obj: Task | Message) -> str:
    """Extract plain text from a Task or Message."""
    if isinstance(obj, Message):
        return get_message_text(obj)

    if isinstance(obj, Task) and obj.artifacts:
        for artifact in reversed(obj.artifacts):
            if artifact.parts:
                for part in reversed(artifact.parts):
                    if hasattr(part, 'root') and hasattr(part.root, 'text'):
                        return part.root.text  # type: ignore[attr-defined]
    return ''


async def send_message(agent_url: str, message_text: str) -> str:
    """Send a message to an A2A agent and return the response."""
    httpx_client = httpx.AsyncClient(timeout=300)

    # Get agent card and create client
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=agent_url)
    agent_card = await resolver.get_agent_card()

    config = ClientConfig(httpx_client=httpx_client, streaming=False)
    factory = ClientFactory(config)
    client = factory.create(agent_card)

    # Create and send message
    msg = Message(
        kind="message",
        role=Role.user,
        parts=[Part(TextPart(kind="text", text=message_text))],
        message_id=uuid4().hex,
    )

    task_manager = ClientTaskManager()
    last_message: Message | None = None

    async for event in client.send_message(msg):
        if isinstance(event, tuple):
            event = event[0]
        await task_manager.process(event)
        if isinstance(event, Message):
            last_message = event

    # Extract response
    task = task_manager.get_task()
    if task:
        return extract_text(task)
    elif last_message is not None:
        return extract_text(last_message)
    else:
        raise RuntimeError('No response from agent')


def main():
    """CLI entry point."""
    if len(sys.argv) != 3:
        print("Usage: uv run agent_a2a_cli.py <agent_url> <message>")
        print('Example: uv run agent_a2a_cli.py http://localhost:9000 "What\'s the weather in San Francisco"')
        sys.exit(1)

    agent_url = sys.argv[1]
    message = sys.argv[2]

    try:
        response = asyncio.run(send_message(agent_url, message))
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
