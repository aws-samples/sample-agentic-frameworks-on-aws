# AI Agents on EKS

A generic AI agent framework built with Strands Agents, MCP (Model Context Protocol), A2A (Agent to Agent), and FastAPI. Configurable for any domain including weather forecasts, financial analysis, customer service, and more.

## Example

Deploy a complete AI agent system with Agent UI, Agent Service, and MCP Server to Amazon EKS in just a few steps.

### Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) (v2.0 or later)
- [Docker](https://docs.docker.com/get-docker/) with buildx support
- [Helm](https://helm.sh/docs/intro/install/) (v3.0 or later)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (v1.28 or later)
- Enable a model that support tool callig, see [Supported models and model features](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html). For this example, request model access for **Claude 3.7 Sonnet** in the [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/home#/modelaccess)

**Required AWS Permissions:**
- EKS cluster creation and management
- IAM role and policy management
- ECR repository management
- Amazon Bedrock access

### Architecture Overview

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "Amazon ECR"
            ECR_UI[Weather UI Image]
            ECR_AGENT[Weather Agent Image]
            ECR_MCP[Weather MCP Image]
        end

        subgraph "Amazon EKS Cluster"
            subgraph "agent-ui namespace"
                UI_POD[Agent UI<br/>FastAPI:8000<br/>OAuth Auth]
            end

            subgraph "weather-agent namespace"
                AGENT_POD[Weather Agent<br/>MCP:8080 A2A:9000 REST:3000]
            end

            subgraph "mcp-servers namespace"
                MCP_POD[Weather MCP Server<br/>HTTP:8080<br/>Tools: forecast, alert]
            end
        end

        subgraph "Amazon Bedrock"
            BEDROCK[Claude 3.7 Sonnet]
        end
    end

    subgraph "End Users"
        USER[Web Browser<br/>User Login]
    end

    UI_POD -->|REST API :3000| AGENT_POD
    AGENT_POD -->|MCP HTTP :8080| MCP_POD
    AGENT_POD -->|Invoke LLM| BEDROCK
    USER -->|Authenticated Agent UI| UI_POD

    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef k8s fill:#326CE5,stroke:#fff,stroke-width:2px,color:#fff
    classDef user fill:#9370DB,stroke:#fff,stroke-width:2px,color:#fff

    class ECR_UI,ECR_AGENT,ECR_MCP,BEDROCK aws
    class UI_POD,AGENT_POD,MCP_POD k8s
    class USER user
```

**Key Components:**
- **Agent UI**: FastAPI-based frontend with OAuth authentication (port 8000)
- **Agent Service**: Triple protocol support - MCP (8080), A2A (9000), REST API (3000)
- **MCP Server**: Dedicated weather tools server providing forecast/alert capabilities (port 8080)
- **Security**: EKS Pod Identity for Bedrock access, OAuth JWT validation for user authentication


## Agent Code

Open the Agent code, go to line 162
```bash
code -g src/agent.py:162:9
```

This is how an Agent gets created:
```python
        agent = Agent(
            name=agent_name,
            description=agent_description,
            model=bedrock_model,
            system_prompt=system_prompt,
            tools=[agent_tools]+mcp_tools,
            messages=messages,
            conversation_manager=conversation_manager
        )
```


## Deployment Steps

TLDR (In case you don't want to run all the steps manually and see the app running)
```bash
source ./scripts/run.sh
```

### 1. Environment Setup

Set up the required environment variables:

```bash
# AWS Configuration
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
export AWS_REGION=us-west-2

# EKS Cluster Configuration
export CLUSTER_NAME=agentic-ai-on-eks

# Kubernetes Configuration
export KUBERNETES_APP_WEATHER_MCP_NAMESPACE=mcp-servers
export KUBERNETES_APP_WEATHER_MCP_NAME=weather-mcp

export KUBERNETES_APP_WEATHER_AGENT_NAMESPACE=weather-agent
export KUBERNETES_APP_WEATHER_AGENT_NAME=weather-agent

export KUBERNETES_APP_AGENT_UI_NAMESPACE=agent-ui
export KUBERNETES_APP_AGENT_UI_NAME=agent-ui
export KUBERNETES_APP_AGENT_UI_SECRET_NAME=agent-ui

# ECR Configuration
export ECR_REPO_HOST=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

export ECR_REPO_WEATHER_MCP_NAME=agents-on-eks/weather-mcp
export ECR_REPO_WEATHER_MCP_URI=${ECR_REPO_HOST}/${ECR_REPO_WEATHER_MCP_NAME}

export ECR_REPO_WEATHER_AGENT_NAME=agents-on-eks/weather-agent
export ECR_REPO_WEATHER_AGENT_URI=${ECR_REPO_HOST}/${ECR_REPO_WEATHER_AGENT_NAME}

export ECR_REPO_AGENT_UI_NAME=agents-on-eks/agent-ui
export ECR_REPO_AGENT_UI_URI=${ECR_REPO_HOST}/${ECR_REPO_AGENT_UI_NAME}

# Amazon Bedrock Configuration
export BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

> **Note:** Make sure you have access to the Amazon Bedrock model in your AWS account.

### 2. Create EKS Cluster

Deploy the infrastructure using Terraform:

```bash
cd ../terraform
terraform init
terraform apply
./prep-env-weather-agent.sh
./prep-env-weather-web.sh
cd -
```

Review the new EKS cluster in the console by visiting the [AWS EKS Console](https://console.aws.amazon.com/eks/home)

### 3. Build and Push All Three Images

Authenticate with ECR:

```bash
# Authenticate with ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REPO_HOST}
```

Build and push all three images:

```bash
# Build and push MCP Server
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_MCP_URI}:latest mcp-servers/weather-mcp-server
docker push ${ECR_REPO_WEATHER_MCP_URI}:latest

# Build and push Agent Service
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_AGENT_URI}:latest .
docker push ${ECR_REPO_WEATHER_AGENT_URI}:latest

# Build and push Agent UI
docker build --platform linux/amd64 -t ${ECR_REPO_AGENT_UI_URI}:latest web
docker push ${ECR_REPO_AGENT_UI_URI}:latest
```

Review the new images cluster in the console by visiting the [AWS ECR Console](https://console.aws.amazon.com/ecr/private-registry/repositories)

### 4. Deploy All Three Services

Make sure you setup kubeconfig:
```bash
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}
```

Deploy the MCP Server:
```bash
# Deploy the MCP Server
helm upgrade ${KUBERNETES_APP_WEATHER_MCP_NAME} mcp-servers/weather-mcp-server/helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
  --create-namespace \
  --set image.repository=${ECR_REPO_WEATHER_MCP_URI}

# Wait for MCP server to be ready
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_MCP_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE}
```

Deploy the Agent Service:
```bash
# Load agent environment variables
source .env

# Deploy the Agent
helm upgrade ${KUBERNETES_APP_WEATHER_AGENT_NAME} helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  --create-namespace \
  --set image.repository=${ECR_REPO_WEATHER_AGENT_URI} \
  --set env.OAUTH_JWKS_URL=${OAUTH_JWKS_URL} \
  --set env.SESSION_STORE_BUCKET_NAME=${SESSION_STORE_BUCKET_NAME} \
  -f helm/mcp-remote.yaml

# Wait for Agent to be ready
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE}
```

Deploy the Agent UI:
```bash
# Load UI environment variables
source web/.env

# Create OAuth secret for the Agent UI
kubectl create ns ${KUBERNETES_APP_AGENT_UI_NAMESPACE} || true
kubectl delete secret ${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} 2>/dev/null || true
kubectl create secret generic ${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
  --from-literal=OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} \
  --from-literal=OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET} \
  --from-literal=OAUTH_LOGOUT_URL=${OAUTH_LOGOUT_URL} \
  --from-literal=OAUTH_WELL_KNOWN_URL=${OAUTH_WELL_KNOWN_URL} \
  --from-literal=OAUTH_JWKS_URL=${OAUTH_JWKS_URL} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE}

# Deploy the Agent UI
helm upgrade ${KUBERNETES_APP_AGENT_UI_NAME} web/helm \
  --install \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
  --create-namespace \
  --set image.repository=${ECR_REPO_AGENT_UI_URI} \
  --set secret.name=${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
  --set env.AGENT_UI_ENDPOINT_URL_1="http://${KUBERNETES_APP_WEATHER_AGENT_NAME}.${KUBERNETES_APP_WEATHER_AGENT_NAME}/prompt" \
  --set service.type="${KUBERNETES_APP_AGENT_UI_SERVICE_TYPE:-ClusterIP}" \
  --set env.BASE_PATH="${KUBERNETES_APP_AGENT_UI_BASE_PATH:-${IDE_URL:+proxy/8000}}" \
  --set env.BASE_URL="${IDE_URL:-http://localhost:8000}"


# Wait for Agent UI to be ready
kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE} \
  rollout status deployment/${KUBERNETES_APP_WEATHER_AGENT_UI_NAME}
```

Review the 3 pods running (MCP, Agent, UI) or go to [AWS EKS Console Resource view](https://console.aws.amazon.com/eks/clusters/agentic-ai-on-eks?&selectedResourceId=pods&selectedTab=cluster-resources-tab)

Or check in the terminal
```bash
kubectl get pods -n weather-agent
kubectl get pods -n agent-ui
```
Expected output should look like this, all pods in `Running` status:
```
NAME                             READY   STATUS    RESTARTS   AGE
weather-agent-7687764cd5-qxb92   1/1     Running   0          1m
weather-mcp-885867d86-bjjd6      1/1     Running   0          1m

NAME                        READY   STATUS    RESTARTS   AGE
agent-ui-775ddb89b4-cv7pt   1/1     Running   0          1m
```

### 5. Access the Weather Agent UI

Before runnign `kubectl port-forward` lets get some values

If running this lab from a workshop environment get the Agent url with this command:
```bash
echo "$IDE_URL/proxy/8000/"
```
Or if running locally on your on your developer computer then use this url http://localhost:8000/

Print the username and password
```bash
echo "Username: Alice"
echp "Password: Passw0rd@"
```

Run Kubectl Port forward the Agent UI and access it:
```bash
kubectl  port-forward svc/${KUBERNETES_APP_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
  8000:fastapi
```

Ask the agent the following question:
```prompt
What's the weather like in San Francisco?
```

Check the agent logs in different terminal
```bash
kubectl logs -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} deploy/${KUBERNETES_APP_WEATHER_AGENT_NAME} -f
```

Ask another question about alerts (a different tool), without specifying the city or state, the Agent remembers the state location from the first message.
```prompt
Any weather alerts?
```

## Agent Configuration

The weather agent's behavior is defined in the `agent.md` file when running locally with `uv run` and in the helm values file [helm/values.yaml](helm/values.yaml) when running in EKS.

The tools for the agent are defined in mcp.json in the helm values file [helm/mcp-remote.yaml](helm/mcp-remote.yaml) to use remote mcp servers, by the default it will use the embedded mcp server enabled in the default [helm/values.yaml](helm/values.yaml) file.

The configuration includes:
- **Agent Name**: Display name for the agent
- **Agent Description**: Brief description of capabilities
- **System Prompt**: Instructions defining behavior and expertise

## Clean Up Resources

When you're done, clean up to avoid charges:

```bash
# Uninstall applications
helm uninstall ${KUBERNETES_APP_WEATHER_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE}
helm uninstall ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE}
helm uninstall ${KUBERNETES_APP_WEATHER_MCP_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE}
```

Delete EKS cluster (via Terraform)
```bash
cd ../terraform
terraform destroy
```

## Next Steps

- **Development**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for local development setup
- **Customization**: Modify `agent.md` to create domain-specific agents
- **Monitoring**: Add CloudWatch logging and metrics for production deployments

## Support

For issues and questions:
- Check the troubleshooting section in [CONTRIBUTING.md](CONTRIBUTING.md)
- Review pod logs: `kubectl logs deployment/<deployment-name>`
- Verify service endpoints: `kubectl get endpoints`
