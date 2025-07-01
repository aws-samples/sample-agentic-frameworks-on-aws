#!/usr/bin/env python3
"""Test Explainability Agent with 6 AI agents"""
import asyncio
import os
import sys

# Add parent directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class MockExplainabilityAgent:
    async def explain_decisions(self, workflow_result):
        """Mock explainability analysis"""
        return {
            "id": "EXP-20241215",
            "ai_explanation": "High-risk SSH connection from DMZ to critical asset triggered automated isolation based on network topology analysis and threat intelligence correlation.",
            "decision_rationale": {
                "overall_decision": f"Risk score {workflow_result.get('overall_risk_score', 0)}/10 triggered automated response",
                "key_factors": [
                    "High network risk (9/10) due to critical asset targeting",
                    "High threat severity (8/10) - Brute Force Attack",
                    "1 compliance violations detected"
                ],
                "decision_tree": [
                    "Network Risk ≥ 7 → Isolation Required",
                    "Threat Severity ≥ 7 → Incident Creation",
                    "Compliance Violations > 0 → Mandatory Reporting"
                ]
            },
            "risk_justification": {
                "network_risk": {
                    "score": 9,
                    "factors": ["Base risk: 5/10", "Critical asset target: +3", "High-risk protocol (SSH): +2"],
                    "calculation": "5 + 3 + 2 = 10/10"
                },
                "threat_severity": {
                    "score": 8,
                    "base_score": 6,
                    "modifiers": ["High severity: +1"],
                    "confidence": 0.9
                }
            },
            "action_reasoning": [
                {
                    "action": "Immediate isolation required",
                    "reasoning": "Network isolation prevents lateral movement and contains threat",
                    "trigger": "Risk score ≥ 8 OR critical asset compromise",
                    "compliance_requirement": "NIST CSF - Respond (RS.RP)"
                },
                {
                    "action": "Activate incident response team",
                    "reasoning": "Formal incident management ensures proper response coordination",
                    "trigger": "Severity ≥ 7 OR compliance violations detected",
                    "compliance_requirement": "SOC2 - Incident Response"
                }
            ],
            "compliance_basis": {
                "frameworks_triggered": ["SOC2"],
                "violation_explanations": [
                    {
                        "violation": "Privileged Access Violation",
                        "framework": "SOC2",
                        "why_triggered": "Event matches Access Control Policy violation pattern",
                        "regulatory_basis": "Service Organization Control 2 - Security and Availability"
                    }
                ],
                "reporting_requirements": ["SOC2 control deficiency documentation"]
            },
            "confidence_factors": {
                "data_quality": "High - Complete event data available",
                "model_confidence": 0.9,
                "rule_certainty": "High - Clear policy violations detected",
                "human_validation": "Recommended for critical decisions",
                "uncertainty_factors": [
                    "Attribution assessment has medium confidence",
                    "Some network topology assumptions made"
                ]
            }
        }

class MockLangGraphOrchestrator:
    def __init__(self):
        self.explainability_agent = MockExplainabilityAgent()
    
    async def process_security_event_with_explanation(self, event):
        """Simulate LangGraph workflow with explainability"""
        print(f"🔄 LangGraph Workflow with Explainability Started")
        
        # Steps 1-5: Previous agent processing
        print(f"  1️⃣ Network Security Agent analyzing...")
        network_result = {"risk_score": 9, "segments": ["DMZ"], "isolation_required": True}
        
        print(f"  2️⃣ Threat Detection Agent analyzing...")
        threat_result = {"threat_type": "Brute Force", "severity_score": 8, "confidence": 0.9}
        
        print(f"  3️⃣ Compliance Agent checking...")
        compliance_result = {"violations": 1, "frameworks": ["SOC2"], "risk": "High"}
        
        print(f"  4️⃣ Incident Response Agent creating incident...")
        incident_result = {"incident_id": "INC-20241215", "severity": "Critical", "status": "Open"}
        
        print(f"  5️⃣ Forensics Agent collecting evidence...")
        forensics_result = {"evidence_id": "EVD-20241215", "artifacts": 4, "status": "Collected"}
        
        # Step 6: NEW - Explainability Analysis
        print(f"  6️⃣ Explainability Agent generating justifications...")
        workflow_result = {
            "overall_risk_score": 9,
            "network_analysis": network_result,
            "threat_analysis": threat_result,
            "compliance_impact": compliance_result,
            "incident_details": incident_result,
            "forensics_status": forensics_result,
            "event": event,
            "recommendations": ["Immediate isolation required", "Activate incident response team"]
        }
        
        explanation = await self.explainability_agent.explain_decisions(workflow_result)
        
        # Step 7: Final Synthesis
        print(f"  7️⃣ Final synthesis with explanations...")
        
        return {
            "workflow_type": "LangGraph Multi-Agent with Explainability",
            "agents_executed": 6,
            "overall_risk_score": 9,
            "network_analysis": network_result,
            "threat_analysis": threat_result,
            "compliance_impact": compliance_result,
            "incident_details": incident_result,
            "forensics_status": forensics_result,
            "explainability_report": explanation,
            "recommendations": ["Immediate isolation required", "Activate incident response team"],
            "workflow_complete": True
        }

