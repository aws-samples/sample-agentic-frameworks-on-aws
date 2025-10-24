import os
from strands.multiagent.a2a import A2AServer
from src.agent import weather_agent
import uvicorn
from fastapi import FastAPI
import logging
import sys
import os
# Configure logging
logging.basicConfig(
    level=logging.DEBUG if (os.getenv("DEBUG", "").lower() in ("1", "true", "yes")) else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)

def run_a2a_server():
    """Start the A2A server"""
    host = os.getenv("A2A_HOST", "0.0.0.0")
    port = int(os.getenv("A2A_PORT", "9000"))
    http_url = os.getenv("A2A_URL", os.getenv("AGENTCORE_RUNTIME_URL", f"http://localhost:{port}"))
    agent = weather_agent()
    app = FastAPI()
    @app.get("/ping")
    def ping():
        return {"status": "healthy"}
    a2a_server = A2AServer(
        agent=agent,
        port=port,
        host=host,
        http_url=http_url,
        serve_at_root=True  # Serves locally at root (/) regardless of remote URL path complexity
    )
    app.mount("/", a2a_server.to_fastapi_app())
    logger.info(f"A2A AgentCard on http://localhost:{port}/.well-known/agent-card.json")
    logger.info(f"A2A Server available on http_url:{http_url}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_a2a_server()
