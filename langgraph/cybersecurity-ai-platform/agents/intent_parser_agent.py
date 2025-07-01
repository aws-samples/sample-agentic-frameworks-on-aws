import asyncio
from typing import Dict, List, Optional
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient
import ast

class IntentParserAgent:
    def __init__(self):
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
        
    async def parse_intent(self, user_input: str) -> Dict:
        """Parse user intent and determine which agents to call"""
        query = f"Parse this security query and determine required agents: {user_input}"
        ai_result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        # Extract structured response from AI output
        intent_data = self._extract_intent_from_ai_output(ai_result["output"], user_input)
        
        return {
            "user_input": user_input,
            "ai_analysis": ai_result["output"],
            "intent_type": intent_data["intent_type"],
            "required_agents": intent_data["required_agents"],
            "structured_event": intent_data["structured_event"],
            "confidence": intent_data["confidence"]
        }
    
    def _extract_intent_from_ai_output(self, ai_output: str, user_input: str) -> Dict:
        """Extract intent data from AI output by parsing tool results"""
        # Default values
        intent_data = {
            "intent_type": "full_security_analysis",
            "required_agents": ["all"],
            "structured_event": {},
            "confidence": 0.8
        }
        
        # Look for tool results in the AI output
        lines = ai_output.split('\n')
        
        for i, line in enumerate(lines):
            # Look for extract_event_data tool result
            if "extract_event_data" in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('{') and next_line.endswith('}'):
                    try:
                        # Parse the dictionary string
                        event_data = ast.literal_eval(next_line)
                        intent_data["structured_event"] = event_data
                    except:
                        # Fallback to manual extraction
                        intent_data["structured_event"] = self._extract_event_data(user_input)
            
            # Look for determine_agents tool result
            elif "determine_agents" in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('[') and next_line.endswith(']'):
                    try:
                        agents = ast.literal_eval(next_line)
                        intent_data["required_agents"] = agents
                    except:
                        pass
            
            # Look for classify_intent tool result
            elif "classify_intent" in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line in ["network_analysis", "threat_analysis", "compliance_check", 
                               "incident_response", "forensic_investigation", "explanation_request", 
                               "full_security_analysis"]:
                    intent_data["intent_type"] = next_line
        
        # If no structured_event was extracted, do it manually
        if not intent_data["structured_event"]:
            intent_data["structured_event"] = self._extract_event_data(user_input)
        
        return intent_data
    
    def _classify_intent(self, user_input: str) -> str:
        """Classify user intent"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["network", "firewall", "segment", "isolation"]):
            return "network_analysis"
        elif any(word in input_lower for word in ["threat", "malware", "attack", "vulnerability"]):
            return "threat_analysis"
        elif any(word in input_lower for word in ["compliance", "policy", "regulation", "audit"]):
            return "compliance_check"
        elif any(word in input_lower for word in ["incident", "response", "playbook"]):
            return "incident_response"
        elif any(word in input_lower for word in ["forensic", "evidence", "investigation"]):
            return "forensic_investigation"
        elif any(word in input_lower for word in ["explain", "why", "reason", "justify"]):
            return "explanation_request"
        else:
            return "full_security_analysis"
    
    def _determine_agents(self, intent_type: str) -> List[str]:
        """Determine which agents to call based on intent"""
        agent_mapping = {
            "network_analysis": ["network"],
            "threat_analysis": ["threat"],
            "compliance_check": ["compliance"],
            "incident_response": ["incident"],
            "forensic_investigation": ["forensics"],
            "explanation_request": ["explainability"],
            "full_security_analysis": ["all"]
        }
        return agent_mapping.get(intent_type, ["all"])
    
    def _extract_event_data(self, user_input: str) -> Dict:
        """Extract structured event data from user input"""
        # Basic event extraction - enhance as needed
        event = {
            "event_type": "unknown",
            "severity": "medium",
            "source_ip": "",
            "destination_ip": "",
            "protocol": "",
            "description": user_input
        }
        
        input_lower = user_input.lower()
        
        # Extract IPs using simple pattern matching
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, user_input)
        if len(ips) >= 1:
            event["source_ip"] = ips[0]
        if len(ips) >= 2:
            event["destination_ip"] = ips[1]
        
        # Determine event type
        if any(word in input_lower for word in ["brute force", "failed login", "ssh"]):
            event["event_type"] = "intrusion"
            event["protocol"] = "SSH"
        elif any(word in input_lower for word in ["sql injection", "web attack"]):
            event["event_type"] = "web_attack"
            event["protocol"] = "HTTPS"
        elif any(word in input_lower for word in ["malware", "trojan", "c&c"]):
            event["event_type"] = "malware"
            event["protocol"] = "HTTP"
        elif any(word in input_lower for word in ["data breach", "exfiltration"]):
            event["event_type"] = "data_breach"
            event["protocol"] = "HTTPS"
        
        # Determine severity
        if any(word in input_lower for word in ["critical", "severe", "urgent"]):
            event["severity"] = "critical"
        elif any(word in input_lower for word in ["high", "important"]):
            event["severity"] = "high"
        elif any(word in input_lower for word in ["low", "minor"]):
            event["severity"] = "low"
        
        return event
    
    def _create_agent(self):
        """Create LangChain agent for intent parsing"""
        tools = [
            Tool(
                name="classify_intent",
                description="Classify user intent for security queries",
                func=lambda query: self._classify_intent(query)
            ),
            Tool(
                name="determine_agents",
                description="Determine which security agents to call",
                func=lambda intent: str(self._determine_agents(intent))
            ),
            Tool(
                name="extract_event_data",
                description="Extract structured event data from user input",
                func=lambda query: str(self._extract_event_data(query))
            )
        ]
        
        system_prompt = """You are an Intent Parser for cybersecurity queries. Analyze user input to:
        - Classify the security intent (network_analysis, threat_analysis, compliance_check, etc.)
        - Determine which security agents should be called
        - Extract structured event data when applicable
        
        Use the available tools and provide clear intent classification and agent routing decisions."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)