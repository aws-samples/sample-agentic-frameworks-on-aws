# Cybersecurity AI Platform with Multi-Agent Intelligence

An enterprise-grade cybersecurity analysis platform leveraging AWS Bedrock and Claude 3 Sonnet with two distinct multi-agent orchestration approaches: Intent-Based Classification and LangGraph Workflows.

## 🏗️ Architecture Overview

This platform demonstrates two different approaches to multi-agent AI orchestration for cybersecurity analysis:

1. **Intent-Based Classification** - Natural language processing with selective agent execution
2. **LangGraph Workflows** - Graph-based state management with comprehensive analysis

Both implementations use 6 specialized AI agents powered by AWS Bedrock Claude 3 Sonnet.

## 🤖 AI Agents

| Agent | Purpose | Tools | Responsibility |
|-------|---------|-------|----------------|
| **Network Security** | Network risk assessment | `calculate_risk`, `identify_segments`, `check_critical_asset` | Network topology analysis, segmentation, isolation recommendations |
| **Threat Detection** | Threat analysis & classification | `classify_threat`, `calculate_severity`, `identify_attack_vector` | IOC correlation, attack pattern analysis, threat intelligence |
| **Compliance** | Regulatory compliance checking | `identify_violations`, `calculate_compliance_risk`, `get_affected_frameworks` | SOC2, PCI-DSS, NIST, ISO27001 compliance assessment |
| **Incident Response** | Incident management | `determine_severity`, `assign_team`, `select_playbook` | Incident creation, response coordination, playbook execution |
| **Digital Forensics** | Evidence collection | `identify_artifacts`, `extract_indicators`, `assess_attribution` | Artifact analysis, IOC extraction, threat attribution |
| **Explainability** | AI decision transparency | `generate_rationale`, `justify_risk_scores`, `explain_actions` | Decision justification, audit trails, compliance explanations |

## 🚀 Quick Start

### Prerequisites

- AWS Account with Bedrock access
- Python 3.11+
- AWS CLI configured

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aws-samples/3P-Agentic-Frameworks.git
cd 3P-Agentic-Frameworks/cybersecurity-ai-platform
```

2. **Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

4. **Enable AWS Bedrock models**
   - Go to AWS Bedrock console
   - Enable Claude 3 Sonnet model access

### Usage

#### Intent-Based Interactive Console
```bash
python3 examples/intent-classifier/interactive_security_console.py
```

**Example Commands:**
```bash
# Network security analysis
analyze Assess network risk for lateral movement from DMZ host 192.168.1.45 to critical database server 10.0.1.100 via SSH

# Advanced threat analysis  
analyze Deep dive into APT campaign indicators: C2 beaconing from 10.0.3.45 to suspicious domain malware-c2.example.com

# Compliance assessment
analyze Evaluate GDPR compliance impact of data exfiltration incident affecting EU customer PII database

# Event simulation
simulate apt_campaign
simulate ransomware
```

#### LangGraph Workflow Testing
```bash
python3 examples/langgraph-workflow/test_multiple_scenarios.py
```

## 📊 Implementation Comparison

| Feature | Intent Classifier | LangGraph Workflow |
|---------|------------------|-------------------|
| **Interface** | Interactive Console | Batch Processing |
| **Execution** | Selective Agents | All Agents Always |
| **Input** | Natural Language | Structured Events |
| **Efficiency** | High (targeted) | Lower (comprehensive) |
| **User Experience** | Excellent | Good |
| **Error Handling** | Resilient | Complex |
| **Use Case** | Interactive Analysis | Comprehensive Workflows |

## 🔧 Configuration

### AWS Bedrock Setup

1. **Enable Model Access**
   - Navigate to AWS Bedrock Console
   - Go to "Model access" 
   - Enable "Claude 3 Sonnet" model

2. **IAM Permissions**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
        }
    ]
}
```

### Environment Variables
```bash
# Required
export AWS_DEFAULT_REGION=us-east-1

# Optional - if not using AWS CLI profiles
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 📁 Project Structure

```
cybersecurity-ai-platform/
├── agents/                     # AI agent implementations
│   ├── network_agent.py       # Network security analysis
│   ├── threat_agent.py        # Threat detection & classification
│   ├── compliance_agent.py    # Compliance checking
│   ├── incident_agent.py      # Incident response
│   ├── forensics_agent.py     # Digital forensics
│   ├── explainability_agent.py # Decision explanation
│   └── intent_parser_agent.py # Intent classification
├── core/                       # Core orchestration
│   ├── bedrock_client.py      # AWS Bedrock integration
│   ├── intelligent_orchestrator.py # Intent-based orchestration
│   └── langgraph_orchestrator.py   # LangGraph workflow
├── examples/                   # Usage examples
│   ├── intent-classifier/     # Interactive console
│   └── langgraph-workflow/    # Workflow examples
├── docs/                       # Documentation
│   ├── intent-classifier/     # Intent approach docs
│   └── langgraph-workflow/    # LangGraph approach docs
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎯 Use Cases

### Intent-Based Classification
- **Interactive Security Analysis** - Real-time threat investigation
- **SOC Analyst Workflows** - Natural language security queries  
- **Executive Briefings** - AI-explained security decisions
- **Compliance Audits** - Regulatory impact assessment

### LangGraph Workflows
- **Automated Incident Response** - Comprehensive event processing
- **Threat Hunting Campaigns** - Systematic threat analysis
- **Forensic Investigations** - Evidence collection workflows
- **Compliance Reporting** - Structured regulatory assessments

## 🔒 Security Considerations

- **AWS IAM** - Least privilege access to Bedrock
- **Data Privacy** - No sensitive data stored or logged
- **Audit Trails** - Complete decision transparency
- **Compliance** - SOC2, PCI-DSS, NIST, ISO27001 alignment

## 📈 Performance & Costs

### Intent-Based Approach
- **Selective Execution**: 60-80% faster than full analysis
- **Cost Optimization**: 40-60% lower Bedrock API costs
- **Response Time**: Sub-second for single agent queries

### LangGraph Approach  
- **Comprehensive Analysis**: Complete security assessment
- **Parallel Processing**: Efficient when all agents needed
- **Resource Usage**: Higher but thorough

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See `docs/` directory for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **AWS Support**: For Bedrock-specific issues, contact AWS Support

## 🏷️ Tags

`aws-bedrock` `claude-3` `langchain` `langgraph` `cybersecurity` `multi-agent` `ai` `security-analysis` `threat-detection` `compliance`