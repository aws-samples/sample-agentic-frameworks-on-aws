# Intent-Based Cybersecurity Analysis Platform

## 🎯 Overview

This implementation uses **Intent Classification** with **Sequential Agent Orchestration** to provide intelligent cybersecurity analysis. Unlike the LangGraph approach, this system uses natural language processing to determine which security agents to execute based on user intent.

## 🏗️ Architecture

### Core Components

1. **Intent Parser Agent** - Classifies user queries and routes to appropriate agents
2. **Intelligent Orchestrator** - Manages sequential agent execution
3. **Specialized Security Agents** - Network, Threat, Compliance, Incident, Forensics, Explainability
4. **Interactive Console** - Real-time analysis with step-by-step visibility

### Key Features

- ✅ **Natural Language Processing** - Understands security queries in plain English
- ✅ **Selective Agent Execution** - Only runs necessary agents for efficiency
- ✅ **Real-time Visibility** - Shows each AgentExecutor chain execution
- ✅ **Error Resilience** - Individual agent failures don't break workflow
- ✅ **Interactive Console** - Terminal-based UI with command support

## 🔄 Workflow Process

### 1. Intent Classification
```
User Query → Intent Parser → Agent Routing Decision
```

### 2. Agent Execution Patterns

#### Selective Execution (Efficient)
```
"Check network security" → Network Agent Only
"SQL injection attack" → Threat Agent Only  
"Compliance implications" → Compliance Agent Only
```

#### Full Analysis (Comprehensive)
```
"Analyze critical security event" → All 6 Agents Sequential
```

### 3. AgentExecutor Chains

Each agent runs its own LangChain AgentExecutor:
- **Intent Parser Chain** → Claude 3 Sonnet + Intent Tools
- **Network Agent Chain** → Claude 3 Sonnet + Network Tools
- **Threat Agent Chain** → Claude 3 Sonnet + Threat Tools
- **Compliance Chain** → Claude 3 Sonnet + Compliance Tools
- **Incident Chain** → Claude 3 Sonnet + Incident Tools
- **Forensics Chain** → Claude 3 Sonnet + Forensics Tools
- **Explainability Chain** → Claude 3 Sonnet + Explanation Tools

## 🚀 Usage

### Launch Interactive Console
```bash
cd /Users/aboavent/Downloads/cisco
source venv/bin/activate
python3 examples/intent-classifier/interactive_security_console.py
```

### Available Commands

#### Natural Language Analysis
```
analyze Check network security for IP 192.168.1.45
analyze SQL injection attack on web server
analyze What are compliance implications of data breach?
analyze Create incident for SSH brute force attack
analyze Explain why risk score is high
```

#### Event Simulation
```
simulate ssh_brute      # SSH brute force attack
simulate sql_injection  # SQL injection on web server
simulate malware        # Malware C&C communication
simulate data_breach    # Data exfiltration event
```

#### Utility Commands
```
history                 # View session history
help                   # Show detailed help
exit                   # Exit console
```

## 📊 Example Execution Flow

### Query: "Check network security for IP 192.168.1.45"

```
📝 Step 1: Intent Parsing...
   🔗 Calling: IntentParserAgent.parse_intent()
   🧠 AgentExecutor Chain: Intent Parser → Claude 3 Sonnet
   ✅ Intent: network_analysis
   🎯 Agents: ['network']
   📊 Confidence: 0.8

🤖 Step 2: Agent Execution...
   🎯 Selective Agent Execution: ['network']

   🌐 NETWORK AGENT:
      🔗 Calling: NetworkSecurityAgent.assess_network_impact()
      🧠 AgentExecutor Chain: Network Agent → Claude 3 Sonnet
      🛠️  Tools: calculate_risk, identify_segments, check_critical_asset
      ✅ Network Agent: Analysis Complete
         Risk Score: 5/10

📊 SELECTIVE ANALYSIS RESULTS:
🎯 Intent: network_analysis | Confidence: 0.8
✅ Network: Analysis Complete
   Risk Score: 5/10
```

## 🔧 Technical Implementation

### Intent Classification Logic
- **Pattern Matching** - Keywords and phrases identify intent
- **Event Extraction** - IPs, protocols, severity from natural language
- **Agent Routing** - Maps intent to required security agents
- **Confidence Scoring** - Measures classification certainty

### Agent Tools by Category

#### Network Agent Tools
- `calculate_risk` - Network risk assessment
- `identify_segments` - Network segment identification
- `check_critical_asset` - Critical asset verification

#### Threat Agent Tools
- `classify_threat` - Threat type classification
- `calculate_severity` - Threat severity scoring
- `identify_attack_vector` - Attack vector identification

#### Compliance Agent Tools
- `identify_violations` - Policy violation detection
- `calculate_compliance_risk` - Compliance risk assessment
- `get_affected_frameworks` - Framework impact analysis

#### Incident Agent Tools
- `determine_severity` - Incident severity assessment
- `assign_team` - Response team assignment
- `select_playbook` - Playbook selection

#### Forensics Agent Tools
- `identify_artifacts` - Digital artifact identification
- `extract_indicators` - IOC extraction
- `assess_attribution` - Threat actor attribution

#### Explainability Agent Tools
- `generate_rationale` - Decision rationale generation
- `justify_risk_scores` - Risk score justification
- `explain_actions` - Action explanation

## 🎯 Benefits vs LangGraph Approach

### Intent Classifier Advantages
- ✅ **Efficiency** - Only runs necessary agents
- ✅ **Natural Language** - Understands plain English queries
- ✅ **Error Isolation** - Agent failures don't cascade
- ✅ **Simplicity** - Sequential execution is predictable
- ✅ **Debugging** - Clear execution path visibility

### When to Use This Approach
- **Interactive Analysis** - Real-time security queries
- **Selective Processing** - Don't need full workflow every time
- **Natural Language Interface** - Security teams prefer plain English
- **Error Resilience** - Production environments requiring stability
- **Resource Efficiency** - Cost-conscious deployments

## 📁 File Structure

```
examples/intent-classifier/
├── interactive_security_console.py    # Main console application

core/
├── intelligent_orchestrator.py        # Intent-based orchestration
├── bedrock_client.py                 # AWS Bedrock integration

agents/
├── intent_parser_agent.py           # Intent classification
├── network_agent.py                 # Network security analysis
├── threat_agent.py                  # Threat detection
├── compliance_agent.py              # Compliance checking
├── incident_agent.py                # Incident response
├── forensics_agent.py               # Digital forensics
└── explainability_agent.py          # Decision explanation
```

This intent-based approach provides a more natural and efficient way to interact with the cybersecurity analysis platform while maintaining the power of multi-agent AI intelligence.