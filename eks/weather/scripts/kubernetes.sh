#!/bin/bash

# Deploy MCP Server
helm upgrade ${KUBERNETES_APP_WEATHER_MCP_NAME} mcp-servers/weather-mcp-server/helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
  --create-namespace \
  --set image.repository=${ECR_REPO_WEATHER_MCP_URI}

# Deploy Agent
helm upgrade ${KUBERNETES_APP_WEATHER_AGENT_NAME} helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  --create-namespace \
  --set image.repository=${ECR_REPO_WEATHER_AGENT_URI} \
  --set env.DYNAMODB_AGENT_STATE_TABLE_NAME=${DYNAMODB_AGENT_STATE_TABLE_NAME} \
  --set env.OAUTH_JWKS_URL=${OAUTH_JWKS_URL} \
  -f helm/mcp-remote.yaml

# Deploy UI
kubectl create ns ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE} || true
kubectl delete secret ${KUBERNETES_APP_WEATHER_AGENT_UI_SECRET_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE} 2>/dev/null || true
kubectl create secret generic ${KUBERNETES_APP_WEATHER_AGENT_UI_SECRET_NAME} \
  --from-literal=OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} \
  --from-literal=OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET} \
  --from-literal=OAUTH_LOGOUT_URL=${OAUTH_LOGOUT_URL} \
  --from-literal=OAUTH_WELL_KNOWN_URL=${OAUTH_WELL_KNOWN_URL} \
  --from-literal=OAUTH_JWKS_URL=${OAUTH_JWKS_URL} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE}
helm upgrade ${KUBERNETES_APP_WEATHER_AGENT_UI_NAME} web/helm \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE} \
  --create-namespace \
  --set image.repository=${ECR_REPO_WEATHER_AGENT_UI_URI} \
  --set secret.name=${KUBERNETES_APP_WEATHER_AGENT_UI_SECRET_NAME} \
  --set env.AGENT_UI_ENDPOINT_URL_1="http://${KUBERNETES_APP_WEATHER_AGENT_NAME}.${KUBERNETES_APP_WEATHER_AGENT_NAME}/prompt" \
  --set service.type="${KUBERNETES_APP_WEATHER_AGENT_UI_SERVICE_TYPE:-ClusterIP}

# TODO: Implement VSCode Proxy
#  --set env.BASE_PATH="${KUBERNETES_APP_WEATHER_AGENT_UI_BASE_PATH:-''}" \
#  --set env.BASE_URL="${IDE_URL:-http://localhost:8000}"


# Wait at the end this way karpenter can select a node for the 3 pods
echo "Waiting for Pods to be running..."
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_MCP_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE}
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE}
kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE}
