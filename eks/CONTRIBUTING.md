# Contributing to AI Agents on EKS

This guide covers local development setup, testing, troubleshooting, and contribution guidelines for the AI Agents on EKS project.

## Development Setup

### Prerequisites

Ensure you have the following configured:
```bash
export AWS_ACCESS_KEY_ID=<key here>
export AWS_SECRET_ACCESS_KEY=<access key here>
export AWS_SESSION_TOKEN=<session here>
```

### Install Dependencies

```bash
uv sync
```

## Local Development

### Interactive Mode

Run the agent in interactive CLI mode:

```bash
uv run interactive
```

Type a question to test the agent. To exit, use `/quit`.

### Protocol Servers

The agent supports three protocols simultaneously:

#### MCP Server

Run as MCP server with streamable-http or stdio transport:

```bash
# Streamable HTTP (default for containers)
uv run mcp-server --transport streamable-http

# Standard I/O (default for CLI)
uv run mcp-server --transport stdio
```

Test the MCP server:
```bash
uv run test-e2e-mcp
```

Connect with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector
```
In the UI, use streamable-http with `http://localhost:8080/mcp`

#### A2A Server

Run as Agent-to-Agent server:

```bash
uv run a2a-server
```

Test the A2A server:
```bash
uv run test-e2a-a2a
```

#### FastAPI Server

Run as FastAPI REST API server:

```bash
# Production mode (with authentication)
uv run fastapi-server

# Development mode (without authentication)
DISABLE_AUTH=1 uv run fastapi-server
```

Test the FastAPI server:
```bash
# Python test client
uv run test-e2e-fastapi

# Curl test client (colorized output)
./tests/test_e2e_fastapi_curl.sh
```

#### Triple Server Mode

Run all three servers simultaneously:

```bash
# Recommended for development (best shutdown behavior)
python3 main.py

# Alternative (may have shutdown issues with uv signal handling)
uv run agent
```

## Container Development

### Building Containers

Build the container using Docker:
```bash
docker build . --tag agent --build-arg RUNTAG=latest-dev
```

Build the container using Finch:
```bash
finch build . --tag agent --build-arg RUNTAG=latest-dev
```

### Running Containers

#### Interactive Mode

```bash
docker run -it \
  -e AWS_REGION=${AWS_REGION} \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
  --entrypoint interactive agent
```

#### Triple Server Mode

```bash
docker run \
  -p 8080:8080 -p 9000:9000 -p 3000:3000 \
  -e AWS_REGION=${AWS_REGION} \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
  -e DISABLE_AUTH=1 \
  agent
```

Test all protocols:
```bash
uv run test-e2e-mcp        # Tests MCP Protocol
uv run test-e2e-a2a        # Tests A2A Protocol
./tests/test_e2e_fastapi_curl.sh  # Tests FastAPI
```

## Testing

### Test Suite Overview

The project includes comprehensive test clients for all three protocols:

#### MCP Test Client (`tests/test_e2e_mcp.py`)
- **Tests**: 6 comprehensive MCP protocol tests (0-5)
- **Coverage**: HTTP connectivity, session initialization, tool discovery, weather queries
- **Usage**: `uv run test-e2e-mcp`

#### A2A Test Client (`tests/test_e2e_a2a.py`)
- **Tests**: 6 comprehensive A2A protocol tests (1-6)
- **Coverage**: Agent card discovery, client initialization, weather queries
- **Usage**: `uv run test-e2e-a2a`

#### FastAPI Test Clients
- **Python Client** (`tests/test_e2e_fastapi.py`): Async HTTP testing with aiohttp
- **Curl Client** (`tests/test_e2e_fastapi_curl.sh`): Workshop-friendly colorized output
- **Tests**: 6 comprehensive FastAPI tests each (1-6)
- **Coverage**: Health checks, weather endpoints, error handling
- **Usage**:
  ```bash
  uv run test-e2e-fastapi           # Python client
  ./tests/test_e2e_fastapi_curl.sh  # Curl client
  ```

**Note**: FastAPI tests require authentication to be disabled:
```bash
DISABLE_AUTH=1 uv run fastapi-server
```

### Test Features

