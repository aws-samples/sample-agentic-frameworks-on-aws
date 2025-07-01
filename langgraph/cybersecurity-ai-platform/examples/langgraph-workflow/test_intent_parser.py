#!/usr/bin/env python3
"""Test intent parser with natural language queries"""
import asyncio
import os
import sys

# Add parent directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set AWS region
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

try:
    from core.intelligent_orchestrator import IntelligentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Cannot import orchestrator: {e}")
    ORCHESTRATOR_AVAILABLE = False

async def test_intent_query(orchestrator, query_name, user_input):
    print(f"\n🔥 Testing Query: {query_name}")
    print("=" * 60)
    print(f"📥 User Input: {user_input}")
    
    try:
        print(f"\n🔄 Processing with intent parser...")
        result = await orchestrator.process_user_query(user_input)
        
        print(f"\n✅ Analysis Complete!")
        
        # Display intent analysis
        if "intent_analysis" in result:
            intent = result["intent_analysis"]
            print(f"📊 Intent Analysis:")
            print(f"   Intent Type: {intent.get('intent_type', 'N/A')}")
            print(f"   Required Agents: {intent.get('required_agents', 'N/A')}")
            print(f"   Confidence: {intent.get('confidence', 'N/A')}")
        
        # Display agent results for selective execution
        if "agent_results" in result:
            print(f"🤖 Agent Results:")
            for agent_name, agent_result in result["agent_results"].items():
                if "error" not in agent_result:
                    print(f"   {agent_name.title()}: ✅ Success")
                else:
                    print(f"   {agent_name.title()}: ❌ {agent_result['error']}")
        
        # Display full workflow results
        if "overall_risk_score" in result:
            print(f"📊 Full Analysis Results:")
            print(f"   Overall Risk Score: {result.get('overall_risk_score', 'N/A')}/10")
            print(f"   🌐 Network Risk: {result.get('network_analysis', {}).get('risk_score', 'N/A')}/10")
            print(f"   🎯 Threat Severity: {result.get('threat_analysis', {}).get('severity_score', 'N/A')}/10")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def test_intent_parsing():
    print("🚀 Testing Intent Parser with Natural Language Queries")
    print("=" * 60)
    
    if not ORCHESTRATOR_AVAILABLE:
        print("❌ Orchestrator not available")
        return
    
    orchestrator = IntelligentOrchestrator()
    
    # Test queries for different intents
    test_queries = [
        ("Network Analysis", "Check network security for IP 192.168.1.45 accessing server 10.0.1.100"),
        ("Threat Analysis", "Analyze this malware threat: trojan communicating with C&C server 8.8.8.8"),
        ("Compliance Check", "What are the compliance implications of this data breach?"),
        ("Incident Response", "Create incident for critical SSH brute force attack"),
        ("Forensic Investigation", "Collect evidence for SQL injection attack on web server"),
        ("Explanation Request", "Explain why the risk score is so high for this event"),
        ("Full Security Analysis", "Analyze this critical security event: multiple failed SSH logins from 192.168.1.45 to 10.0.1.100")
    ]
    
    results = []
    for name, query in test_queries:
        success = await test_intent_query(orchestrator, name, query)
        results.append((name, success))
    
    print(f"\n📈 Summary of Intent Parsing Tests:")
    print("=" * 60)
    for name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\n🎯 Overall Results: {successful}/{len(results)} queries processed successfully")

if __name__ == "__main__":
    asyncio.run(test_intent_parsing())