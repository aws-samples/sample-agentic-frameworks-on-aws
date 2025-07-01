import asyncio
from typing import Dict, List
from datetime import datetime
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient

class ThreatDetectionAgent:
    def __init__(self):
        self.threat_intelligence_feeds = []
        self.ioc_database = {}
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
        
    async def analyze_threat(self, event: Dict) -> Dict:
        """Analyze threat using Bedrock Claude AI agent"""
        query = f"Analyze security threat: {event}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        # Combine AI analysis with rule-based threat detection
        threat_type = self._classify_threat_type(event)
        severity_score = self._calculate_threat_severity(event)
        
        return {
            "ai_analysis": ai_result["output"],
            "threat_type": threat_type,
            "severity_score": severity_score,
            "confidence": self._calculate_confidence(event),
            "ioc_matches": self._check_ioc_matches(event),
            "attack_vector": self._identify_attack_vector(event),
            "recommended_response": self._get_recommended_response(severity_score)
        }
    
    async def correlate_threats(self, events: List[Dict]) -> Dict:
        """Correlate multiple threat events"""
        correlations = []
        
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if self._are_related(event1, event2):
                    correlations.append({
                        "event1": event1,
                        "event2": event2,
                        "correlation_type": "ip_based",
                        "confidence": 0.8
                    })
        
        return {
            "correlations": correlations,
            "campaign_indicators": self._detect_campaign_patterns(events),
            "threat_actor_attribution": self._assess_attribution(events)
        }
    
    def _classify_threat_type(self, event: Dict) -> str:
        """Classify threat type based on event characteristics"""
        description = event.get("description", "").lower()
        event_type = event.get("event_type", "").lower()
        
        # Enhanced pattern matching
        if any(term in description for term in ["sql injection", "sqli", "union select", "drop table"]):
            return "Web Application Attack"
        elif any(term in description for term in ["brute force", "failed login", "multiple attempts"]):
            return "Brute Force Attack"
        elif any(term in description for term in ["malware", "trojan", "virus", "c&c", "command and control"]):
            return "Malware"
        elif any(term in description for term in ["data breach", "exfiltration", "data transfer"]):
            return "Data Exfiltration"
        elif event_type == "intrusion":
            return "Brute Force Attack"
        elif event_type == "web_attack":
            return "Web Application Attack"
        elif event_type == "malware":
            return "Malware"
        elif event_type == "data_breach":
            return "Data Exfiltration"
        else:
            return "Unknown Threat"
    
    def _calculate_threat_severity(self, event: Dict) -> int:
        """Calculate threat severity score"""
        base_score = 5
        
        severity = event.get("severity", "medium").lower()
        if severity == "critical":
            base_score = 8
        elif severity == "high":
            base_score = 7
        elif severity == "medium":
            base_score = 5
        elif severity == "low":
            base_score = 3
        
        # Adjust based on threat type
        threat_type = self._classify_threat_type(event)
        if threat_type == "Malware":
            base_score += 1
        elif threat_type == "Data Exfiltration":
            base_score += 2
        
        return min(base_score, 10)
    
    def _calculate_confidence(self, event: Dict) -> float:
        """Calculate confidence in threat assessment"""
        confidence = 0.5
        
        if event.get("source_ip") and event.get("source_ip") != "unknown":
            confidence += 0.2
        if event.get("destination_ip") and event.get("destination_ip") != "unknown":
            confidence += 0.2
        if event.get("protocol") and event.get("protocol") != "unknown":
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _check_ioc_matches(self, event: Dict) -> List[Dict]:
        """Check for IOC matches"""
        matches = []
        source_ip = event.get("source_ip", "")
        
        # Simulate IOC matching
        if source_ip == "192.168.1.45":
            matches.append({
                "type": "malicious_ip",
                "value": source_ip,
                "source": "ThreatFeed_Alpha",
                "confidence": 0.85
            })
        
        return matches
    
    def _identify_attack_vector(self, event: Dict) -> str:
        """Identify attack vector"""
        protocol = event.get("protocol", "").upper()
        description = event.get("description", "").lower()
        
        if protocol in ["SSH", "RDP", "TELNET"]:
            return "Remote Access"
        elif protocol in ["HTTP", "HTTPS"] or "web" in description:
            return "Web-based"
        elif "network" in description or "lateral" in description:
            return "Network-based"
        else:
            return "Network-based"
    
    def _get_recommended_response(self, severity_score: int) -> str:
        """Get recommended response based on severity"""
        if severity_score >= 8:
            return "Immediate containment and investigation"
        elif severity_score >= 6:
            return "Enhanced monitoring and containment"
        else:
            return "Monitor and investigate"
    
    def _are_related(self, event1: Dict, event2: Dict) -> bool:
        """Check if two events are related"""
        return (event1.get("source_ip") == event2.get("source_ip") or
                event1.get("destination_ip") == event2.get("destination_ip"))
    
    def _detect_campaign_patterns(self, events: List[Dict]) -> List[str]:
        """Detect campaign patterns"""
        patterns = []
        
        # Check for coordinated attacks
        source_ips = [e.get("source_ip") for e in events if e.get("source_ip")]
        if len(set(source_ips)) < len(source_ips) * 0.5:
            patterns.append("Coordinated attack from multiple sources")
        
        return patterns
    
    def _assess_attribution(self, events: List[Dict]) -> Dict:
        """Assess threat actor attribution"""
        # Simple attribution logic
        internal_ips = sum(1 for e in events if self._is_internal_ip(e.get("source_ip", "")))
        
        if internal_ips > len(events) * 0.7:
            return {"confidence": "Medium", "threat_actor": "Internal Threat", "campaign": "Unknown"}
        else:
            return {"confidence": "Low", "threat_actor": "Unknown", "campaign": "Unknown"}
    
    def _is_internal_ip(self, ip: str) -> bool:
        """Check if IP is internal"""
        if not ip:
            return False
        return ip.startswith(("10.", "192.168.", "172.16."))
    
    def _create_agent(self):
        """Create LangChain agent with threat detection tools"""
        tools = [
            Tool(
                name="classify_threat",
                description="Classify threat type from security events",
                func=lambda event: self._classify_threat_type(eval(event) if isinstance(event, str) and event.startswith('{') else event)
            ),
            Tool(
                name="calculate_severity",
                description="Calculate threat severity score",
                func=lambda event: str(self._calculate_threat_severity(eval(event) if isinstance(event, str) and event.startswith('{') else event))
            ),
            Tool(
                name="identify_attack_vector",
                description="Identify attack vector used in threat",
                func=lambda event: self._identify_attack_vector(eval(event) if isinstance(event, str) and event.startswith('{') else event)
            )
        ]
        
        system_prompt = """You are a Threat Detection AI agent. Analyze security threats and provide expert assessment of:
        - Threat classification and severity
        - Attack vectors and techniques
        - Threat actor attribution
        - Recommended response actions
        
        Focus on accurate threat identification and actionable intelligence for security teams."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)