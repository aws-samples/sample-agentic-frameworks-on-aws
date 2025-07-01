from typing import Dict, List, TypedDict
from langgraph.graph import StateGraph, END
from agents.network_agent import NetworkSecurityAgent
from agents.threat_agent import ThreatDetectionAgent
from agents.compliance_agent import ComplianceAgent
from agents.incident_agent import IncidentResponseAgent
from agents.forensics_agent import ForensicsAgent
from agents.explainability_agent import ExplainabilityAgent

class SecurityState(TypedDict):
    event: Dict
    network_analysis: Dict
    threat_analysis: Dict
    compliance_analysis: Dict
    incident_created: Dict
    forensics_evidence: Dict
    explainability_report: Dict
    final_response: Dict
    next_action: str

class LangGraphOrchestrator:
    def __init__(self):
        self.network_agent = NetworkSecurityAgent()
        self.threat_agent = ThreatDetectionAgent()
        self.compliance_agent = ComplianceAgent()
        self.incident_agent = IncidentResponseAgent()
        self.forensics_agent = ForensicsAgent()
        self.explainability_agent = ExplainabilityAgent()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for multi-agent coordination"""
        workflow = StateGraph(SecurityState)
        
        # Add nodes for each agent
        workflow.add_node("network_analysis", self._network_analysis_node)
        workflow.add_node("threat_analysis", self._threat_analysis_node)
        workflow.add_node("compliance_check", self._compliance_check_node)
        workflow.add_node("incident_response", self._incident_response_node)
        workflow.add_node("forensics_collection", self._forensics_collection_node)
        workflow.add_node("explainability_analysis", self._explainability_analysis_node)
        workflow.add_node("final_synthesis", self._final_synthesis_node)
        
        # Define workflow edges
        workflow.set_entry_point("network_analysis")
        workflow.add_edge("network_analysis", "threat_analysis")
        workflow.add_edge("threat_analysis", "compliance_check")
        workflow.add_conditional_edges(
            "compliance_check",
            self._should_create_incident,
            {
                "create_incident": "incident_response",
                "skip_incident": "final_synthesis"
            }
        )
        workflow.add_edge("incident_response", "forensics_collection")
        workflow.add_edge("forensics_collection", "explainability_analysis")
        workflow.add_conditional_edges(
            "compliance_check",
            lambda state: "explainability_analysis" if not self._should_create_incident(state) == "create_incident" else "incident_response"
        )
        workflow.add_edge("explainability_analysis", "final_synthesis")
        workflow.add_edge("final_synthesis", END)
        
        return workflow.compile()
    
    async def process_security_event(self, event: Dict) -> Dict:
        """Process security event through LangGraph workflow"""
        initial_state = SecurityState(
            event=event,
            network_analysis={},
            threat_analysis={},
            compliance_analysis={},
            incident_created={},
            forensics_evidence={},
            explainability_report={},
            final_response={},
            next_action=""
        )
        
        result = await self.workflow.ainvoke(initial_state)
        return result["final_response"]
    
    async def _network_analysis_node(self, state: SecurityState) -> SecurityState:
        """Network analysis node"""
        analysis = await self.network_agent.assess_network_impact(state["event"])
        state["network_analysis"] = analysis
        return state
    
    async def _threat_analysis_node(self, state: SecurityState) -> SecurityState:
        """Threat analysis node"""
        analysis = await self.threat_agent.analyze_threat(state["event"])
        state["threat_analysis"] = analysis
        return state
    
    async def _compliance_check_node(self, state: SecurityState) -> SecurityState:
        """Compliance check node"""
        analysis = await self.compliance_agent.check_compliance_impact(state["event"])
        state["compliance_analysis"] = analysis
        return state
    
    async def _incident_response_node(self, state: SecurityState) -> SecurityState:
        """Incident response node"""
        incident = await self.incident_agent.create_incident(state["event"])
        state["incident_created"] = incident
        return state
    
    async def _forensics_collection_node(self, state: SecurityState) -> SecurityState:
        """Forensics collection node"""
        evidence = await self.forensics_agent.collect_evidence(state["event"])
        state["forensics_evidence"] = evidence
        return state
    
    async def _explainability_analysis_node(self, state: SecurityState) -> SecurityState:
        """Explainability analysis node"""
        # Create workflow result for explanation
        workflow_result = {
            "overall_risk_score": max(
                state["network_analysis"].get("risk_score", 0),
                state["threat_analysis"].get("severity_score", 0)
            ),
            "network_analysis": state["network_analysis"],
            "threat_analysis": state["threat_analysis"],
            "compliance_impact": state["compliance_analysis"],
            "incident_details": state.get("incident_created", {}),
            "forensics_status": state.get("forensics_evidence", {}),
            "event": state["event"],
            "recommendations": ["Immediate isolation required", "Activate incident response team"]
        }
        
        explanation = await self.explainability_agent.explain_decisions(workflow_result)
        state["explainability_report"] = explanation
        return state
    
    async def _final_synthesis_node(self, state: SecurityState) -> SecurityState:
        """Final synthesis node"""
        # Calculate overall risk score
        network_risk = state["network_analysis"].get("risk_score", 0)
        threat_severity = state["threat_analysis"].get("severity_score", 0)
        overall_risk = max(network_risk, threat_severity)
        
        # Generate recommendations
        recommendations = []
        if overall_risk >= 8:
            recommendations.extend([
                "Immediate isolation required",
                "Activate incident response team",
                "Begin forensic investigation"
            ])
        elif overall_risk >= 6:
            recommendations.extend([
                "Enhanced monitoring",
                "Containment procedures",
                "Document all actions"
            ])
        
        state["final_response"] = {
            "overall_risk_score": overall_risk,
            "network_analysis": state["network_analysis"],
            "threat_analysis": state["threat_analysis"],
            "compliance_impact": state["compliance_analysis"],
            "incident_details": state.get("incident_created", {}),
            "forensics_status": state.get("forensics_evidence", {}),
            "explainability_report": state.get("explainability_report", {}),
            "recommendations": recommendations,
            "workflow_complete": True
        }
        
        return state
    
    def _should_create_incident(self, state: SecurityState) -> str:
        """Conditional logic to determine if incident should be created"""
        network_risk = state["network_analysis"].get("risk_score", 0)
        threat_severity = state["threat_analysis"].get("severity_score", 0)
        compliance_violations = len(state["compliance_analysis"].get("violations", []))
        
        # Create incident if high risk or compliance violations
        if network_risk >= 7 or threat_severity >= 7 or compliance_violations > 0:
            return "create_incident"
        else:
            return "skip_incident"