All test clients provide:
- **Server Readiness Check**: Automatic availability checking with timeouts
- **Structured Output**: Numbered tests with ✅/❌ indicators
- **Comprehensive Coverage**: Protocol-specific functionality testing
- **Error Handling**: Graceful failure handling and clear messages
- **Response Preview**: Clean preview of responses with truncation

## Agent Configuration

### Configuration Files

The agent's behavior is defined in markdown configuration files:

#### Default Configuration (`agent.md`)
```markdown
# Weather Assistant Agent Configuration

## Agent Name
Weather Assistant

## Agent Description
Weather Assistant that provides weather forecasts and alerts

## System Prompt
You are Weather Assistant that helps the user with forecasts or alerts:
- Provide weather forecasts for US cities for the next 3 days if no specific period is mentioned
- When returning forecasts, always include whether the weather is good for outdoor activities for each day
- Provide information about weather alerts for US cities when requested
```

#### Custom Configuration

Create a custom configuration file:
```bash
cat > custom_weather_agent.md << 'EOF'
# Advanced Weather Specialist Configuration

## Agent Name
Advanced Weather Specialist

## Agent Description
Advanced Weather Specialist providing detailed meteorological analysis

## System Prompt
You are an Advanced Weather Specialist with expertise in meteorology:
- Provide comprehensive weather forecasts for any location worldwide
- Include detailed meteorological analysis with pressure systems and wind patterns
- Offer specialized advice for aviation, marine, and agricultural weather needs
- Always explain the reasoning behind your forecasts using meteorological principles
EOF

# Use custom configuration
export AGENT_CONFIG_FILE=/path/to/custom_weather_agent.md
```

#### Configuration Loading Priority

1. **Custom file** specified by `AGENT_CONFIG_FILE` environment variable
2. **Default file** `agent.md` in the project directory
3. **Fallback file** `cloudbot.md` if `agent.md` is missing

**Important**: An MD configuration file is **required**. The system will raise an error if no configuration file is found.

## Architecture Details

### Entry Points Configuration

The project uses multiple entry points defined in `pyproject.toml`:

```python
[project.scripts]
"mcp-server"       = "src.main:main_mcp_server"    # MCP only
"a2a-server"       = "src.main:main_a2a_server"    # A2A only
"fastapi-server"   = "src.main:main_fastapi"       # FastAPI only
"interactive"      = "src.main:main_interactive"   # CLI mode
"agent"            = "src.main:servers"            # All three servers (DEFAULT)
"test-e2e-mcp"     = "tests.test_e2e_mcp:run_main"   # MCP e2e tests
"test-e2e-a2a"     = "tests.test_e2e_a2a:run_main"   # A2A e2e tests
"test-e2e-fastapi" = "tests.test_e2e_fastapi:main"   # FastAPI e2e tests
```

### File Structure

```
weather/
├── src/                     # Source code directory
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Core weather agent logic + configuration utilities
│   ├── agent_server_mcp.py  # MCP server (port 8080)
│   ├── agent_server_a2a.py  # A2A server (port 9000)
│   ├── agent_server_fastapi.py # FastAPI server (port 3000)
│   ├── agent_interactive.py # Interactive CLI agent
│   └── main.py              # Entry points + triple server orchestrator
├── tests/                   # E2E test suite
│   ├── __init__.py          # Test package init
│   ├── test_e2e_mcp.py      # MCP protocol test client
│   ├── test_e2e_a2a.py      # A2A protocol test client
│   ├── test_e2e_fastapi.py  # FastAPI Python test client
│   └── test_e2e_fastapi_curl.sh # Workshop-friendly curl test script
├── Dockerfile               # Multi-arch container (agent)
├── helm/                    # Kubernetes deployment charts
├── mcp-servers/             # MCP tool definitions
│   └── weather-mcp-server/  # Weather MCP server
├── pyproject.toml          # Entry points configuration
├── README.md               # Human-readable deployment tutorial
└── AmazonQ.md              # AI Agent technical reference
```

### Logging Configuration

All modules use standardized logging:

```python
# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') == '1' else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)
```

**Usage Examples:**
```bash
# Normal logging (INFO level)
uv run agent

# Debug logging (DEBUG level)
DEBUG=1 uv run agent

# Container with debug logging
docker run -e DEBUG=1 weather-agent
```

## Troubleshooting

### Common Issues

