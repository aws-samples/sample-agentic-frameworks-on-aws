import asyncio
from typing import Dict, List
from datetime import datetime
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient

class ComplianceAgent:
    def __init__(self):
        self.compliance_frameworks = ["SOC2", "PCI-DSS", "NIST", "ISO27001"]
        self.policy_violations = []
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
        
    async def check_compliance_impact(self, event: Dict) -> Dict:
        """Check compliance impact using Bedrock Claude AI agent"""
        query = f"Analyze compliance impact for security event: {event}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        # Combine AI analysis with rule-based compliance checking
        violations = self._identify_violations(event)
        frameworks_affected = self._get_affected_frameworks(violations)
        
        return {
            "ai_analysis": ai_result["output"],
            "violations": violations,
            "frameworks_affected": frameworks_affected,
            "compliance_risk": self._calculate_compliance_risk(violations),
            "required_actions": self._get_required_actions(violations),
            "reporting_required": len(frameworks_affected) > 0
        }
    
    async def get_compliance_status(self) -> Dict:
        """Get overall compliance status"""
        return {
            "overall_score": 85,
            "frameworks": {
                "SOC2": {"score": 88, "status": "Compliant", "last_audit": "2024-01-01"},
                "PCI-DSS": {"score": 82, "status": "Compliant", "last_audit": "2023-12-15"},
                "NIST": {"score": 90, "status": "Compliant", "last_audit": "2024-01-10"},
                "ISO27001": {"score": 85, "status": "Compliant", "last_audit": "2023-11-20"}
            },
            "active_violations": len(self.policy_violations),
            "remediation_items": self._get_remediation_items()
        }
    
    def _identify_violations(self, event: Dict) -> List[Dict]:
        """Identify policy violations from security event"""
        violations = []
        
        # Check for data access violations
        if "database" in event.get("description", "").lower():
            violations.append({
                "type": "Unauthorized Data Access",
                "severity": "High",
                "policy": "Data Protection Policy",
                "framework": "PCI-DSS"
            })
        
        # Check for network security violations
        if event.get("protocol") in ["SSH", "RDP"] and event.get("severity") == "high":
            violations.append({
                "type": "Privileged Access Violation",
                "severity": "Medium",
                "policy": "Access Control Policy",
                "framework": "SOC2"
            })
        
        # Check for incident response violations
        if event.get("severity") == "critical":
            violations.append({
                "type": "Incident Response Required",
                "severity": "High",
                "policy": "Incident Response Policy",
                "framework": "NIST"
            })
            
        return violations
    
    def _get_affected_frameworks(self, violations: List[Dict]) -> List[str]:
        """Get list of affected compliance frameworks"""
        frameworks = set()
        for violation in violations:
            frameworks.add(violation.get("framework"))
        return list(frameworks)
    
    def _calculate_compliance_risk(self, violations: List[Dict]) -> str:
        """Calculate overall compliance risk level"""
        if not violations:
            return "Low"
        
        high_severity_count = sum(1 for v in violations if v.get("severity") == "High")
        
        if high_severity_count >= 2:
            return "High"
        elif high_severity_count == 1:
            return "Medium"
        else:
            return "Low"
    
    def _get_required_actions(self, violations: List[Dict]) -> List[str]:
        """Get required compliance actions"""
        actions = []
        
        for violation in violations:
            if violation.get("framework") == "PCI-DSS":
                actions.append("Document incident for PCI compliance report")
                actions.append("Review cardholder data access controls")
            elif violation.get("framework") == "SOC2":
                actions.append("Update security monitoring procedures")
                actions.append("Review access control effectiveness")
            elif violation.get("framework") == "NIST":
                actions.append("Activate incident response plan")
                actions.append("Document lessons learned")
                
        return list(set(actions))  # Remove duplicates
    
    def _get_remediation_items(self) -> List[Dict]:
        """Get current remediation items"""
        return [
            {
                "id": "REM-001",
                "description": "Update firewall rules for PCI compliance",
                "priority": "High",
                "due_date": "2024-02-01",
                "framework": "PCI-DSS"
            },
            {
                "id": "REM-002", 
                "description": "Implement additional logging for SOC2",
                "priority": "Medium",
                "due_date": "2024-02-15",
                "framework": "SOC2"
            }
        ]
    
    def _create_agent(self):
        """Create LangChain agent with compliance tools"""
        tools = [
            Tool(
                name="identify_violations",
                description="Identify policy violations from security events",
                func=lambda event: str(self._identify_violations(eval(event) if isinstance(event, str) else event))
            ),
            Tool(
                name="calculate_compliance_risk",
                description="Calculate compliance risk level",
                func=lambda violations: self._calculate_compliance_risk(eval(violations) if isinstance(violations, str) and violations.startswith('[') else violations)
            ),
            Tool(
                name="get_affected_frameworks",
                description="Get compliance frameworks affected by violations",
                func=lambda violations: str(self._get_affected_frameworks(eval(violations) if isinstance(violations, str) and violations.startswith('[') else violations))
            )
        ]
        
        system_prompt = """You are a Compliance Management AI agent. Analyze security events for compliance impact across:
        - SOC2 Type II requirements
        - PCI-DSS standards
        - NIST Cybersecurity Framework
        - ISO 27001 controls
        
        Provide compliance risk assessment and required remediation actions for regulatory adherence."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)