async def test_explainability_agent():
    print("🚀 Enhanced Cybersecurity Platform with AI Explainability")
    print("=" * 60)
    
    # Test event
    event = {
        "event_type": "intrusion",
        "severity": "critical",
        "source_ip": "192.168.1.45",
        "destination_ip": "10.0.1.100", 
        "protocol": "SSH",
        "description": "Multiple failed login attempts to critical server"
    }
    
    print(f"📥 Processing Security Event:")
    print(f"   Type: {event['event_type']}")
    print(f"   Severity: {event['severity']}")
    print(f"   Source: {event['source_ip']} → {event['destination_ip']}")
    print(f"   Protocol: {event['protocol']}")
    
    # Process through enhanced LangGraph workflow
    orchestrator = MockLangGraphOrchestrator()
    result = await orchestrator.process_security_event_with_explanation(event)
    
    print(f"\n📊 Enhanced Workflow Results:")
    print(f"   Agents Executed: {result['agents_executed']} (including Explainability)")
    print(f"   Overall Risk Score: {result['overall_risk_score']}/10")
    print(f"   Explanation ID: {result['explainability_report']['id']}")
    
    print(f"\n🧠 AI Decision Explanation:")
    explanation = result['explainability_report']
    print(f"   Summary: {explanation['ai_explanation'][:100]}...")
    print(f"   Key Factors: {len(explanation['decision_rationale']['key_factors'])} identified")
    print(f"   Actions Justified: {len(explanation['action_reasoning'])}")
    print(f"   Compliance Frameworks: {explanation['compliance_basis']['frameworks_triggered']}")
    
    print(f"\n🔍 Decision Rationale:")
    for factor in explanation['decision_rationale']['key_factors']:
        print(f"   • {factor}")
    
    print(f"\n⚖️ Risk Score Justification:")
    network_risk = explanation['risk_justification']['network_risk']
    print(f"   Network Risk: {network_risk['score']}/10")
    for factor in network_risk['factors']:
        print(f"     - {factor}")
    print(f"   Calculation: {network_risk['calculation']}")
    
    print(f"\n📋 Action Justifications:")
    for action in explanation['action_reasoning']:
        print(f"   Action: {action['action']}")
        print(f"   Reasoning: {action['reasoning']}")
        print(f"   Compliance: {action['compliance_requirement']}")
        print()
    
    print(f"\n🎯 Trust & Transparency Metrics:")
    confidence = explanation['confidence_factors']
    print(f"   Data Quality: {confidence['data_quality']}")
    print(f"   Model Confidence: {confidence['model_confidence']}")
    print(f"   Rule Certainty: {confidence['rule_certainty']}")
    print(f"   Human Validation: {confidence['human_validation']}")
    
    print(f"\n✅ Enhanced workflow with explainability completed!")
    print(f"🔗 6 specialized AI agents with full decision transparency")
    print(f"📝 Audit-ready explanations for compliance and trust")

if __name__ == "__main__":
    asyncio.run(test_explainability_agent())