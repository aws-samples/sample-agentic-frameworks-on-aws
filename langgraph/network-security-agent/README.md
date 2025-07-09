# Network Security Analysis Agent

An LLM-powered network security agent that analyzes network logs and identifies potential threats using Amazon Bedrock with Anthropic Claude.

## 📁 Project Structure

```
network-agent/
├── agents/
│   ├── bedrock/                    # Production Bedrock agents
│   │   ├── bedrock_agent_with_tools.py    # Full agent with LangChain tools
│   │   └── bedrock_network_agent.py       # Basic Bedrock + LangChain agent
│   └── demo/                       # Demo versions (no AWS required)
│       ├── demo_agent_with_tools.py       # Demo with simulated tools
│       └── demo_bedrock_agent.py          # Demo Bedrock simulation
├── data/
│   └── network_logs.csv           # Sample network data
├── docs/
│   ├── README.md                  # Detailed documentation
│   └── network_security_analysis.ipynb   # Jupyter analysis notebook
├── setup/
│   ├── requirements.txt           # Python dependencies
│   └── setup_bedrock_agent.py     # Setup and installation script
└── README.md                      # This file
```

## 🚀 Quick Start

### Option 1: Demo Mode (No AWS Required)
```bash
cd agents/demo
python3 demo_agent_with_tools.py
```

### Option 2: Full Bedrock Integration
```bash
# 1. Install dependencies
cd setup
python3 setup_bedrock_agent.py

# 2. Configure AWS credentials
aws configure

# 3. Run the agent
cd ../agents/bedrock
python3 bedrock_agent_with_tools.py
```

## 🎯 Agent Types

### Production Agents (`agents/bedrock/`)

**`bedrock_agent_with_tools.py`** - **COMPREHENSIVE IMPLEMENTATION**
- Full Amazon Bedrock + LangChain integration
- Advanced tool system with 6 specialized analysis tools
- Real-time network analysis capabilities
- Professional security reporting

**`bedrock_network_agent.py`** - **CORE IMPLEMENTATION**
- Amazon Bedrock + LangChain integration
- Statistical analysis and threat detection
- Comprehensive security reporting

### Demo Agents (`agents/demo/`)

**`demo_agent_with_tools.py`** - **TOOLS DEMONSTRATION**
- Shows how tools work without AWS
- Simulates Claude's analytical process
- Perfect for understanding the system

**`demo_bedrock_agent.py`** - **BEDROCK SIMULATION**
- Demonstrates Bedrock agent output
- No AWS credentials required
- Shows expected analysis quality

## 🛠️ Available Tools (bedrock_agent_with_tools.py)

1. **get_top_data_transfers** - Identify potential data exfiltration
2. **check_port_scanning** - Detect reconnaissance behavior
3. **check_suspicious_ports** - Flag malicious port usage
4. **analyze_protocol_distribution** - Find protocol anomalies
5. **get_high_volume_ips** - Identify compromised endpoints
6. **analyze_temporal_patterns** - Detect coordinated attacks

## 📊 Key Features

- **LLM-Powered Analysis**: Uses Claude-3 Sonnet for expert-level insights
- **Tool Integration**: Specialized tools for different threat types
- **Comprehensive Reporting**: Professional security assessments
- **Flexible Deployment**: Demo and production versions
- **AWS Integration**: Full Bedrock and LangChain support

## 🔧 Requirements

- Python 3.8+
- AWS Account with Bedrock access (for production agents)
- Claude model access in Bedrock
- Network logs in CSV format

See the [Installation Guide](INSTALLATION.md) for detailed setup instructions.

## 📖 Documentation

- **[Comprehensive Guide](docs/README.md)** - Detailed documentation and architecture overview
- **[Installation Guide](INSTALLATION.md)** - Step-by-step setup instructions
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Contributing Guide](CONTRIBUTING.md)** - Development and contribution guidelines
- **[Jupyter Notebook](docs/network_security_analysis.ipynb)** - Data exploration examples

## 🎛️ Customization

Each agent can be customized for specific threat patterns, detection thresholds, and reporting requirements. See the [API Reference](API_REFERENCE.md) for configuration options and the [Contributing Guide](CONTRIBUTING.md) for development guidelines.