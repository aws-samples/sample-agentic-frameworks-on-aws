import asyncio
from typing import Dict, List, Optional
from agents.intent_parser_agent import IntentParserAgent
from agents.network_agent import NetworkSecurityAgent
from agents.threat_agent import ThreatDetectionAgent
from agents.compliance_agent import ComplianceAgent
from agents.incident_agent import IncidentResponseAgent
from agents.forensics_agent import ForensicsAgent
from agents.explainability_agent import ExplainabilityAgent

class IntelligentOrchestrator:
    def __init__(self):
        self.intent_parser = IntentParserAgent()
        
        # Individual agents for selective execution
        self.agents = {
            "network": NetworkSecurityAgent(),
            "threat": ThreatDetectionAgent(),
            "compliance": ComplianceAgent(),
            "incident": IncidentResponseAgent(),
            "forensics": ForensicsAgent(),
            "explainability": ExplainabilityAgent()
        }
    
    async def process_user_query(self, user_input: str) -> Dict:
        """Process user query with intent-based routing"""
        # Parse intent first
        intent_result = await self.intent_parser.parse_intent(user_input)
        
        # Route based on intent
        if intent_result["required_agents"] == ["all"]:
            # Use simplified multi-agent workflow for complex analysis
            return await self._execute_full_analysis(intent_result)
        else:
            # Use selective agent execution
            return await self._execute_selective_agents(intent_result)
    
    async def _execute_full_analysis(self, intent_result: Dict) -> Dict:
        """Execute full multi-agent analysis without LangGraph"""
        structured_event = intent_result.get("structured_event", {})
        
        # Only set defaults for truly missing fields, don't override extracted data
        if "source_ip" not in structured_event or not structured_event["source_ip"]:
            structured_event["source_ip"] = "unknown"
        if "destination_ip" not in structured_event or not structured_event["destination_ip"]:
            structured_event["destination_ip"] = "unknown"
        if "protocol" not in structured_event or not structured_event["protocol"]:
            structured_event["protocol"] = "unknown"
        
        results = {
            "intent_analysis": intent_result,
            "network_analysis": {},
            "threat_analysis": {},
            "compliance_impact": {},
            "incident_details": {},
            "forensics_status": {},
            "explainability_report": {},
            "overall_risk_score": 0,
            "recommendations": []
        }
        
        try:
            # Execute all agents sequentially
            results["network_analysis"] = await self.agents["network"].assess_network_impact(structured_event)
            results["threat_analysis"] = await self.agents["threat"].analyze_threat(structured_event)
            results["compliance_impact"] = await self.agents["compliance"].check_compliance_impact(structured_event)
            results["incident_details"] = await self.agents["incident"].create_incident(structured_event)
            results["forensics_status"] = await self.agents["forensics"].collect_evidence(structured_event)
            
            # Calculate overall risk score
            network_risk = results["network_analysis"].get("risk_score", 0)
            threat_severity = results["threat_analysis"].get("severity_score", 0)
            results["overall_risk_score"] = max(network_risk, threat_severity)
            
            # Generate recommendations
            if results["overall_risk_score"] >= 8:
                results["recommendations"] = ["Immediate isolation required", "Activate incident response team"]
            elif results["overall_risk_score"] >= 6:
                results["recommendations"] = ["Enhanced monitoring", "Prepare incident response"]
            else:
                results["recommendations"] = ["Continue monitoring", "Review security controls"]
            
            # Generate explainability report
            results["explainability_report"] = await self.agents["explainability"].explain_decisions(results)
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    async def _execute_selective_agents(self, intent_result: Dict) -> Dict:
        """Execute only selected agents based on intent"""
        results = {
            "intent_analysis": intent_result,
            "agent_results": {},
            "overall_assessment": {}
        }
        
        required_agents = intent_result["required_agents"]
        structured_event = intent_result.get("structured_event", {})
        
        # Only set defaults for truly missing fields, don't override extracted data
        if "source_ip" not in structured_event or not structured_event["source_ip"]:
            structured_event["source_ip"] = "unknown"
        if "destination_ip" not in structured_event or not structured_event["destination_ip"]:
            structured_event["destination_ip"] = "unknown"
        if "protocol" not in structured_event or not structured_event["protocol"]:
            structured_event["protocol"] = "unknown"
        
        # Execute selected agents
        for agent_name in required_agents:
            if agent_name in self.agents:
                try:
                    agent = self.agents[agent_name]
                    
                    if agent_name == "network":
                        result = await agent.assess_network_impact(structured_event)
                    elif agent_name == "threat":
                        result = await agent.analyze_threat(structured_event)
                    elif agent_name == "compliance":
                        result = await agent.check_compliance_impact(structured_event)
                    elif agent_name == "incident":
                        result = await agent.create_incident(structured_event)
                    elif agent_name == "forensics":
                        result = await agent.collect_evidence(structured_event)
                    elif agent_name == "explainability":
                        # For explainability, use the full results
                        result = await agent.explain_decisions(results)
                    else:
                        result = {"error": f"Unknown agent: {agent_name}"}
                    
                    results["agent_results"][agent_name] = result
                    
                except Exception as e:
                    results["agent_results"][agent_name] = {"error": str(e)}
        
        # Generate overall assessment
        results["overall_assessment"] = self._generate_assessment(results)
        
        return results
    
    def _generate_assessment(self, results: Dict) -> Dict:
        """Generate overall assessment from selective agent results"""
        assessment = {
            "intent_confidence": results["intent_analysis"]["confidence"],
            "agents_executed": list(results["agent_results"].keys()),
            "execution_status": "completed",
            "recommendations": []
        }
        
        # Extract key insights from agent results
        for agent_name, result in results["agent_results"].items():
            if "error" not in result:
                if agent_name == "network" and "risk_score" in result:
                    assessment["network_risk"] = result["risk_score"]
                elif agent_name == "threat" and "severity_score" in result:
                    assessment["threat_severity"] = result["severity_score"]
                elif agent_name == "compliance" and "compliance_risk" in result:
                    assessment["compliance_risk"] = result["compliance_risk"]
        
        # Generate recommendations based on results
        if "network" in results["agent_results"]:
            network_result = results["agent_results"]["network"]
            if network_result.get("recommended_isolation"):
                assessment["recommendations"].append("Network isolation recommended")
        
        if "threat" in results["agent_results"]:
            threat_result = results["agent_results"]["threat"]
            if threat_result.get("severity_score", 0) >= 7:
                assessment["recommendations"].append("High severity threat detected")
        
        return assessment