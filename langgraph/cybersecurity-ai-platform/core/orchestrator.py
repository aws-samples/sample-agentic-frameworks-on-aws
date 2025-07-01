import asyncio
from typing import Dict, List
from agents.network_agent import NetworkSecurityAgent
from agents.threat_agent import ThreatDetectionAgent
from agents.compliance_agent import ComplianceAgent

class AgentOrchestrator:
    def __init__(self):
        self.network_agent = NetworkSecurityAgent()
        self.threat_agent = ThreatDetectionAgent()
        self.compliance_agent = ComplianceAgent()
        self.active_threats = []

    async def process_security_event(self, event: Dict) -> Dict:
        """Orchestrate multiple agents to analyze security event"""
        tasks = [
            self.threat_agent.analyze_threat(event),
            self.network_agent.assess_network_impact(event),
            self.compliance_agent.check_compliance_impact(event)
        ]
        
        threat_analysis, network_impact, compliance_impact = await asyncio.gather(*tasks)
        
        # Synthesize results
        severity_score = max(
            threat_analysis.get("severity_score", 0),
            network_impact.get("risk_score", 0)
        )
        
        actions = []
        if severity_score > 7:
            actions.extend(await self.network_agent.generate_mitigation_actions(event))
        
        return {
            "threat_analysis": threat_analysis,
            "network_impact": network_impact,
            "compliance_impact": compliance_impact,
            "severity_score": severity_score,
            "actions": actions
        }

    async def configure_device(self, config: Dict):
        """Configure network device through network agent"""
        return await self.network_agent.configure_device(config)

    async def get_active_threats(self) -> List[Dict]:
        """Get current active threats"""
        return await self.threat_agent.get_active_threats()

    async def get_compliance_status(self) -> Dict:
        """Get compliance status"""
        return await self.compliance_agent.get_compliance_status()