#### Architecture Mismatch
- **Symptom**: `exec format error` in pod logs
- **Root Cause**: Single-arch image on incompatible node
- **Fix**: Verify architecture with `docker manifest inspect`
- **Prevention**: Always use `--platform linux/amd64`

#### Health Check Failures
- **Symptom**: Pod CrashLoopBackOff, health check timeouts
- **Root Cause**: Wrong transport or port configuration
- **Fix**: Ensure streamable-http transport and correct ports (8080/9000/3000)
- **Debug**: Check `kubectl logs deployment/weather-agent`

#### Shutdown Problems
- **Symptom**: `uv run agent` doesn't respond to Ctrl+C properly
- **Root Cause**: Signal interception by uv process wrapper
- **Fix**: Use direct Python execution: `python3 main.py`
- **Alternative**: Use `uv run agent` but expect to need force kill

#### Single Protocol Access
- **Symptom**: Only MCP or A2A accessible, not both
- **Root Cause**: Wrong entry point in Dockerfile
- **Fix**: Ensure `CMD ["agent"]`
- **Verification**: Test both `curl localhost:8080` and `curl localhost:9000`

#### FastAPI Not Responding
- **Symptom**: FastAPI endpoints return 404 or connection refused
- **Root Cause**: FastAPI dependency missing or wrong port configuration
- **Fix**: Ensure FastAPI is installed and FASTAPI_PORT=3000
- **Verification**: Test `curl localhost:3000/health`

### EKS Debugging

#### Check Pod Status
```bash
kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  get pods -l app.kubernetes.io/instance=${KUBERNETES_APP_WEATHER_AGENT_NAME}
```

#### View Logs
```bash
kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  logs deployment/${KUBERNETES_APP_WEATHER_AGENT_NAME}
```

#### Check Events
```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### Port Forwarding for Testing
```bash
kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  port-forward service/${KUBERNETES_APP_WEATHER_AGENT_NAME} 8080:8080 9000:9000 3000:3000
```

## Multi-Architecture Support

### Building Multi-Architecture Images

Build for AMD64 architecture:
```bash
docker build --platform linux/amd64 \
  -t ${ECR_REPO_URI}:latest \
  .
docker push ${ECR_REPO_URI}:latest
```

Verify architecture support:
```bash
docker manifest inspect ${ECR_REPO_URI}:latest | grep -E "amd64"
```

## Environment Variables

### Required Variables

```bash
# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# Bedrock Configuration
BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0

# Server Ports
MCP_PORT=8080                # MCP server port
A2A_PORT=9000                # A2A server port
FASTAPI_PORT=3000            # FastAPI server port

# Development
DEBUG=1                      # Enable debug logging
DISABLE_AUTH=1               # Disable FastAPI authentication for testing
AGENT_CONFIG_FILE=/path/to/custom/agent.md  # Custom agent configuration
```

## Contributing Guidelines

### Before Making Changes

1. Read both README.md and AmazonQ.md
2. Identify which documentation sections will be affected
3. Note current entry points and configuration

### During Implementation

1. Test changes locally with `agent`
2. Verify all protocols work (MCP:8080, A2A:9000, REST:3000)
3. Update entry points if pyproject.toml changes
4. Test multi-architecture builds if Dockerfile changes

### After Changes

1. Update technical details in AmazonQ.md
2. Update user instructions in README.md
3. Verify all command examples work
4. Test container build and deployment

### Documentation Synchronization

When making changes, update both files:

#### README.md Updates:
- Command examples with new entry points
- Environment variables if added/changed
- Deployment steps if process changes
- Prerequisites if tools/versions change

#### AmazonQ.md Updates:
- Entry points table if pyproject.toml changes
- Docker CMD if Dockerfile changes
- Quick commands with new entry points
- Technical decisions for architectural changes
- Troubleshooting database for new issues

### Critical Consistency Points

These MUST be identical across both files:
- Entry point names (`mcp-server`, `a2a-server`, etc.)
- Port numbers (8080 for MCP, 9000 for A2A, 3000 for REST API)
- Environment variables (BEDROCK_MODEL_ID, AWS_REGION, etc.)
- Resource names (cluster, IAM roles, ECR repositories)

## Support

For development issues:
- Check the troubleshooting section above
- Review test client outputs for protocol-specific issues
- Verify environment variables are set correctly
- Test with debug logging enabled: `DEBUG=1`
