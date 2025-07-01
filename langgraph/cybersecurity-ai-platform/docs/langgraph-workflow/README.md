# Cloud-Native Cybersecurity Management Platform

AI-powered cybersecurity platform with **LangChain agentic workflows** using **AWS Bedrock with Anthropic Claude** that emulate Network Engineers.

## Agentic Framework

**LangGraph Multi-Agent Workflow** with AWS Bedrock Claude-3-Sonnet:
- **Network Security Agent**: Network engineer AI with topology analysis tools
- **Threat Detection Agent**: Cybersecurity analyst AI with threat intelligence tools  
- **Compliance Agent**: Compliance officer AI with regulatory framework tools
- **Incident Response Agent**: Incident coordinator AI with response playbooks
- **Digital Forensics Agent**: Forensics investigator AI with evidence collection tools
- **Explainability Agent**: AI transparency specialist for decision justification
- **LangGraph Orchestrator**: State-based workflow coordination with conditional logic

## AI Architecture

- **LLM**: Anthropic Claude-3-Sonnet via AWS Bedrock
- **Framework**: LangChain ReAct agents with custom tools
- **Pattern**: Multi-agent system with specialized domain expertise

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose
docker-compose up -d

# Access API at http://localhost:8000
```

## API Endpoints

- `POST /security/analyze` - Analyze security events
- `POST /network/configure` - Configure network devices
- `GET /threats/active` - Get active threats
- `GET /compliance/status` - Get compliance status

## Architecture

The platform uses AI agents that emulate network engineer workflows:

1. **Event Analysis**: Multi-agent analysis of security events
2. **Risk Assessment**: Network impact and compliance risk evaluation  
3. **Automated Response**: AI-generated mitigation actions
4. **Compliance Monitoring**: Continuous compliance status tracking

## Monitoring

- Prometheus metrics at http://localhost:9090
- Application logs in `/logs` directory