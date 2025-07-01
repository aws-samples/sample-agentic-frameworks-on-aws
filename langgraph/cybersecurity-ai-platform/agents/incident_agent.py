import asyncio
from typing import Dict, List
from datetime import datetime
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient

class IncidentResponseAgent:
    def __init__(self):
        self.active_incidents = []
        self.playbooks = {}
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
        
    async def create_incident(self, event: Dict) -> Dict:
        """Create incident using AI agent"""
        query = f"Create incident response plan for: {event}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        severity = self._determine_severity(event)
        
        incident = {
            "id": incident_id,
            "severity": severity,
            "status": "Open",
            "created": datetime.now().isoformat(),
            "event": event,
            "ai_response_plan": ai_result["output"],
            "playbook": self._select_playbook(event),
            "assigned_team": self._assign_team(severity)
        }
        
        self.active_incidents.append(incident)
        return incident
    
    async def get_response_actions(self, incident_id: str) -> List[str]:
        """Get incident response actions"""
        incident = next((i for i in self.active_incidents if i["id"] == incident_id), None)
        if not incident:
            return []
            
        severity = incident["severity"]
        event_type = incident["event"].get("event_type", "")
        
        actions = []
        if severity == "Critical":
            actions.extend([
                "Activate emergency response team",
                "Isolate affected systems immediately",
                "Notify CISO and executive team"
            ])
        elif severity == "High":
            actions.extend([
                "Escalate to security team lead",
                "Begin containment procedures",
                "Document all actions taken"
            ])
            
        return actions
    
    def _determine_severity(self, event: Dict) -> str:
        """Determine incident severity"""
        event_severity = event.get("severity", "").lower()
        if event_severity == "critical":
            return "Critical"
        elif event_severity == "high":
            return "High"
        elif event_severity == "medium":
            return "Medium"
        else:
            return "Low"
    
    def _select_playbook(self, event: Dict) -> str:
        """Select appropriate incident response playbook"""
        event_type = event.get("event_type", "").lower()
        if "malware" in event_type:
            return "Malware Response Playbook"
        elif "intrusion" in event_type:
            return "Intrusion Response Playbook"
        elif "data" in event_type:
            return "Data Breach Response Playbook"
        else:
            return "General Incident Response Playbook"
    
    def _assign_team(self, severity: str) -> str:
        """Assign response team based on severity"""
        if severity == "Critical":
            return "Emergency Response Team"
        elif severity == "High":
            return "Security Operations Team"
        else:
            return "SOC Analyst"
    
    def _create_agent(self):
        """Create LangChain agent with incident response tools"""
        tools = [
            Tool(
                name="determine_severity",
                description="Determine incident severity level",
                func=lambda event: self._determine_severity(eval(event) if isinstance(event, str) else event)
            ),
            Tool(
                name="select_playbook",
                description="Select appropriate incident response playbook",
                func=lambda event: self._select_playbook(eval(event) if isinstance(event, str) else event)
            ),
            Tool(
                name="assign_team",
                description="Assign response team based on severity",
                func=lambda severity: self._assign_team(severity)
            )
        ]
        
        system_prompt = """You are an Incident Response AI agent. Coordinate incident response activities:
        - Create structured incident response plans
        - Assign appropriate response teams
        - Select relevant playbooks and procedures
        - Escalate based on severity levels
        
        Provide clear, actionable incident response guidance following industry best practices."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)