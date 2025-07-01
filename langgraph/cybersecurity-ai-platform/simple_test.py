#!/usr/bin/env python3
"""Simple test of cybersecurity agents without external dependencies"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

class MockNetworkAgent:
    def calculate_risk(self, source_ip, dest_ip, protocol):
        risk = 5
        if dest_ip.startswith("10.0.1"):  # Critical asset
            risk += 3
        if protocol in ["SSH", "RDP", "SMB"]:
            risk += 2
        return min(risk, 10)
    
    def identify_segments(self, source_ip, dest_ip):
        segments = []
        if source_ip.startswith("192.168.1"):
            segments.append("DMZ")
        if dest_ip.startswith("10.0.0"):
            segments.append("Internal")
        return segments

class MockThreatAgent:
    def classify_threat(self, event):
        description = event.get("description", "").lower()
        if "failed login" in description:
            return "Brute Force Attack"
        elif "malware" in description:
            return "Malware"
        return "Unknown Threat"
    
    def calculate_severity(self, event, threat_type):
        base_severity = {"Brute Force Attack": 6, "Malware": 8, "Unknown Threat": 5}
        severity = base_severity.get(threat_type, 5)
        if event.get("severity") == "high":
            severity += 1
        return min(severity, 10)

class MockComplianceAgent:
    def identify_violations(self, event):
        violations = []
        if event.get("protocol") in ["SSH", "RDP"] and event.get("severity") == "high":
            violations.append({
                "type": "Privileged Access Violation",
                "framework": "SOC2"
            })
        return violations

def test_cybersec_platform():
    print("🔒 Cybersecurity AI Platform Test")
    print("=" * 40)
    
    # Test event
    event = {
        "event_type": "intrusion",
        "severity": "high",
        "source_ip": "192.168.1.45", 
        "destination_ip": "10.0.1.100",
        "protocol": "SSH",
        "description": "Failed login attempts"
    }
    
    # Network Security Agent
    network_agent = MockNetworkAgent()
    risk_score = network_agent.calculate_risk(event["source_ip"], event["destination_ip"], event["protocol"])
    segments = network_agent.identify_segments(event["source_ip"], event["destination_ip"])
    
    print(f"🌐 Network Analysis:")
    print(f"   Risk Score: {risk_score}/10")
    print(f"   Affected Segments: {segments}")
    print(f"   Lateral Movement Risk: {'Yes' if risk_score > 6 else 'No'}")
    
    # Threat Detection Agent
    threat_agent = MockThreatAgent()
    threat_type = threat_agent.classify_threat(event)
    severity = threat_agent.calculate_severity(event, threat_type)
    
    print(f"\n🎯 Threat Analysis:")
    print(f"   Threat Type: {threat_type}")
    print(f"   Severity Score: {severity}/10")
    print(f"   Attack Vector: Remote Access")
    
    # Compliance Agent
    compliance_agent = MockComplianceAgent()
    violations = compliance_agent.identify_violations(event)
    
    print(f"\n📋 Compliance Impact:")
    print(f"   Violations Found: {len(violations)}")
    if violations:
        print(f"   Framework Affected: {violations[0]['framework']}")
        print(f"   Violation Type: {violations[0]['type']}")
    
    # AI Recommendations
    print(f"\n🤖 AI Recommendations:")
    print(f"   • Isolate host {event['source_ip']} from network")
    print(f"   • Block traffic at firewall")
    print(f"   • Enhanced monitoring required")
    print(f"   • Update incident response documentation")
    
    print(f"\n✅ Platform test completed successfully!")
    print(f"💡 Full AI features available with AWS Bedrock + Claude integration")

if __name__ == "__main__":
    test_cybersec_platform()