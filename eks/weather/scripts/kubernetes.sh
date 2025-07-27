#!/bin/bash

# Get kubeconfig

aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}

# Deploy the MCP Server
helm upgrade ${KUBERNETES_APP_WEATHER_MCP_NAME} mcp-servers/weather-mcp-server/helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
  --create-namespace \
  -f mcp-servers/weather-mcp-server/helm/workshop-values.yaml

# Deploy the Agent
helm upgrade ${KUBERNETES_APP_WEATHER_AGENT_NAME} helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  --create-namespace \
  -f helm/workshop-values.yaml

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
  -f web/helm/workshop-values.yaml


# Wait at the end this way karpenter can select a node for the 3 pods
echo "Waiting for Pods to be running..."

# Wait for MCP server to be ready
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_MCP_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE}

# Wait for Agent to be ready
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE}

# Wait for Agent UI to be ready
kubectl rollout status deployment ${KUBERNETES_APP_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE}
