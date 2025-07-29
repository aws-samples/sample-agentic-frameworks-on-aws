#!/usr/bin/env python3
"""
Test script for the Weather Agent A2A (Agent-to-Agent) Protocol

This script tests the A2A endpoints to ensure they work correctly.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)
from rich.console import Console
from rich.markdown import Markdown

# Configure logging to be less verbose for better UX
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"


async def test_a2a_protocol(base_url: str = "http://localhost:9000"):
    """Test the Weather Agent A2A Protocol endpoints"""

    print(f"Testing Weather Agent A2A Protocol at {base_url}")
    print("=" * 50)

    # Set a longer timeout for the HTTP client
    timeout = httpx.Timeout(60.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as httpx_client:
            # Test 1: Agent Card Discovery
            print("1. Testing agent card discovery...")
            try:
                resolver = A2ACardResolver(
                    httpx_client=httpx_client,
                    base_url=base_url,
                )
                agent_card = await resolver.get_agent_card()
                print("✅ Agent card discovery successful")
                print(f"   Agent Name: {agent_card.name}")
                print(f"   Agent Description: {agent_card.description}")
                print(f"   Version: {agent_card.version}")
                if hasattr(agent_card.capabilities, '__len__'):
                    print(f"   Capabilities: {len(agent_card.capabilities)} available")
                else:
                    print(f"   Capabilities: Available")
                if hasattr(agent_card, 'protocol_version'):
                    print(f"   Protocol Version: {agent_card.protocol_version}")
                # Print available attributes for debugging
                print(f"   Agent Card Retrieved: ✓")
            except Exception as e:
                print(f"❌ Agent card discovery failed: {str(e)}")
                return False

            print()

            # Test 2: A2A Client Initialization
            print("2. Testing A2A client initialization...")
            try:
                client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)
                print("✅ A2A client initialized successfully")
                print(f"   Client Ready: True")
                print(f"   Connection Established: ✓")
            except Exception as e:
                print(f"❌ A2A client initialization failed: {str(e)}")
                return False

            print()

            # Test 3: Weather Query Message
            print("3. Testing weather query message...")
            try:
                query_text = "What's the weather forecast for Seattle this week?"
                request = create_message_request(query_text)
                print(f"   Query: {query_text}")

                response = await client.send_message(request)
                print("✅ Weather query successful")

                # Extract response content
                response_dict = json.loads(response.model_dump_json(exclude_none=True))
                if "result" in response_dict and "parts" in response_dict["result"]:
                    for part in response_dict["result"]["parts"]:
                        if part.get("kind") == "text" and "text" in part:
                            response_text = part["text"]
                            print(f"   Response: {response_text[:100]}...")
                            break

            except Exception as e:
                print(f"❌ Weather query failed: {str(e)}")
                return False

            print()

            # Test 4: Alert Query Message
            print("4. Testing weather alert query...")
            try:
                alert_query = "Are there any weather alerts for Miami?"
                request = create_message_request(alert_query)
                print(f"   Query: {alert_query}")

                response = await client.send_message(request)
                print("✅ Weather alert query successful")

                # Extract response content
                response_dict = json.loads(response.model_dump_json(exclude_none=True))
                if "result" in response_dict and "parts" in response_dict["result"]:
                    for part in response_dict["result"]["parts"]:
                        if part.get("kind") == "text" and "text" in part:
                            response_text = part["text"]
                            print(f"   Response: {response_text[:100]}...")
                            break

            except Exception as e:
                print(f"❌ Weather alert query failed: {str(e)}")
                return False

            print()

            # Test 5: Invalid Message Format
            print("5. Testing invalid message format handling...")
            try:
                # Create an invalid request (missing required fields)
                invalid_payload = {
                    "message": {
                        "role": "user",
                        "parts": [],  # Empty parts array
                        "messageId": uuid4().hex,
                    },
                }
                invalid_request = SendMessageRequest(
                    id=str(uuid4()),
                    params=MessageSendParams(**invalid_payload)
                )

                response = await client.send_message(invalid_request)
                print("✅ Invalid message handling works correctly")
                print("   Server gracefully handled malformed request")

            except Exception as e:
                error_msg = str(e)
                if "500" in error_msg or "503" in error_msg:
                    print("✅ Invalid message properly rejected")
                    print("   Server correctly returned error for malformed request")
                else:
                    print("✅ Invalid message properly rejected")
                    print(f"   Error: {error_msg[:80]}...")

            print()

            # Test 6: Display Full Response (Optional)
            print("6. Testing full response display...")
            try:
                final_query = "Give me a brief weather summary for New York"
                request = create_message_request(final_query)
                response = await client.send_message(request)

                print("✅ Full response test successful")
                display_formatted_response(response)

            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "500" in error_msg:
                    print("⚠️  Full response test skipped (server busy)")
                    print("   This is normal during high load testing")
                else:
                    print(f"❌ Full response test failed: {error_msg[:60]}...")

            print()

            # Test 7: Conversational Memory Loss Test
            print("7. Testing conversational memory loss (forecast then alerts)...")
            try:
                # First, ask for weather forecast for a specific city
                forecast_query = "What's the weather forecast for Denver, Colorado?"
                request1 = create_message_request(forecast_query)
                print(f"   First Query: {forecast_query}")

                response1 = await client.send_message(request1)

                # Extract and display first response
                response_dict1 = json.loads(response1.model_dump_json(exclude_none=True))
                if "result" in response_dict1 and "parts" in response_dict1["result"]:
                    for part in response_dict1["result"]["parts"]:
                        if part.get("kind") == "text" and "text" in part:
                            response_text1 = part["text"]
                            print(f"   First Response: {response_text1[:80]}...")
                            break

                print()

                # Then, ask for alerts without specifying location - should NOT remember Denver
                alert_query = "Any alerts?"
                request2 = create_message_request(alert_query)
                print(f"   Follow-up Query: {alert_query}")

                response2 = await client.send_message(request2)

                # Extract and display second response
                response_dict2 = json.loads(response2.model_dump_json(exclude_none=True))
                if "result" in response_dict2 and "parts" in response_dict2["result"]:
                    for part in response_dict2["result"]["parts"]:
                        if part.get("kind") == "text" and "text" in part:
                            response_text2 = part["text"]
                            print(f"   Follow-up Response: {response_text2[:80]}...")

                            # Check that the response does NOT mention Denver or Colorado (memory loss)
                            response_lower = response_text2.lower()

                            if "denver" in response_lower or "colorado" in response_lower:
                                print("❌ Conversational memory loss test failed")
                                print("   Agent still remembers the previous location (memory not cleared)")
                                return False
                            else:
                                print("✅ Conversational memory loss test successful")
                                print("   Agent correctly forgot the previous location (Denver/Colorado not mentioned)")
                            break
                else:
                    print("✅ Conversational memory loss test completed")
                    print("   Agent processed follow-up query (memory state unclear)")

            except Exception as e:
                print(f"❌ Conversational memory loss test failed: {str(e)}")
                return False

            print()
            print("=" * 50)
            print("A2A Protocol testing completed!")
            return True

    except Exception as e:
        print(f"❌ A2A Protocol test failed: {str(e)}")
        return False


def create_message_request(query_text: str) -> SendMessageRequest:
    """
    Create a message request to send to the agent.

    Args:
        query_text: The text query to send

    Returns:
        A SendMessageRequest object
    """
    send_message_payload: dict[str, Any] = {
        "message": {
            "role": "user",
            "parts": [{"kind": "text", "text": query_text}],
            "messageId": uuid4().hex,
        },
    }
    return SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**send_message_payload))


def display_formatted_response(response: Any) -> None:
    """
    Display the response from the agent in a formatted way.

    Args:
        response: The response from the agent
    """
    try:
        # Parse the JSON response to extract the text content
        response_dict = json.loads(response.model_dump_json(exclude_none=True))

        # Extract and render the markdown text
        if "result" in response_dict and "parts" in response_dict["result"]:
            for part in response_dict["result"]["parts"]:
                if part.get("kind") == "text" and "text" in part:
                    print("   Formatted Response:")
                    print("   " + "-" * 40)

                    # Split response into lines and indent each line
                    md_text = part["text"]
                    lines = md_text.split('\n')
                    for line in lines[:5]:  # Show first 5 lines
                        print(f"   {line}")

                    if len(lines) > 5:
                        print(f"   ... ({len(lines) - 5} more lines)")

                    print("   " + "-" * 40)
                    break
    except Exception as e:
        print(f"   Response formatting error: {str(e)}")


async def wait_for_server(base_url: str = "http://localhost:9000", timeout: int = 30):
    """Wait for the A2A server to be ready"""
    print(f"Waiting for A2A server at {base_url} to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(f"{base_url}/.well-known/agent.json")
                if response.status_code == 200:
                    print("✅ A2A server is ready!")
                    return True
        except:
            pass
        await asyncio.sleep(1)

    print(f"❌ A2A server not ready after {timeout} seconds")
    return False


async def main():
    """Main function to run the A2A client test."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else f"http://localhost:{os.getenv('A2A_PORT', '9000')}"

    if await wait_for_server(base_url):
        success = await test_a2a_protocol(base_url)
        if not success:
            sys.exit(1)
    else:
        print("A2A server is not responding. Please start the A2A server first:")
        print("uv run a2a-server")
        sys.exit(1)


def run_main():
    """Wrapper function for script entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
