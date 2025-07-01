import asyncio
from typing import Dict, List
from datetime import datetime
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient

class ForensicsAgent:
    def __init__(self):
        self.evidence_chain = []
        self.analysis_results = {}
        self.bedrock_client = BedrockLLMClient()
        self.current_event = {}
        self.agent = self._create_agent()
        
    async def collect_evidence(self, event: Dict) -> Dict:
        """Collect digital evidence using AI agent"""
        self.current_event = event
        query = f"Plan evidence collection for security event: {event}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        evidence_id = f"EVD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        evidence = {
            "id": evidence_id,
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "ai_collection_plan": ai_result["output"],
            "artifacts": self._identify_artifacts(event),
            "preservation_status": "Collected",
            "chain_of_custody": [{"action": "Initial Collection", "timestamp": datetime.now().isoformat()}]
        }
        
        self.evidence_chain.append(evidence)
        return evidence
    
    async def analyze_artifacts(self, evidence_id: str) -> Dict:
        """Analyze collected artifacts"""
        evidence = next((e for e in self.evidence_chain if e["id"] == evidence_id), None)
        if not evidence:
            return {"error": "Evidence not found"}
        
        query = f"Analyze digital artifacts: {evidence['artifacts']}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        analysis = {
            "evidence_id": evidence_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "ai_analysis": ai_result["output"],
            "timeline": self._create_timeline(evidence),
            "indicators": self._extract_indicators(evidence),
            "attribution": self._assess_attribution(evidence)
        }
        
        self.analysis_results[evidence_id] = analysis
        return analysis
    
    async def generate_report(self, evidence_id: str) -> Dict:
        """Generate forensics report"""
        evidence = next((e for e in self.evidence_chain if e["id"] == evidence_id), None)
        analysis = self.analysis_results.get(evidence_id)
        
        if not evidence or not analysis:
            return {"error": "Evidence or analysis not found"}
        
        report = {
            "report_id": f"RPT-{evidence_id}",
            "generated": datetime.now().isoformat(),
            "evidence_summary": evidence,
            "analysis_summary": analysis,
            "findings": self._summarize_findings(analysis),
            "recommendations": self._generate_recommendations(analysis)
        }
        
        return report
    
    def _identify_artifacts(self, event: Dict) -> List[str]:
        """Identify digital artifacts to collect"""
        artifacts = ["System logs", "Network traffic captures"]
        
        protocol = event.get("protocol", "").upper()
        if protocol in ["HTTP", "HTTPS"]:
            artifacts.extend(["Web server logs", "Browser artifacts"])
        elif protocol in ["SSH", "RDP"]:
            artifacts.extend(["Authentication logs", "Session recordings"])
        elif protocol in ["SMB", "CIFS"]:
            artifacts.extend(["File access logs", "Share permissions"])
            
        return artifacts
    
    def _create_timeline(self, evidence: Dict) -> List[Dict]:
        """Create event timeline"""
        event = evidence["event"]
        return [
            {
                "timestamp": evidence["timestamp"],
                "event": f"Security event detected from {event.get('source_ip')}",
                "source": "Security Monitoring"
            },
            {
                "timestamp": evidence["timestamp"],
                "event": f"Evidence collection initiated",
                "source": "Forensics Agent"
            }
        ]
    
    def _extract_indicators(self, evidence: Dict) -> List[str]:
        """Extract indicators of compromise"""
        event = evidence["event"]
        indicators = []
        
        if event.get("source_ip"):
            indicators.append(f"IP: {event['source_ip']}")
        if event.get("destination_ip"):
            indicators.append(f"Target IP: {event['destination_ip']}")
        if event.get("protocol"):
            indicators.append(f"Protocol: {event['protocol']}")
            
        return indicators
    
    def _assess_attribution(self, evidence: Dict) -> Dict:
        """Assess threat attribution"""
        event = evidence["event"]
        source_ip = event.get("source_ip", "")
        
        attribution = {
            "confidence": "Low",
            "threat_actor": "Unknown",
            "campaign": "Unknown"
        }
        
        # Simple attribution logic
        if source_ip.startswith("192.168."):
            attribution["threat_actor"] = "Internal Threat"
            attribution["confidence"] = "Medium"
        elif "malware" in event.get("description", "").lower():
            attribution["threat_actor"] = "Cybercriminal Group"
            attribution["confidence"] = "Medium"
            
        return attribution
    
    def _summarize_findings(self, analysis: Dict) -> List[str]:
        """Summarize key findings"""
        return [
            "Security incident confirmed through digital evidence",
            f"Timeline established with {len(analysis['timeline'])} key events",
            f"Identified {len(analysis['indicators'])} indicators of compromise",
            f"Attribution assessment: {analysis['attribution']['confidence']} confidence"
        ]
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate forensics recommendations"""
        return [
            "Preserve all collected evidence for legal proceedings",
            "Implement additional monitoring for identified indicators",
            "Review and update incident response procedures",
            "Consider threat hunting activities based on findings"
        ]
    
    def _create_agent(self):
        """Create LangChain agent with forensics tools"""
        tools = [
            Tool(
                name="identify_artifacts",
                description="Identify digital artifacts to collect for forensic analysis",
                func=lambda event: str(self._identify_artifacts(eval(event) if isinstance(event, str) else event))
            ),
            Tool(
                name="extract_indicators",
                description="Extract indicators of compromise from artifacts list",
                func=lambda artifacts: str(self._extract_indicators({"event": self.current_event}))
            ),
            Tool(
                name="assess_attribution",
                description="Assess threat actor attribution from indicators",
                func=lambda indicators: str(self._assess_attribution({"event": self.current_event}))
            )
        ]
        
        system_prompt = """You are a Digital Forensics AI agent. Conduct thorough forensic investigations:
        - Plan and execute evidence collection procedures
        - Analyze digital artifacts and create timelines
        - Extract indicators of compromise
        - Assess threat actor attribution
        - Generate comprehensive forensic reports
        
        Follow proper chain of custody and forensic best practices."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)