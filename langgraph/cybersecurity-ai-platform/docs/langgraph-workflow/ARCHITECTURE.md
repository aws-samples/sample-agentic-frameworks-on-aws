# Cybersecurity AI Platform - Agentic Architecture Documentation

## Overview

This document describes the architecture of a cloud-native cybersecurity management platform that uses **LangGraph multi-agent workflows** with **AWS Bedrock Claude AI** to emulate Network Engineer decision-making processes.

## Architecture Diagrams

### 1. Enhanced LangGraph Workflow
![Enhanced LangGraph Workflow](./enhanced_langgraph_workflow.png)

## Agentic Framework

### Multi-Agent System Design

The platform implements a **LangGraph-based multi-agent system** with 6 specialized AI agents:

| Agent | Role | AI Model | Tools | Responsibility |
|-------|------|----------|-------|----------------|
| **Network Security Agent** | Network Engineer | Claude-3-Sonnet | `calculate_risk`, `identify_segments`, `check_critical_asset` | Network topology analysis, device configuration, risk assessment |
| **Threat Detection Agent** | Security Analyst | Claude-3-Sonnet | `classify_threat`, `calculate_severity`, `identify_attack_vector` | Threat intelligence, IOC correlation, attack pattern analysis |
| **Compliance Agent** | Compliance Officer | Claude-3-Sonnet | `identify_violations`, `calculate_compliance_risk`, `get_affected_frameworks` | Regulatory compliance (SOC2, PCI-DSS, NIST, ISO27001) |
| **Incident Response Agent** | Incident Coordinator | Claude-3-Sonnet | `determine_severity`, `select_playbook`, `assign_team` | Incident creation, response coordination, playbook execution |
| **Digital Forensics Agent** | Forensics Investigator | Claude-3-Sonnet | `identify_artifacts`, `extract_indicators`, `assess_attribution` | Evidence collection, artifact analysis, threat attribution |
| **Explainability Agent** | AI Transparency Specialist | Claude-3-Sonnet | `generate_rationale`, `justify_risk_scores`, `explain_actions` | Decision justification, audit trails, compliance explanations |

### LangGraph Orchestration

#### State Management
```python
class SecurityState(TypedDict):
    event: Dict                 # Input security event
    network_analysis: Dict      # Network agent results
    threat_analysis: Dict       # Threat agent results  
    compliance_analysis: Dict   # Compliance agent results
    incident_created: Dict      # Incident response results
    forensics_evidence: Dict    # Forensics collection results
    explainability_report: Dict # Decision explanations and justifications
    final_response: Dict        # Synthesized response
    next_action: str           # Workflow control
```

#### Workflow Logic
1. **Sequential Processing**: Network → Threat → Compliance analysis
2. **Conditional Branching**: Create incident if risk ≥ 7 OR compliance violations > 0
3. **Parallel Execution**: Incident response + Forensics collection
4. **Explainability Analysis**: Generate decision justifications and audit trails
5. **Final Synthesis**: Aggregate results with explanations and generate recommendations

## Technical Architecture

### Core Components

#### 1. API Layer (FastAPI)
- **Endpoints**: `/security/analyze`, `/incident/create`, `/forensics/collect`
- **Authentication**: JWT-based security
- **Rate Limiting**: Redis-backed throttling
- **Validation**: Pydantic models

#### 2. LangGraph Orchestrator
- **Framework**: LangGraph StateGraph
- **Pattern**: ReAct (Reasoning + Acting)
- **State Persistence**: Shared state across agents
- **Error Handling**: Graceful failure recovery

#### 3. AI Agents (AWS Bedrock)
- **LLM**: Anthropic Claude-3-Sonnet
- **Integration**: LangChain + AWS Bedrock
- **Tools**: Custom domain-specific functions
- **Prompting**: Role-based system prompts

#### 4. Data Layer
- **Database**: PostgreSQL (incident data, configurations)
- **Cache**: Redis (session state, rate limiting)
- **Storage**: S3 (evidence, logs, artifacts)
- **Monitoring**: CloudWatch + Prometheus

### Security Event Processing Flow

```mermaid
graph TD
    A[Security Event] --> B[Network Analysis]
    B --> C[Threat Analysis]
    C --> D[Compliance Check]
    D --> E{Risk >= 7?}
    E -->|Yes| F[Create Incident]
    E -->|No| G[Explainability Analysis]
    F --> H[Collect Evidence]
    H --> G[Explainability Analysis]
    G --> I[Final Synthesis]
    I --> J[Security Response + Audit Trail]
```

### Agent Tool Specifications

#### Explainability Agent Tools
```python
tools = [
    Tool(name="generate_rationale",
         description="Generate human-readable rationale for security decisions",
         func=lambda result: str(self._generate_rationale(eval(result)))),
    Tool(name="justify_risk_scores",
         description="Justify risk score calculations with detailed breakdown", 
         func=lambda result: str(self._justify_risk_scores(eval(result)))),
    Tool(name="explain_actions",
         description="Explain why specific security actions were recommended",
         func=lambda result: str(self._explain_actions(eval(result))))
]
```

#### Network Security Agent Tools
```python
tools = [
    Tool(name="calculate_risk", 
         description="Calculate network risk score for IP addresses and protocols",
         func=lambda query: str(self._calculate_network_risk(*query.split(",")))),
    Tool(name="identify_segments",
         description="Identify network segments affected by IPs", 
         func=lambda query: str(self._identify_network_segments(*query.split(",")))),
    Tool(name="check_critical_asset",
         description="Check if IP is a critical network asset",
         func=lambda ip: str(self._is_critical_asset(ip)))
]
```

