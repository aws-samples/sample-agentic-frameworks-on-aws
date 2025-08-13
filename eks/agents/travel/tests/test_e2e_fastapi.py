#!/usr/bin/env python3
"""
Test script for the AI Agent FastAPI Server

This script tests the FastAPI endpoints to ensure they work correctly.
"""

import asyncio
import aiohttp
import json
import time

async def wait_for_server(base_url: str, timeout: int = 30):
    """Wait for the server to be ready"""
    print(f"Waiting for FastAPI server at {base_url} to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/health") as response:
                    if response.status == 200:
                        print("✅ FastAPI server is ready!")
                        return True
        except:
            pass
        await asyncio.sleep(1)

    print("❌ FastAPI server not ready after 30 seconds")
    print("FastAPI server is not responding. Please start the FastAPI server first:")
    print("uv run fastapi")
    return False

async def test_fastapi_endpoints(base_url: str = "http://localhost:3000"):
    """Test the AI Agent FastAPI endpoints"""

    if not await wait_for_server(base_url):
        return

    print(f"Testing AI Agent FastAPI at {base_url}")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:

        # Test 1: Health Check
        print("1. Testing health check endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print("✅ Health check passed")
                    print(f"   Status: {health_data.get('status')}")
                else:
                    print(f"❌ Health check failed with status {response.status}")
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")

        print()

        # Test 2: Root Endpoint
        print("2. Testing root endpoint...")
        try:
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    root_data = await response.json()
                    print("✅ Root endpoint successful")
                    print(f"   Message: {root_data.get('message')}")
                    print(f"   Available endpoints: {list(root_data.get('endpoints', {}).keys())}")
                else:
                    print(f"❌ Root endpoint failed with status {response.status}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {str(e)}")

        print()

        # Test 3: Prompt Endpoint - Travel Query
        print("3. Testing prompt endpoint with travel query...")
        try:
            prompt_data = {"text": "Plan me a trip to Seattle next week."}
            async with session.post(
                f"{base_url}/prompt",
                json=prompt_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    print("✅ Prompt endpoint successful")
                    print(f"   Input: {prompt_data['text']}")
                    response_text = response_data.get('text', '')
                    print(f"   Response: {response_text[:100]}...")
                else:
                    print(f"❌ Prompt endpoint failed with status {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Prompt endpoint failed: {str(e)}")

        print()

        # Test 5: Error Handling - Empty Text
        print("5. Testing error handling with empty text...")
        try:
            prompt_data = {"text": ""}
            async with session.post(
                f"{base_url}/prompt",
                json=prompt_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 400:
                    print("✅ Empty text error handling works correctly")
                    error_data = await response.json()
                    print(f"   Error message: {error_data.get('detail')}")
                else:
                    print(f"❌ Expected 400 status, got {response.status}")
        except Exception as e:
            print(f"❌ Error handling test failed: {str(e)}")

        print()

        # Test 6: Invalid Endpoint
        print("6. Testing invalid endpoint (404)...")
        try:
            async with session.get(f"{base_url}/invalid") as response:
                if response.status == 404:
                    print("✅ 404 handling works correctly")
                    print(f"   Status: {response.status}")
                else:
                    print(f"❌ Expected 404 status, got {response.status}")
        except Exception as e:
            print(f"❌ 404 test failed: {str(e)}")

    print()
    print("=" * 60)
    print("FastAPI testing completed!")

def main():
    """Main entry point"""
    asyncio.run(test_fastapi_endpoints())

if __name__ == "__main__":
    main()
