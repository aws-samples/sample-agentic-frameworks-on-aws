import os
from strands.multiagent.a2a import A2AServer
from src.agent import weather_agent
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
    port = int(os.getenv("A2A_PORT", "9000"))
    http_url = os.getenv("A2A_URL", f"http://localhost:{port}")
    agent = weather_agent()
    server = A2AServer(
        agent=agent,
        port=port,
        host="0.0.0.0",
        http_url=http_url
    )
    try:
        logger.info(f"A2A AgentCard on http://localhost:{port}/.well-known/agent-card.json")
        logger.info(f"A2A Server available on http_url:{http_url}")
        logger.info("Press Ctrl+C to stop the server")
        server.serve()
    except KeyboardInterrupt:
        logger.info("\nShutting down A2A server...")
        server.stop()

if __name__ == "__main__":
    run_a2a_server()
