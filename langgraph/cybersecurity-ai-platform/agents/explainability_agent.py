import asyncio
from typing import Dict, List, Any
from datetime import datetime
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient

class ExplainabilityAgent:
    def __init__(self):
        self.decision_logs = []
        self.audit_trail = {}
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
        
    async def explain_decisions(self, workflow_result: Dict) -> Dict:
        """Generate explanations for AI decisions using Claude"""
        query = f"Explain the reasoning behind these security decisions: {workflow_result}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        explanation_id = f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        explanation = {
            "id": explanation_id,
            "timestamp": datetime.now().isoformat(),
            "ai_explanation": ai_result["output"],
            "decision_rationale": self._generate_rationale(workflow_result),
            "risk_justification": self._justify_risk_scores(workflow_result),
            "action_reasoning": self._explain_actions(workflow_result)
        }
        
        self.decision_logs.append(explanation)
        return explanation
    
    def _generate_rationale(self, result: Any) -> Dict:
        """Generate human-readable rationale for decisions"""
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            return {
                "overall_decision": "Unable to generate rationale - invalid input format",
                "key_factors": [],
                "decision_tree": []
            }
        
        rationale = {
            "overall_decision": f"Risk score {result.get('overall_risk_score', 0)}/10 triggered automated response",
            "key_factors": [],
            "decision_tree": []
        }
        
        # Network analysis rationale
        network = result.get("network_analysis", {})
        if isinstance(network, dict) and network.get("risk_score", 0) >= 7:
            rationale["key_factors"].append(f"High network risk ({network.get('risk_score')}/10) due to critical asset targeting")
            rationale["decision_tree"].append("Network Risk ≥ 7 → Isolation Required")
        
        # Threat analysis rationale
        threat = result.get("threat_analysis", {})
        if isinstance(threat, dict) and threat.get("severity_score", 0) >= 7:
            rationale["key_factors"].append(f"High threat severity ({threat.get('severity_score')}/10) - {threat.get('threat_type')}")
            rationale["decision_tree"].append("Threat Severity ≥ 7 → Incident Creation")
        
        # Compliance rationale
        compliance = result.get("compliance_impact", {})
        if isinstance(compliance, dict) and compliance.get("violations"):
            violations = compliance.get("violations", [])
            if isinstance(violations, list) and violations:
                rationale["key_factors"].append(f"{len(violations)} compliance violations detected")
                rationale["decision_tree"].append("Compliance Violations > 0 → Mandatory Reporting")
        
        return rationale
    
    def _justify_risk_scores(self, result: Any) -> Dict:
        """Justify risk score calculations"""
        if not isinstance(result, dict):
            return {}
        
        justification = {}
        
        network = result.get("network_analysis", {})
        if isinstance(network, dict) and "risk_score" in network:
            justification["network_risk"] = {
                "score": network["risk_score"],
                "factors": [
                    "Base risk: 5/10",
                    f"Critical asset target: +3" if network.get("recommended_isolation") else "Standard asset: +0",
                    "High-risk protocol (SSH/RDP): +2" if network.get("lateral_movement_risk") else "Standard protocol: +0"
                ],
                "calculation": "5 + 3 + 2 = 10/10"
            }
        
        threat = result.get("threat_analysis", {})
        if isinstance(threat, dict) and "severity_score" in threat:
            justification["threat_severity"] = {
                "score": threat["severity_score"],
                "base_score": threat.get("severity_score", 5),
                "modifiers": [],
                "confidence": threat.get("confidence", 0)
            }
        
        return justification
    
    def _explain_actions(self, result: Any) -> List[Dict]:
        """Explain why specific actions were recommended"""
        if not isinstance(result, dict):
            return []
        
        explanations = []
        recommendations = result.get("recommendations", [])
        
        if not isinstance(recommendations, list):
            return []
        
        for action in recommendations:
            if isinstance(action, str):
                if "isolation" in action.lower():
                    explanations.append({
                        "action": action,
                        "reasoning": "Network isolation prevents lateral movement and contains threat",
                        "trigger": "Risk score ≥ 8 OR critical asset compromise",
                        "compliance_requirement": "NIST CSF - Respond (RS.RP)"
                    })
                elif "incident" in action.lower():
                    explanations.append({
                        "action": action,
                        "reasoning": "Formal incident management ensures proper response coordination",
                        "trigger": "Severity ≥ 7 OR compliance violations detected",
                        "compliance_requirement": "SOC2 - Incident Response"
                    })
        
        return explanations
    
    def _create_agent(self):
        """Create LangChain agent with explainability tools"""
        tools = [
            Tool(
                name="generate_rationale",
                description="Generate human-readable rationale for security decisions",
                func=lambda result: str(self._generate_rationale(result))
            ),
            Tool(
                name="justify_risk_scores",
                description="Justify risk score calculations with detailed breakdown",
                func=lambda result: str(self._justify_risk_scores(result))
            ),
            Tool(
                name="explain_actions",
                description="Explain why specific security actions were recommended",
                func=lambda result: str(self._explain_actions(result))
            )
        ]
        
        system_prompt = """You are an AI Explainability agent for cybersecurity decisions. Your role is to:
        - Provide clear, transparent explanations for all AI-driven security decisions
        - Justify risk assessments and action recommendations
        - Ensure compliance with regulatory transparency requirements
        - Build trust through detailed decision rationale
        
        Always provide your final answer in a clear, structured format without using additional Action/Observation cycles after your analysis is complete."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)