#!/usr/bin/env python3
"""Simple CLI to send messages to an A2A agent server."""

import argparse
import asyncio
import json
import sys
from uuid import uuid4
import httpx
import yaml
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


async def send_message(agent_url: str, message_text: str, show_card: bool = False) -> tuple[str, dict | None]:
    """Send a message to an A2A agent and return the response.

    Returns:
        Tuple of (response_text, agent_card_dict if show_card else None)
    """
    httpx_client = httpx.AsyncClient(timeout=300)

    # Get agent card and create client
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=agent_url)
    agent_card = await resolver.get_agent_card()

    card_dict = None
    if show_card:
        card_dict = agent_card.model_dump()

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
        return extract_text(task), card_dict
    elif last_message is not None:
        return extract_text(last_message), card_dict
    else:
        raise RuntimeError('No response from agent')


def remove_null_fields(obj):
    """Recursively remove null fields from dictionaries and lists."""
    if isinstance(obj, dict):
        return {k: remove_null_fields(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_null_fields(item) for item in obj]
    return obj


def format_card_output(card_dict: dict) -> str:
    """Format agent card as YAML for better readability."""
    cleaned_dict = remove_null_fields(card_dict)

    # Custom representer for multi-line strings to use literal block style
    def str_representer(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_representer)

    return yaml.dump(cleaned_dict, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Send messages to an A2A agent server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: uv run agent_a2a_cli.py http://localhost:9000 "What\'s the weather in San Francisco" --show-card'
    )
    parser.add_argument("agent_url", help="URL of the A2A agent server")
    parser.add_argument("message", help="Message to send to the agent")
    parser.add_argument(
        "--show-card",
        action="store_true",
        help="Display AgentCard information before the response"
    )

    args = parser.parse_args()

    try:
        response, card_dict = asyncio.run(send_message(args.agent_url, args.message, args.show_card))

        if card_dict:
            print("=" * 60)
            print("AGENT CARD INFORMATION")
            print("=" * 60)
            print(format_card_output(card_dict))
            print("=" * 60)
            print()

        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
