#!/usr/bin/env python3
"""Interactive Security Console - Real-time cybersecurity analysis with step-by-step execution visibility"""
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any
import json

# Add parent directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set AWS region
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

try:
    from core.intelligent_orchestrator import IntelligentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Cannot import orchestrator: {e}")
    ORCHESTRATOR_AVAILABLE = False

class SecurityConsole:
    def __init__(self):
        self.orchestrator = IntelligentOrchestrator() if ORCHESTRATOR_AVAILABLE else None
        self.session_history = []
        
    def display_banner(self):
        print("\n" + "="*80)
        print("🛡️  INTERACTIVE CYBERSECURITY ANALYSIS CONSOLE")
        print("="*80)
        print("🤖 AI-Powered Security Analysis with Real-time Agent Execution")
        print("📊 Multi-Agent Intelligence: Network • Threat • Compliance • Incident • Forensics")
        print("="*80)
        
    def display_menu(self):
        print("\n📋 AVAILABLE COMMANDS:")
        print("  1️⃣  analyze <query>     - Natural language security analysis")
        print("  2️⃣  simulate <type>     - Simulate security events")
        print("  3️⃣  history            - View session history")
        print("  4️⃣  help               - Show detailed help")
        print("  5️⃣  exit               - Exit console")
        print("-" * 50)
        
    def display_help(self):
        print("\n📖 DETAILED HELP & SOPHISTICATED EXAMPLES:")
        
        print("\n🔍 NETWORK SECURITY ANALYSIS:")
        print("  analyze Assess network risk for lateral movement from DMZ host 192.168.1.45 to critical database server 10.0.1.100 via SSH")
        print("  analyze Evaluate network segmentation effectiveness between development subnet 172.16.10.0/24 and production environment")
        print("  analyze Check firewall rule violations for privileged access from external IP 203.0.113.15 to internal management interface")
        print("  analyze Investigate suspicious network traffic patterns between workstation 10.0.2.25 and external cloud storage 185.199.108.153")
        
        print("\n🎯 ADVANCED THREAT ANALYSIS:")
        print("  analyze Deep dive into APT campaign indicators: C2 beaconing from 10.0.3.45 to suspicious domain malware-c2.example.com")
        print("  analyze Correlate multi-stage attack: initial phishing email, macro execution, credential harvesting, and lateral movement to domain controller")
        print("  analyze Analyze zero-day exploit attempt targeting Apache Struts vulnerability CVE-2023-50164 from IP 198.51.100.42")
        print("  analyze Investigate fileless malware execution using PowerShell Empire framework with persistence mechanisms")
        print("  analyze Assess ransomware deployment patterns: file encryption, shadow copy deletion, and network share propagation")
        
        print("\n📋 COMPLIANCE & REGULATORY ANALYSIS:")
        print("  analyze Evaluate GDPR compliance impact of data exfiltration incident affecting EU customer PII database")
        print("  analyze Assess SOX compliance violations from unauthorized access to financial reporting systems during quarter-end")
        print("  analyze Review HIPAA breach notification requirements for compromised patient records in healthcare database")
        print("  analyze Analyze PCI-DSS scope impact from cardholder data environment compromise via SQL injection")
        print("  analyze Check NIST Cybersecurity Framework alignment for incident response procedures and control effectiveness")
        
        print("\n🚨 INCIDENT RESPONSE & FORENSICS:")
        print("  analyze Create comprehensive incident response plan for nation-state actor targeting critical infrastructure")
        print("  analyze Develop forensic investigation strategy for insider threat involving privileged user data theft")
        print("  analyze Coordinate multi-team response for supply chain compromise affecting software distribution pipeline")
        print("  analyze Plan evidence preservation for legal proceedings involving intellectual property theft via cyber espionage")
        print("  analyze Design containment strategy for worm propagation across enterprise network with 10,000+ endpoints")
        
        print("\n🔬 DIGITAL FORENSICS & ATTRIBUTION:")
        print("  analyze Collect volatile memory artifacts from compromised domain controller for malware analysis")
        print("  analyze Preserve network packet captures for timeline reconstruction of advanced persistent threat activity")
        print("  analyze Extract browser artifacts and cached credentials from suspected insider threat workstation")
        print("  analyze Analyze malware reverse engineering results to identify threat actor TTPs and infrastructure")
        print("  analyze Correlate threat intelligence feeds with observed IOCs for attribution to known APT groups")
        
        print("\n🧠 AI DECISION EXPLAINABILITY:")
        print("  analyze Explain risk scoring methodology for critical infrastructure targeting by foreign adversary")
        print("  analyze Justify automated containment decisions during active ransomware deployment")
        print("  analyze Provide audit trail for compliance officer review of incident classification and response actions")
        print("  analyze Generate executive briefing on AI-driven threat detection accuracy and false positive rates")
        
        print("\n🎭 SOPHISTICATED SIMULATION SCENARIOS:")
        print("  simulate apt_campaign      - Advanced Persistent Threat multi-stage attack")
        print("  simulate insider_threat    - Malicious insider data exfiltration")
        print("  simulate supply_chain      - Software supply chain compromise")
        print("  simulate ransomware        - Enterprise-wide ransomware deployment")
        print("  simulate zero_day          - Zero-day exploit in critical infrastructure")
        print("  simulate nation_state      - Nation-state cyber warfare scenario")
        
        print("\n💡 TIPS FOR BETTER ANALYSIS:")
        print("  • Include specific IP addresses, domains, or file hashes for deeper analysis")
        print("  • Mention compliance frameworks (SOX, GDPR, HIPAA, PCI-DSS) for regulatory impact")
        print("  • Specify attack techniques (MITRE ATT&CK TTPs) for threat intelligence correlation")
        print("  • Reference business context (critical systems, data sensitivity) for risk prioritization")
        print("  • Ask for explanations to understand AI decision-making processes")
        
    async def process_analysis(self, query: str):
        if not self.orchestrator:
            print("❌ Orchestrator not available")
            return
            
        print(f"\n🔄 PROCESSING QUERY: {query}")
        print("=" * 60)
        
        try:
            # Show step-by-step execution
            print("📝 Step 1: Intent Parsing...")
            print("   🔗 Calling: IntentParserAgent.parse_intent()")
            print("   🧠 AgentExecutor Chain: Intent Parser → Claude 3 Sonnet")
            
            intent_result = await self.orchestrator.intent_parser.parse_intent(query)
            
            print(f"   ✅ Intent: {intent_result['intent_type']}")
            print(f"   🎯 Agents: {intent_result['required_agents']}")
            print(f"   📊 Confidence: {intent_result['confidence']}")
            
            if intent_result.get('structured_event'):
                event = intent_result['structured_event']
                print(f"   📋 Event: {event.get('event_type', 'N/A')} | {event.get('severity', 'N/A')} | {event.get('protocol', 'N/A')}")
                print(f"   📍 IPs: {event.get('source_ip', 'N/A')} → {event.get('destination_ip', 'N/A')}")
            
            print("\n🤖 Step 2: Agent Execution...")
            
            if intent_result["required_agents"] == ["all"]:
                print("   🔄 Full Multi-Agent Analysis...")
                await self.execute_full_analysis_with_details(intent_result)
            else:
                print(f"   🎯 Selective Agent Execution: {intent_result['required_agents']}")
                await self.execute_selective_analysis_with_details(intent_result)
                
            # Store in history
            self.session_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "intent": intent_result['intent_type'],
                "agents": intent_result['required_agents'],
                "success": True
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.session_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "error": str(e),
                "success": False
            })
    
    async def execute_full_analysis_with_details(self, intent_result: Dict):
        """Execute full analysis with detailed agent call tracking"""
        # Use the extracted structured_event directly from intent_result
        structured_event = intent_result.get("structured_event", {}).copy()
        
        print(f"   📋 Using Event Data: {structured_event}")
        
        results = {
            "intent_analysis": intent_result,
            "network_analysis": {},
            "threat_analysis": {},
            "compliance_impact": {},
            "incident_details": {},
            "forensics_status": {},
            "explainability_report": {},
            "overall_risk_score": 0,
            "recommendations": [],
            "execution_sequence": []
        }
        
        # Network Agent
        print("\n   🌐 NETWORK AGENT:")
        print("      🔗 Calling: NetworkSecurityAgent.assess_network_impact()")
        print("      🧠 AgentExecutor Chain: Network Agent → Claude 3 Sonnet")
        print("      🛠️  Tools: calculate_risk, identify_segments, check_critical_asset")
        try:
            results["network_analysis"] = await self.orchestrator.agents["network"].assess_network_impact(structured_event)
            results["execution_sequence"].append("✅ Network Agent")
            print(f"      ✅ Network Risk: {results['network_analysis'].get('risk_score', 'N/A')}/10")
        except Exception as e:
            print(f"      ❌ Network Agent Error: {e}")
            results["network_analysis"] = {"error": str(e)}
            results["execution_sequence"].append("❌ Network Agent")
        
        # Threat Agent
        print("\n   🎯 THREAT AGENT:")
        print("      🔗 Calling: ThreatDetectionAgent.analyze_threat()")
        print("      🧠 AgentExecutor Chain: Threat Agent → Claude 3 Sonnet")
        print("      🛠️  Tools: classify_threat, calculate_severity, identify_attack_vector")
        try:
            results["threat_analysis"] = await self.orchestrator.agents["threat"].analyze_threat(structured_event)
            results["execution_sequence"].append("✅ Threat Agent")
            print(f"      ✅ Threat: {results['threat_analysis'].get('threat_type', 'N/A')} | Severity: {results['threat_analysis'].get('severity_score', 'N/A')}/10")
        except Exception as e:
            print(f"      ❌ Threat Agent Error: {e}")
            results["threat_analysis"] = {"error": str(e)}
            results["execution_sequence"].append("❌ Threat Agent")
        
        # Compliance Agent
        print("\n   📋 COMPLIANCE AGENT:")
        print("      🔗 Calling: ComplianceAgent.check_compliance_impact()")
        print("      🧠 AgentExecutor Chain: Compliance Agent → Claude 3 Sonnet")
        print("      🛠️  Tools: identify_violations, calculate_compliance_risk, get_affected_frameworks")
        try:
            results["compliance_impact"] = await self.orchestrator.agents["compliance"].check_compliance_impact(structured_event)
            results["execution_sequence"].append("✅ Compliance Agent")
            print(f"      ✅ Compliance Risk: {results['compliance_impact'].get('compliance_risk', 'N/A')}")
        except Exception as e:
            print(f"      ❌ Compliance Agent Error: {e}")
            results["compliance_impact"] = {"error": str(e)}
            results["execution_sequence"].append("❌ Compliance Agent")
        
        # Incident Agent
        print("\n   🚨 INCIDENT AGENT:")
        print("      🔗 Calling: IncidentResponseAgent.create_incident()")
        print("      🧠 AgentExecutor Chain: Incident Agent → Claude 3 Sonnet")
        print("      🛠️  Tools: determine_severity, assign_team, select_playbook")
        try:
            results["incident_details"] = await self.orchestrator.agents["incident"].create_incident(structured_event)
            results["execution_sequence"].append("✅ Incident Agent")
            print(f"      ✅ Incident: {results['incident_details'].get('id', 'N/A')} | {results['incident_details'].get('severity', 'N/A')}")
        except Exception as e:
            print(f"      ❌ Incident Agent Error: {e}")
            results["incident_details"] = {"error": str(e)}
            results["execution_sequence"].append("❌ Incident Agent")
        
        # Forensics Agent
        print("\n   🔍 FORENSICS AGENT:")
        print("      🔗 Calling: ForensicsAgent.collect_evidence()")
        print("      🧠 AgentExecutor Chain: Forensics Agent → Claude 3 Sonnet")
        print("      🛠️  Tools: identify_artifacts, extract_indicators, assess_attribution")
        try:
            results["forensics_status"] = await self.orchestrator.agents["forensics"].collect_evidence(structured_event)
            results["execution_sequence"].append("✅ Forensics Agent")
            print(f"      ✅ Evidence: {results['forensics_status'].get('id', 'N/A')} | {results['forensics_status'].get('preservation_status', 'N/A')}")
        except Exception as e:
            print(f"      ❌ Forensics Agent Error: {e}")
            results["forensics_status"] = {"error": str(e)}
            results["execution_sequence"].append("❌ Forensics Agent")
        
        # Calculate overall risk score
        network_risk = results["network_analysis"].get("risk_score", 0) if "error" not in results["network_analysis"] else 0
        threat_severity = results["threat_analysis"].get("severity_score", 0) if "error" not in results["threat_analysis"] else 0
        results["overall_risk_score"] = max(network_risk, threat_severity)
        
        # Generate recommendations
        if results["overall_risk_score"] >= 8:
            results["recommendations"] = ["Immediate isolation required", "Activate incident response team"]
        elif results["overall_risk_score"] >= 6:
            results["recommendations"] = ["Enhanced monitoring", "Prepare incident response"]
        else:
            results["recommendations"] = ["Continue monitoring", "Review security controls"]
        
        # Explainability Agent
        print("\n   🧠 EXPLAINABILITY AGENT:")
        print("      🔗 Calling: ExplainabilityAgent.explain_decisions()")
        print("      🧠 AgentExecutor Chain: Explainability Agent → Claude 3 Sonnet")
        print("      🛠️  Tools: generate_rationale, justify_risk_scores, explain_actions")
        try:
            results["explainability_report"] = await self.orchestrator.agents["explainability"].explain_decisions(results)
            results["execution_sequence"].append("✅ Explainability Agent")
            print(f"      ✅ Explanation: {results['explainability_report'].get('id', 'N/A')}")
        except Exception as e:
            print(f"      ❌ Explainability Agent Error: {e}")
            results["explainability_report"] = {"error": str(e)}
            results["execution_sequence"].append("❌ Explainability Agent")
        
        self.display_full_results(results)
    
    async def execute_selective_analysis_with_details(self, intent_result: Dict):
        """Execute selective analysis with detailed agent call tracking"""
        results = {
            "intent_analysis": intent_result,
            "agent_results": {},
            "overall_assessment": {},
            "execution_sequence": []
        }
        
        required_agents = intent_result["required_agents"]
        # Use the extracted structured_event directly from intent_result
        structured_event = intent_result.get("structured_event", {}).copy()
        
        print(f"   📋 Using Event Data: {structured_event}")
        
        # Execute selected agents with detailed tracking
        for agent_name in required_agents:
            if agent_name in self.orchestrator.agents:
                print(f"\n   🎯 {agent_name.upper()} AGENT:")
                print(f"      🔗 Calling: {agent_name.title()}Agent")
                print(f"      🧠 AgentExecutor Chain: {agent_name.title()} Agent → Claude 3 Sonnet")
                
                # Show tools for each agent
                tools_map = {
                    "network": "calculate_risk, identify_segments, check_critical_asset",
                    "threat": "classify_threat, calculate_severity, identify_attack_vector",
                    "compliance": "identify_violations, calculate_compliance_risk, get_affected_frameworks",
                    "incident": "determine_severity, assign_team, select_playbook",
                    "forensics": "identify_artifacts, extract_indicators, assess_attribution",
                    "explainability": "generate_rationale, justify_risk_scores, explain_actions"
                }
                print(f"      🛠️  Tools: {tools_map.get(agent_name, 'N/A')}")
                
                try:
                    agent = self.orchestrator.agents[agent_name]
                    
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
                        result = await agent.explain_decisions(results)
                    else:
                        result = {"error": f"Unknown agent: {agent_name}"}
                    
                    results["agent_results"][agent_name] = result
                    results["execution_sequence"].append(f"✅ {agent_name.title()} Agent")
                    print(f"      ✅ {agent_name.title()} Agent: Analysis Complete")
                    
                    # Show key result
                    if agent_name == "network" and "risk_score" in result:
                        print(f"         Risk Score: {result['risk_score']}/10")
                    elif agent_name == "threat" and "severity_score" in result:
                        print(f"         Severity: {result['severity_score']}/10 | Type: {result.get('threat_type', 'N/A')}")
                    elif agent_name == "compliance" and "compliance_risk" in result:
                        print(f"         Compliance Risk: {result['compliance_risk']}")
                    
                except Exception as e:
                    results["agent_results"][agent_name] = {"error": str(e)}
                    results["execution_sequence"].append(f"❌ {agent_name.title()} Agent")
                    print(f"      ❌ {agent_name.title()} Agent Error: {e}")
        
        # Generate overall assessment
        results["overall_assessment"] = self.orchestrator._generate_assessment(results)
        self.display_selective_results(results)
    
    def display_full_results(self, result: Dict[str, Any]):
        print("\n📊 FULL ANALYSIS RESULTS:")
        print("=" * 40)
        
        # Execution Sequence
        if result.get("execution_sequence"):
            print("🔄 Agent Execution Sequence:")
            for i, agent in enumerate(result["execution_sequence"], 1):
                print(f"   {i}. {agent}")
            print()
        
        # Overall Risk
        risk_score = result.get('overall_risk_score', 0)
        print(f"🎯 Overall Risk Score: {risk_score}/10 {self.get_risk_emoji(risk_score)}")
        
        # Network Analysis
        network = result.get('network_analysis', {})
        if network and "error" not in network:
            print(f"🌐 Network Risk: {network.get('risk_score', 'N/A')}/10")
            if network.get('recommended_isolation'):
                print("   ⚠️  Isolation Recommended")
        
        # Threat Analysis  
        threat = result.get('threat_analysis', {})
        if threat and "error" not in threat:
            print(f"🎯 Threat: {threat.get('threat_type', 'Unknown')} | Severity: {threat.get('severity_score', 'N/A')}/10")
            print(f"   Vector: {threat.get('attack_vector', 'N/A')} | Confidence: {threat.get('confidence', 'N/A')}")
        
        # Compliance
        compliance = result.get('compliance_impact', {})
        if compliance and "error" not in compliance:
            print(f"📋 Compliance Risk: {compliance.get('compliance_risk', 'N/A')}")
            violations = compliance.get('violations', [])
            if violations:
                print(f"   ⚠️  {len(violations)} violations detected")
        
        # Incident
        incident = result.get('incident_details', {})
        if incident and "error" not in incident:
            print(f"🚨 Incident: {incident.get('id', 'N/A')} | {incident.get('severity', 'N/A')}")
            print(f"   Team: {incident.get('assigned_team', 'N/A')}")
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
    
    def display_selective_results(self, result: Dict[str, Any]):
        print("\n📊 SELECTIVE ANALYSIS RESULTS:")
        print("=" * 40)
        
        # Execution Sequence
        if result.get("execution_sequence"):
            print("🔄 Agent Execution Sequence:")
            for i, agent in enumerate(result["execution_sequence"], 1):
                print(f"   {i}. {agent}")
            print()
        
        intent = result.get('intent_analysis', {})
        print(f"🎯 Intent: {intent.get('intent_type', 'N/A')} | Confidence: {intent.get('confidence', 'N/A')}")
        
        agent_results = result.get('agent_results', {})
        for agent_name, agent_result in agent_results.items():
            if 'error' in agent_result:
                print(f"❌ {agent_name.title()}: {agent_result['error']}")
            else:
                print(f"✅ {agent_name.title()}: Analysis Complete")
                
                # Show key metrics
                if agent_name == 'network' and 'risk_score' in agent_result:
                    print(f"   Risk Score: {agent_result['risk_score']}/10")
                elif agent_name == 'threat' and 'severity_score' in agent_result:
                    print(f"   Severity: {agent_result['severity_score']}/10 | Type: {agent_result.get('threat_type', 'N/A')}")
                elif agent_name == 'compliance' and 'compliance_risk' in agent_result:
                    print(f"   Compliance Risk: {agent_result['compliance_risk']}")
        
        # Overall Assessment
        assessment = result.get('overall_assessment', {})
        if assessment.get('recommendations'):
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(assessment['recommendations'], 1):
                print(f"   {i}. {rec}")
    
    def simulate_event(self, event_type: str):
        events = {
            'ssh_brute': {
                'query': 'Analyze critical SSH brute force attack from 192.168.1.45 to 10.0.1.100',
                'description': 'Multiple failed SSH login attempts to critical server'
            },
            'sql_injection': {
                'query': 'Investigate SQL injection attack on web server 10.0.2.50',
                'description': 'SQL injection attempts detected on web application'
            },
            'malware': {
                'query': 'Analyze malware threat: trojan communicating with C&C server 8.8.8.8',
                'description': 'Trojan malware communication to external command server'
            },
            'data_breach': {
                'query': 'Investigate data exfiltration from 10.0.1.75 to 185.199.108.153',
                'description': 'Large data transfer to external cloud storage detected'
            },
            'apt_campaign': {
                'query': 'Analyze sophisticated APT campaign with multi-stage attack from nation-state actor targeting critical infrastructure via spear phishing and lateral movement',
                'description': 'Advanced Persistent Threat multi-stage attack campaign'
            },
            'insider_threat': {
                'query': 'Investigate malicious insider threat involving privileged user accessing sensitive financial data outside normal business hours and copying to external USB device',
                'description': 'Malicious insider data exfiltration scenario'
            },
            'supply_chain': {
                'query': 'Assess supply chain compromise affecting software distribution pipeline with malicious code injection in trusted vendor update mechanism',
                'description': 'Software supply chain compromise attack'
            },
            'ransomware': {
                'query': 'Respond to enterprise-wide ransomware deployment with file encryption, shadow copy deletion, and network share propagation across 5000+ endpoints',
                'description': 'Large-scale ransomware deployment scenario'
            },
            'zero_day': {
                'query': 'Analyze zero-day exploit targeting critical infrastructure SCADA systems with custom malware designed for industrial control system manipulation',
                'description': 'Zero-day exploit in critical infrastructure'
            },
            'nation_state': {
                'query': 'Coordinate response to nation-state cyber warfare campaign targeting government networks with advanced evasion techniques and persistent access mechanisms',
                'description': 'Nation-state cyber warfare scenario'
            }
        }
        
        if event_type not in events:
            print(f"❌ Unknown event type. Available: {', '.join(events.keys())}")
            return
        
        event = events[event_type]
        print(f"\n🎭 SIMULATING: {event['description']}")
        return event['query']
    
    def display_history(self):
        if not self.session_history:
            print("\n📝 No session history available")
            return
            
        print(f"\n📝 SESSION HISTORY ({len(self.session_history)} queries):")
        print("=" * 60)
        
        for i, entry in enumerate(self.session_history[-10:], 1):  # Show last 10
            timestamp = entry['timestamp'][:19].replace('T', ' ')
            status = "✅" if entry['success'] else "❌"
            print(f"{i:2d}. {status} {timestamp} | {entry.get('intent', 'N/A')}")
            print(f"    Query: {entry['query'][:60]}...")
            if not entry['success']:
                print(f"    Error: {entry.get('error', 'Unknown')}")
            print()
    
    def get_risk_emoji(self, score: int) -> str:
        if score >= 8:
            return "🔴"
        elif score >= 6:
            return "🟡"
        else:
            return "🟢"
    
    async def run(self):
        self.display_banner()
        
        if not ORCHESTRATOR_AVAILABLE:
            print("❌ Orchestrator not available. Exiting...")
            return
        
        print("🚀 Console ready! Type 'help' for commands or 'exit' to quit.")
        
        while True:
            try:
                self.display_menu()
                user_input = input("\n🛡️  Enter command: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    print("\n👋 Goodbye! Stay secure!")
                    break
                    
                elif user_input.lower() == 'help':
                    self.display_help()
                    
                elif user_input.lower() == 'history':
                    self.display_history()
                    
                elif user_input.startswith('analyze '):
                    query = user_input[8:].strip()
                    if query:
                        await self.process_analysis(query)
                    else:
                        print("❌ Please provide a query after 'analyze'")
                        
                elif user_input.startswith('simulate '):
                    event_type = user_input[9:].strip()
                    if event_type:
                        query = self.simulate_event(event_type)
                        if query:
                            await self.process_analysis(query)
                    else:
                        print("❌ Please specify event type after 'simulate'")
                        
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Stay secure!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

async def main():
    console = SecurityConsole()
    await console.run()

if __name__ == "__main__":
    asyncio.run(main())