#### Threat Detection Agent Tools
```python
tools = [
    Tool(name="classify_threat",
         description="Classify threat type based on event characteristics",
         func=lambda event: self._classify_threat(eval(event))),
    Tool(name="calculate_severity", 
         description="Calculate threat severity score from 1-10",
         func=lambda data: str(self._calculate_severity(*data.split(",")))),
    Tool(name="identify_attack_vector",
         description="Identify the attack vector used",
         func=lambda event: self._identify_attack_vector(eval(event)))
]
```

## Deployment Architecture

### Cloud-Native Infrastructure

#### Container Orchestration
```yaml
# docker-compose.yml
services:
  cybersec-platform:
    build: .
    ports: ["8000:8000"]
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/cybersec
    depends_on: [redis, postgres]
  
  redis:
    image: redis:7-alpine
    
  postgres:
    image: postgres:15-alpine
    
  prometheus:
    image: prom/prometheus:latest
```

#### AWS Services Integration
- **Bedrock**: Claude-3-Sonnet LLM hosting
- **VPC**: Network isolation and security
- **RDS**: Managed PostgreSQL database
- **ElastiCache**: Managed Redis cluster
- **S3**: Evidence and artifact storage
- **CloudWatch**: Monitoring and logging

### Scalability Considerations

#### Horizontal Scaling
- **API Layer**: Load balancer + multiple FastAPI instances
- **Agent Processing**: Async execution with connection pooling
- **Database**: Read replicas for query distribution
- **Cache**: Redis cluster for high availability

#### Performance Optimization
- **Connection Pooling**: Database and Bedrock connections
- **Caching Strategy**: Agent results and configuration data
- **Async Processing**: Non-blocking I/O operations
- **Batch Processing**: Multiple events in single workflow

## Security & Compliance

### Security Measures
- **Authentication**: JWT tokens with role-based access
- **Encryption**: TLS 1.3 for data in transit, AES-256 for data at rest
- **Network Security**: VPC isolation, security groups, NACLs
- **Secrets Management**: AWS Secrets Manager integration

### Compliance Framework Support
- **SOC2 Type II**: Access controls, monitoring, incident response
- **PCI-DSS**: Data protection, network security, vulnerability management
- **NIST Cybersecurity Framework**: Identify, Protect, Detect, Respond, Recover
- **ISO 27001**: Information security management system

## Monitoring & Observability

### Metrics Collection
- **Application Metrics**: Request latency, error rates, throughput
- **Agent Metrics**: Processing time, success rates, tool usage
- **Infrastructure Metrics**: CPU, memory, network, storage
- **Business Metrics**: Incident response time, threat detection accuracy

### Alerting Strategy
- **Critical Alerts**: System failures, security breaches
- **Warning Alerts**: Performance degradation, capacity thresholds
- **Info Alerts**: Successful incident resolution, compliance updates

## API Reference

### Core Endpoints

#### Analyze Security Event
```http
POST /security/analyze
Content-Type: application/json

{
  "event_type": "intrusion",
  "severity": "high",
  "source_ip": "192.168.1.45",
  "destination_ip": "10.0.1.100", 
  "protocol": "SSH",
  "description": "Failed login attempts"
}
```

#### Create Incident
```http
POST /incident/create
Content-Type: application/json

{
  "event_type": "security_breach",
  "severity": "critical",
  "source_ip": "external_ip",
  "description": "Malware detected"
}
```

#### Collect Evidence
```http
POST /forensics/collect
Content-Type: application/json

{
  "event_type": "data_exfiltration", 
  "source_ip": "compromised_host",
  "description": "Suspicious file transfers"
}
```

#### Explain Decisions
```http
POST /explain/decisions
Content-Type: application/json

{
  "overall_risk_score": 9,
  "network_analysis": {...},
  "threat_analysis": {...},
  "recommendations": [...]
}
```

#### Generate Audit Report
```http
GET /audit/report/EXP-001,EXP-002
```

## Future Enhancements

### Planned Features
1. **Real-time Threat Hunting**: Proactive threat detection using ML models
2. **Automated Remediation**: Self-healing security responses
3. **Multi-tenant Architecture**: Support for multiple organizations
4. **Advanced Analytics**: Threat trend analysis and predictive modeling
5. **Integration Hub**: SIEM, SOAR, and security tool integrations

### Scalability Roadmap
1. **Kubernetes Migration**: Container orchestration at scale
2. **Microservices Architecture**: Service decomposition for better scalability
3. **Event Streaming**: Apache Kafka for real-time event processing
4. **Global Deployment**: Multi-region disaster recovery

---

## Quick Start

### Prerequisites
- AWS Account with Bedrock access
- Docker and Docker Compose
- Python 3.11+

### Installation
```bash
# Clone repository
git clone <repository-url>
cd cybersec-platform

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials

# Deploy with Docker Compose
docker-compose up -d

# Access API documentation
open http://localhost:8000/docs
```

### Testing
```bash
# Run agent tests
python3 examples/langgraph-workflow/test_langgraph.py

# Test API endpoints
curl -X POST http://localhost:8000/security/analyze \
  -H "Content-Type: application/json" \
  -d '{"event_type":"intrusion","severity":"high","source_ip":"192.168.1.45","destination_ip":"10.0.1.100","protocol":"SSH","description":"Failed login attempts"}'
```

This architecture provides a robust, scalable, and intelligent cybersecurity management platform that leverages the power of AI agents to automate and enhance security operations.