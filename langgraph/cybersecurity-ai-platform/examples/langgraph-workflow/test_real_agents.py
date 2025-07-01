#!/usr/bin/env python3
"""Test real AI agents with actual LLM calls"""
import asyncio
import os
import sys

# Add parent directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set AWS region
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Check if we can import the real agents
try:
    from core.langgraph_orchestrator import LangGraphOrchestrator
    REAL_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Cannot import real agents: {e}")
    REAL_AGENTS_AVAILABLE = False

async def test_real_cybersec_platform():
    print("🔥 Testing REAL Cybersecurity AI Platform")
    print("=" * 50)
    
    print(f"🔧 Environment Check:")
    print(f"   AWS Region: us-east-1")
    print(f"   AWS Credentials: Using default configuration")
    print(f"   Real Agents: {'✅ Available' if REAL_AGENTS_AVAILABLE else '❌ Import Failed'}")
    
    if not REAL_AGENTS_AVAILABLE:
        print("\n❌ Cannot run real agents - missing dependencies")
        print("💡 Install with: pip install -r requirements.txt")
        return
    
    # Test event
    event = {
        "event_type": "intrusion",
        "severity": "critical",
        "source_ip": "192.168.1.45",
        "destination_ip": "10.0.1.100",
        "protocol": "SSH",
        "description": "Multiple failed login attempts to critical server"
    }
    
    print(f"\n📥 Processing Real Security Event:")
    print(f"   Type: {event['event_type']}")
    print(f"   Severity: {event['severity']}")
    print(f"   Source: {event['source_ip']} → {event['destination_ip']}")
    
    try:
        print(f"\n🚀 Initializing LangGraph Orchestrator with 6 AI Agents...")
        orchestrator = LangGraphOrchestrator()
        
        print(f"🔄 Processing through real AI agents...")
        result = await orchestrator.process_security_event(event)
        
        print(f"\n✅ REAL AI Analysis Complete!")
        print(f"📊 Results:")
        print(f"   Overall Risk Score: {result.get('overall_risk_score', 'N/A')}/10")
        print(f"   Workflow Complete: {result.get('workflow_complete', False)}")
        
        # Show agent results
        if 'network_analysis' in result:
            print(f"   🌐 Network Risk: {result['network_analysis'].get('risk_score', 'N/A')}/10")
        
        if 'threat_analysis' in result:
            print(f"   🎯 Threat Severity: {result['threat_analysis'].get('severity_score', 'N/A')}/10")
        
        if 'explainability_report' in result:
            exp_id = result['explainability_report'].get('id', 'N/A')
            print(f"   🧠 Explanation ID: {exp_id}")
        
        print(f"\n🎉 Successfully executed 6 real AI agents with AWS Bedrock!")
        
    except Exception as e:
        print(f"\n❌ Error running real agents: {e}")
        print(f"💡 This might be due to:")
        print(f"   - Missing AWS Bedrock access")
        print(f"   - Invalid credentials")
        print(f"   - Network connectivity issues")
        print(f"   - Missing Python dependencies")

if __name__ == "__main__":
    asyncio.run(test_real_cybersec_platform())