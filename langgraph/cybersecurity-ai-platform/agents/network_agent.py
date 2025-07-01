import asyncio
from typing import Dict, List
from netmiko import ConnectHandler
from langchain.tools import Tool
from core.bedrock_client import BedrockLLMClient

class NetworkSecurityAgent:
    def __init__(self):
        self.device_configs = {}
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
        
    async def assess_network_impact(self, event: Dict) -> Dict:
        """Assess network impact using AI agent"""
        query = f"Analyze network security impact: {event}"
        result = await asyncio.to_thread(self.agent.invoke, {"input": query})
        
        # Parse AI response and combine with rule-based analysis
        source_ip = event.get("source_ip", "unknown")
        dest_ip = event.get("destination_ip", "unknown")
        protocol = event.get("protocol", "unknown")
        
        risk_score = self._calculate_network_risk(source_ip, dest_ip, protocol)
        
        return {
            "ai_analysis": result["output"],
            "risk_score": risk_score,
            "affected_segments": self._identify_network_segments(source_ip, dest_ip),
            "lateral_movement_risk": risk_score > 6,
            "recommended_isolation": risk_score > 8
        }
    
    async def generate_mitigation_actions(self, event: Dict) -> List[str]:
        """Generate network-level mitigation actions"""
        actions = []
        source_ip = event.get("source_ip")
        
        if self._is_internal_ip(source_ip):
            actions.append(f"Isolate host {source_ip} from network")
            actions.append(f"Block traffic from {source_ip} at firewall")
        else:
            actions.append(f"Block external IP {source_ip} at perimeter")
            
        actions.append("Update IDS/IPS signatures")
        return actions
    
    async def configure_device(self, config: Dict) -> Dict:
        """Configure network device"""
        device_ip = config.get("ip_address")
        device_type = config.get("device_type")
        changes = config.get("config_changes", {})
        
        # Simulate device configuration
        config_commands = self._generate_config_commands(device_type, changes)
        
        return {
            "device": device_ip,
            "status": "configured",
            "commands_applied": config_commands,
            "backup_created": True
        }
    
    def _calculate_network_risk(self, source_ip: str, dest_ip: str, protocol: str) -> int:
        """Calculate network risk score"""
        risk = 5  # Base risk
        
        if dest_ip and dest_ip != "unknown" and self._is_critical_asset(dest_ip):
            risk += 3
        if protocol and protocol.upper() in ["SSH", "RDP", "SMB"]:
            risk += 2
        if source_ip and dest_ip and source_ip != "unknown" and dest_ip != "unknown" and self._is_lateral_movement(source_ip, dest_ip):
            risk += 2
            
        return min(risk, 10)
    
    def _identify_network_segments(self, source_ip: str, dest_ip: str) -> List[str]:
        """Identify affected network segments"""
        segments = []
        if source_ip and source_ip.startswith("192.168.1"):
            segments.append("DMZ")
        if dest_ip and dest_ip.startswith("10.0.0"):
            segments.append("Internal")
        return segments
    
    def _is_internal_ip(self, ip: str) -> bool:
        """Check if IP is internal"""
        if not ip or ip == "unknown":
            return False
        return ip.startswith(("10.", "192.168.", "172.16."))
    
    def _is_critical_asset(self, ip: str) -> bool:
        """Check if IP is critical asset"""
        if not ip or ip == "unknown":
            return False
        critical_ranges = ["10.0.1.", "192.168.100."]
        return any(ip.startswith(range_) for range_ in critical_ranges)
    
    def _is_lateral_movement(self, source_ip: str, dest_ip: str) -> bool:
        """Detect potential lateral movement"""
        if not source_ip or not dest_ip or source_ip == "unknown" or dest_ip == "unknown":
            return False
        try:
            return (self._is_internal_ip(source_ip) and 
                    self._is_internal_ip(dest_ip) and
                    source_ip.split('.')[2] != dest_ip.split('.')[2])
        except:
            return False
    
    def _generate_config_commands(self, device_type: str, changes: Dict) -> List[str]:
        """Generate configuration commands"""
        commands = []
        
        if device_type == "firewall":
            for rule in changes.get("firewall_rules", []):
                commands.append(f"access-list deny {rule}")
        elif device_type == "switch":
            for vlan in changes.get("vlans", []):
                commands.append(f"vlan {vlan}")
                
        return commands
    
    def _create_agent(self):
        """Create LangChain agent with network security tools"""
        tools = [
            Tool(
                name="calculate_risk",
                description="Calculate network risk score for IP addresses and protocols",
                func=lambda event: str(self._calculate_network_risk(
                    eval(event).get('source_ip', 'unknown') if isinstance(event, str) else event.get('source_ip', 'unknown'),
                    eval(event).get('destination_ip', 'unknown') if isinstance(event, str) else event.get('destination_ip', 'unknown'),
                    eval(event).get('protocol', 'unknown') if isinstance(event, str) else event.get('protocol', 'unknown')
                ))
            ),
            Tool(
                name="identify_segments", 
                description="Identify network segments affected by IPs",
                func=lambda event: str(self._identify_network_segments(
                    eval(event).get('source_ip', 'unknown') if isinstance(event, str) else event.get('source_ip', 'unknown'),
                    eval(event).get('destination_ip', 'unknown') if isinstance(event, str) else event.get('destination_ip', 'unknown')
                ))
            ),
            Tool(
                name="check_critical_asset",
                description="Check if IP is a critical network asset", 
                func=lambda ip: str(self._is_critical_asset(ip))
            )
        ]
        
        system_prompt = """You are a Network Security Engineer AI agent. Analyze network security events and provide expert recommendations for:
        - Network risk assessment
        - Threat containment strategies  
        - Device configuration changes
        - Network segmentation recommendations
        
        Use the available tools to gather technical data and provide actionable security guidance."""
        
        return self.bedrock_client.create_agent(tools, system_prompt)