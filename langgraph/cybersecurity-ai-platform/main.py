import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from agents.network_agent import NetworkSecurityAgent
from agents.threat_agent import ThreatDetectionAgent
from agents.compliance_agent import ComplianceAgent
from core.langgraph_orchestrator import LangGraphOrchestrator

app = FastAPI(title="CyberSec AI Platform", version="1.0.0")

class SecurityEvent(BaseModel):
    event_type: str
    severity: str
    source_ip: str
    destination_ip: str
    protocol: str
    description: str

class NetworkConfig(BaseModel):
    device_type: str
    ip_address: str
    config_changes: Dict

orchestrator = LangGraphOrchestrator()

@app.post("/security/analyze")
async def analyze_security_event(event: SecurityEvent):
    """Analyze security event using AI agents"""
    result = await orchestrator.process_security_event(event.dict())
    return {"analysis": result, "recommendations": result.get("actions", [])}

@app.post("/network/configure")
async def configure_network_device(config: NetworkConfig, background_tasks: BackgroundTasks):
    """Configure network device through AI agent"""
    background_tasks.add_task(orchestrator.network_agent.configure_device, config.dict())
    return {"status": "Configuration initiated", "device": config.ip_address}

@app.get("/threats/active")
async def get_active_threats():
    """Get current active threats"""
    threats = await orchestrator.threat_agent.get_active_threats()
    return {"threats": threats, "count": len(threats)}

@app.get("/compliance/status")
async def get_compliance_status():
    """Get compliance status across infrastructure"""
    status = await orchestrator.compliance_agent.get_compliance_status()
    return {"compliance": status}

@app.post("/incident/create")
async def create_incident(event: SecurityEvent):
    """Create security incident"""
    incident = await orchestrator.incident_agent.create_incident(event.dict())
    return {"incident": incident}

@app.post("/forensics/collect")
async def collect_evidence(event: SecurityEvent):
    """Collect digital evidence"""
    evidence = await orchestrator.forensics_agent.collect_evidence(event.dict())
    return {"evidence": evidence}

@app.post("/explain/decisions")
async def explain_decisions(workflow_result: dict):
    """Explain AI security decisions"""
    explanation = await orchestrator.explainability_agent.explain_decisions(workflow_result)
    return {"explanation": explanation}

@app.get("/audit/report/{decision_ids}")
async def generate_audit_report(decision_ids: str):
    """Generate audit report for compliance"""
    ids = decision_ids.split(",")
    report = await orchestrator.explainability_agent.generate_audit_report(ids)
    return {"audit_report": report}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)