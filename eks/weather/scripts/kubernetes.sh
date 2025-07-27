#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/../..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

source "${SCRIPTDIR}/env.sh"

# Get kubeconfig
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}

# Deploy the MCP Server
helm upgrade ${KUBERNETES_APP_WEATHER_MCP_NAME} "${MCP_HELM_CHART}" \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
  --create-namespace \
  -f "${WEATHER_MCP_VALUES}"

# Deploy the Agent
helm upgrade ${KUBERNETES_APP_WEATHER_AGENT_NAME} "${AGENT_HELM_CHART}" \
  --install \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
  --create-namespace \
  -f "${WEATHER_AGENT_HELM_VALUES}"

# Create OAuth secret for the Agent UI
kubectl create ns ${KUBERNETES_APP_AGENT_UI_NAMESPACE} || true
kubectl delete secret ${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} 2>/dev/null || true
kubectl create secret generic ${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
  --from-env-file ${UI_AGENT_DIRECTORY}/.env

# Deploy the Agent UI
helm upgrade ${KUBERNETES_APP_AGENT_UI_NAME} "${UI_AGENT_HELM_CHART}" \
  --install \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
  --create-namespace \
  -f "${UI_AGENT_HELM_VALUES}"


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
