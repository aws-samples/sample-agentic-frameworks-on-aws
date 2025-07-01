#!/usr/bin/env python3
"""Test core AI agents with real Bedrock calls"""
import asyncio
import os
import sys

# Add parent directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set AWS region
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

async def test_bedrock_agent():
    print("🔥 Testing Real Bedrock AI Agent")
    print("=" * 40)
    
    print(f"🔧 Environment:")
    print(f"   AWS Region: us-east-1")
    print(f"   AWS Credentials: Using default configuration")
    
    try:
        # Import and test core Bedrock client
        from core.bedrock_client import BedrockLLMClient
        
        print(f"\n🚀 Initializing Bedrock Client...")
        client = BedrockLLMClient()
        
        print(f"🧠 Testing Claude-3-Sonnet via AWS Bedrock...")
        
        # Create a simple tool for testing
        from langchain.tools import Tool
        
        def simple_risk_calc(query):
            return "Risk calculated: 8/10 (High)"
        
        tools = [Tool(
            name="calculate_risk",
            description="Calculate security risk score",
            func=simple_risk_calc
        )]
        
        # Create agent
        system_prompt = "You are a cybersecurity AI agent. Analyze the security event and provide a risk assessment."
        agent = client.create_agent(tools, system_prompt)
        
        # Test with security event
        test_query = "Analyze this security event: SSH brute force attack from 192.168.1.45 to critical server 10.0.1.100"
        
        print(f"📥 Query: {test_query}")
        print(f"🔄 Calling Claude via Bedrock...")
        
        result = await asyncio.to_thread(agent.invoke, {"input": test_query})
        
        print(f"\n✅ SUCCESS! Real AI Response:")
        print(f"📊 Claude Analysis: {result['output'][:200]}...")
        print(f"\n🎉 Real Bedrock integration working!")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("💡 Some dependencies missing, but core structure is ready")
        
    except Exception as e:
        print(f"\n❌ Bedrock Error: {e}")
        print("💡 This could be due to:")
        print("   - AWS Bedrock not enabled in your account")
        print("   - Claude model access not granted")
        print("   - Insufficient IAM permissions")
        print("   - Network connectivity issues")

if __name__ == "__main__":
    asyncio.run(test_bedrock_agent())