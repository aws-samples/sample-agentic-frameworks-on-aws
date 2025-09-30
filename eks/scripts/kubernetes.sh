#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

# Function to show usage
show_usage() {
    echo "Usage: $0"
    echo ""
    echo "Deploy Kubernetes components to EKS cluster."
    echo ""
    echo "Use DEPLOY_COMPONENT environment variable to specify which component to deploy:"
    echo "  DEPLOY_COMPONENT=weather-mcp   Deploy Weather MCP Server only"
    echo "  DEPLOY_COMPONENT=weather-agent Deploy Weather Agent only"
    echo "  DEPLOY_COMPONENT=travel-agent  Deploy Travel Agent only"
    echo "  DEPLOY_COMPONENT=ui            Deploy UI Chatbot only"
    echo "  (no variable set)              Deploy all components"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy all components"
    echo "  DEPLOY_COMPONENT=weather-mcp $0      # Deploy only Weather MCP Server"
    echo "  DEPLOY_COMPONENT=weather-agent $0    # Deploy only Weather Agent"
    echo "  DEPLOY_COMPONENT=travel-agent $0     # Deploy only Travel Agent"
    echo "  DEPLOY_COMPONENT=ui $0               # Deploy only UI Chatbot"
}

# Parse component from environment variable
COMPONENT="${DEPLOY_COMPONENT:-all}"

# Handle help request
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    show_usage
    exit 0
fi

# Validate component parameter
case "$COMPONENT" in
    weather-mcp|weather-agent|travel-agent|ui|all)
        ;;
    *)
        echo "Error: Invalid component '$COMPONENT'"
        echo ""
        show_usage
        exit 1
        ;;
esac

# Always skip terraform
source "${SCRIPTDIR}/env.sh"

# Get kubeconfig
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}

# Function to deploy Weather MCP Server
deploy_mcp() {
    # delete deployment, service, and service account weather-mcp
    kubectl delete deployment ${KUBERNETES_APP_WEATHER_MCP_NAME} \
    --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} 2>/dev/null || true
    kubectl delete service ${KUBERNETES_APP_WEATHER_MCP_NAME} \
    --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} 2>/dev/null || true
    kubectl delete serviceaccount ${KUBERNETES_APP_WEATHER_MCP_NAME} \
    --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} 2>/dev/null || true
    echo "Deploying Weather MCP Server..."
    helm upgrade ${KUBERNETES_APP_WEATHER_MCP_NAME} "${MCP_HELM_CHART}" \
      --install \
      --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
      --create-namespace \
      -f "${WEATHER_MCP_VALUES}"
    # Wait for Weather MCP server to be ready
    kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_MCP_NAME} \
      --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE}
    echo "Weather MCP Server deployed successfully!"
}

# Function to deploy Weather Agent
deploy_weather() {
    # delete deployment, service, and service account weather-agent
    kubectl delete deployment ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
    --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} 2>/dev/null || true
    kubectl delete service ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
    --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} 2>/dev/null || true
    kubectl delete serviceaccount ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
    --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} 2>/dev/null || true
    echo "Deploying Weather Agent..."
    helm upgrade ${KUBERNETES_APP_WEATHER_AGENT_NAME} "${AGENT_HELM_CHART}" \
      --install \
      --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
      --create-namespace \
      -f "${WEATHER_AGENT_HELM_VALUES}"
    # Wait for Weather Agent to be ready
    kubectl rollout status deployment ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
      --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE}
    echo "Weather Agent deployed successfully!"
}

# Function to deploy Travel Agent
deploy_travel() {
    # delete deployment, service, and service account travel-agent
    kubectl delete deployment ${KUBERNETES_APP_TRAVEL_AGENT_NAME} \
    --namespace ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE} 2>/dev/null || true
    kubectl delete service ${KUBERNETES_APP_TRAVEL_AGENT_NAME} \
    --namespace ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE} 2>/dev/null || true
    kubectl delete serviceaccount ${KUBERNETES_APP_TRAVEL_AGENT_NAME} \
    --namespace ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE} 2>/dev/null || true
    echo "Deploying Travel Agent..."
    helm upgrade ${KUBERNETES_APP_TRAVEL_AGENT_NAME} "${AGENT_HELM_CHART}" \
      --install \
      --namespace ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE} \
      --create-namespace \
      -f "${TRAVEL_AGENT_HELM_VALUES}"
    # Wait for Travel Agent to be ready
    kubectl rollout status deployment ${KUBERNETES_APP_TRAVEL_AGENT_NAME} \
      --namespace ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE}
    echo "Travel Agent deployed successfully!"
}

# Function to deploy UI Chatbot
deploy_ui() {
    echo "Deploying UI Chatbot..."
    # Create OAuth secret for the Agent UI, before deploying the UI ChatBot
    kubectl create ns ${KUBERNETES_APP_AGENT_UI_NAMESPACE} || true
    kubectl delete secret ${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
      --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} 2>/dev/null || true
    kubectl create secret generic ${KUBERNETES_APP_AGENT_UI_SECRET_NAME} \
      --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
      --from-env-file ${UI_AGENT_DIRECTORY}/.env
    # Deploy the UI ChatBot
    helm upgrade ${KUBERNETES_APP_AGENT_UI_NAME} "${UI_AGENT_HELM_CHART}" \
      --install \
      --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
      --create-namespace \
      -f "${UI_AGENT_HELM_VALUES}"
    # Wait for UI ChatBot to be ready
    kubectl rollout status deployment ${KUBERNETES_APP_AGENT_UI_NAME} \
      --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE}
    echo "UI Chatbot deployed successfully!"
}

# Deploy based on component parameter
case "$COMPONENT" in
    weather-mcp)
        deploy_mcp
        ;;
    weather-agent)
        deploy_weather
        ;;
    travel-agent)
        deploy_travel
        ;;
    ui)
        deploy_ui
        ;;
    all)
        echo "Deploying all components..."
        deploy_mcp
        deploy_weather
        deploy_travel
        deploy_ui
        echo "All components deployed successfully!"
        ;;
esac

