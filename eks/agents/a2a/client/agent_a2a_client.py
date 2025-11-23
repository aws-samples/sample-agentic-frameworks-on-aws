#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.13"
# dependencies = ["a2a-sdk==0.3.16"]
# ///
"""Simple CLI to send messages to an A2A agent server."""

import argparse
import asyncio
import sys
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart, Task

async def send_message(base_url: str, message: str):
    async with httpx.AsyncClient(timeout=300) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        config = ClientConfig(httpx_client=httpx_client,streaming=True)
        factory = ClientFactory(config)
        client = factory.create(agent_card)
        msg = Message(kind="message", role=Role.user, parts=[Part(TextPart(kind="text", text=message))], message_id=uuid4().hex)
        last_artifact_id = None
        async for event in client.send_message(msg):
            if isinstance(event, tuple) and len(event) == 2:
                tast: Task
                task, update_event = event
                if task.artifacts and task.artifacts[0].name == "agent_response" and task.artifacts[0].parts:
                    #print(f"Task: {task.model_dump_json(exclude_none=True, indent=2)}")
                    # only print if the artifact has changed
                    if last_artifact_id != task.artifacts[0].artifact_id:
                        print(task.artifacts[0].parts[0].root.text, end="", flush=True)
                    last_artifact_id = task.artifacts[0].artifact_id
        print()

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
        asyncio.run(send_message(base_url=args.agent_url, message=args.message))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
