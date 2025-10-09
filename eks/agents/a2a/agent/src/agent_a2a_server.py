import os
from strands.multiagent.a2a import A2AServer
from .agent import get_agent

def create_a2a_server(port, http_url):
    """Create and configure an A2A server with the agent."""
    agent = get_agent()
    server = A2AServer(
        agent=agent,
        port=port,
        host="0.0.0.0",
        http_url=http_url
    )
    print(f"A2A Server available on http_url:{http_url}")
    return server

def main():
    """Start the A2A server and keep it running."""
    port = int(os.getenv("A2A_PORT", "9000"))
    http_url = os.getenv("A2A_URL", f"http://localhost:{port}")
    server = create_a2a_server(port, http_url)
    print("Press Ctrl+C to stop the server")
    try:
        server.serve()
    except KeyboardInterrupt:
        print("\nShutting down A2A server...")
        server.stop()

if __name__ == "__main__":
    main()
