#!/usr/bin/env python3
"""Test multiple security scenarios with real AI agents"""
import asyncio
import os
import sys

# Add parent directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set AWS region
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

try:
    from core.langgraph_orchestrator import LangGraphOrchestrator
    REAL_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Cannot import real agents: {e}")
    REAL_AGENTS_AVAILABLE = False

async def test_scenario(orchestrator, scenario_name, event):
    print(f"\n🔥 Testing Scenario: {scenario_name}")
    print("=" * 60)
    
    print(f"📥 Event Details:")
    print(f"   Type: {event['event_type']}")
    print(f"   Severity: {event['severity']}")
    print(f"   Source: {event['source_ip']} → {event['destination_ip']}")
    print(f"   Protocol: {event['protocol']}")
    print(f"   Description: {event['description']}")
    
    try:
        print(f"\n🔄 Processing through 6 AI agents...")
        result = await orchestrator.process_security_event(event)
        
        print(f"\n✅ Analysis Complete!")
        print(f"📊 Results:")
        print(f"   Overall Risk Score: {result.get('overall_risk_score', 'N/A')}/10")
        print(f"   🌐 Network Risk: {result.get('network_analysis', {}).get('risk_score', 'N/A')}/10")
        print(f"   🎯 Threat Type: {result.get('threat_analysis', {}).get('threat_type', 'N/A')}")
        print(f"   🎯 Threat Severity: {result.get('threat_analysis', {}).get('severity_score', 'N/A')}/10")
        print(f"   📋 Compliance Risk: {result.get('compliance_analysis', {}).get('compliance_risk', 'N/A')}")
        print(f"   🚨 Incident ID: {result.get('incident_details', {}).get('id', 'N/A')}")
        print(f"   🔍 Evidence ID: {result.get('forensics_status', {}).get('id', 'N/A')}")
        print(f"   🧠 Explanation ID: {result.get('explainability_report', {}).get('id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def test_multiple_scenarios():
    print("🚀 Testing Multiple Cybersecurity Scenarios")
    print("=" * 60)
    
    if not REAL_AGENTS_AVAILABLE:
        print("❌ Real agents not available")
        return
    
    orchestrator = LangGraphOrchestrator()
    
    # Scenario 1: SSH Brute Force (Internal)
    scenario1 = {
        "event_type": "intrusion",
        "severity": "critical",
        "source_ip": "192.168.1.45",
        "destination_ip": "10.0.1.100",
        "protocol": "SSH",
        "description": "Multiple failed login attempts to critical server"
    }
    
    # Scenario 2: Web Application Attack (External)
    scenario2 = {
        "event_type": "web_attack",
        "severity": "high",
        "source_ip": "203.0.113.15",
        "destination_ip": "10.0.2.50",
        "protocol": "HTTPS",
        "description": "SQL injection attempts detected on web application"
    }
    
    # Scenario 3: Malware Detection (Medium)
    scenario3 = {
        "event_type": "malware",
        "severity": "medium",
        "source_ip": "10.0.3.25",
        "destination_ip": "8.8.8.8",
        "protocol": "HTTP",
        "description": "Trojan malware communication to external C&C server"
    }
    
    # Scenario 4: Data Exfiltration (Critical)
    scenario4 = {
        "event_type": "data_breach",
        "severity": "critical",
        "source_ip": "10.0.1.75",
        "destination_ip": "185.199.108.153",
        "protocol": "HTTPS",
        "description": "Large data transfer to external cloud storage detected"
    }
    
    scenarios = [
        ("SSH Brute Force Attack", scenario1),
        ("Web Application Attack", scenario2),
        ("Malware Communication", scenario3),
        ("Data Exfiltration", scenario4)
    ]
    
    results = []
    for name, event in scenarios:
        success = await test_scenario(orchestrator, name, event)
        results.append((name, success))
    
    print(f"\n📈 Summary of All Scenarios:")
    print("=" * 60)
    for name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\n🎯 Overall Results: {successful}/{len(results)} scenarios completed successfully")

if __name__ == "__main__":
    asyncio.run(test_multiple_scenarios())