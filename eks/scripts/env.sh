#!/usr/bin/env bash

# We can set -e or -u it brakes the workshop studio shell
#set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

# Setup the .env, and web/.env, and workshop-values.yaml
$SCRIPTDIR/terraform-prep-env-weather-agent.sh
$SCRIPTDIR/terraform-prep-env-travel-agent.sh
$SCRIPTDIR/terraform-prep-env-weather-ui.sh

# AWS Configuration
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
export AWS_REGION=us-west-2

# EKS Cluster Configuration
export CLUSTER_NAME=${CLUSTER_NAME:-agentic-ai-on-eks}

# Kubernetes Configuration
export KUBERNETES_APP_WEATHER_MCP_NAMESPACE=mcp-servers
export KUBERNETES_APP_WEATHER_MCP_NAME=weather-mcp

export KUBERNETES_APP_WEATHER_AGENT_NAMESPACE=agents
export KUBERNETES_APP_WEATHER_AGENT_NAME=weather-agent

export KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE=agents
export KUBERNETES_APP_TRAVEL_AGENT_NAME=travel-agent

export KUBERNETES_APP_AGENT_UI_NAMESPACE=ui
export KUBERNETES_APP_AGENT_UI_NAME=agent-ui
export KUBERNETES_APP_AGENT_UI_SECRET_NAME=agent-ui

# ECR Configuration
export ECR_REPO_HOST=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

export ECR_REPO_WEATHER_MCP_NAME=agents-on-eks/weather-mcp
export ECR_REPO_WEATHER_MCP_URI=${ECR_REPO_HOST}/${ECR_REPO_WEATHER_MCP_NAME}

export ECR_REPO_WEATHER_AGENT_NAME=agents-on-eks/weather-agent
export ECR_REPO_WEATHER_AGENT_URI=${ECR_REPO_HOST}/${ECR_REPO_WEATHER_AGENT_NAME}

export ECR_REPO_TRAVEL_AGENT_NAME=agents-on-eks/travel-agent
export ECR_REPO_TRAVEL_AGENT_URI=${ECR_REPO_HOST}/${ECR_REPO_TRAVEL_AGENT_NAME}

export ECR_REPO_AGENT_UI_NAME=agents-on-eks/agent-ui
export ECR_REPO_AGENT_UI_URI=${ECR_REPO_HOST}/${ECR_REPO_AGENT_UI_NAME}

# Amazon Bedrock Configuration
export BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0

# Helm Charts
export MCP_HELM_CHART="${ROOTDIR}/manifests/helm/mcp"
export AGENT_HELM_CHART="${ROOTDIR}/manifests/helm/agent"
export UI_AGENT_HELM_CHART="${ROOTDIR}/manifests/helm/ui"

# UI
export UI_AGENT_DIRECTORY="${ROOTDIR}/ui"
export UI_AGENT_HELM_VALUES="${UI_AGENT_HELM_CHART}/workshop-ui-values.yaml"

# Agents
export WEATHER_AGENT_DIRECTORY="${ROOTDIR}/agents/weather"
export WEATHER_AGENT_HELM_VALUES="${AGENT_HELM_CHART}/workshop-agent-weather-values.yaml"

export TRAVEL_AGENT_DIRECTORY="${ROOTDIR}/agents/travel"
export TRAVEL_AGENT_HELM_VALUES="${AGENT_HELM_CHART}/workshop-agent-travel-values.yaml"

# MCP Servers
# TODO: move all mcp servers to the root under ${ROOTDIR}/mcp-servers
export WEATHER_MCP_DIRECTORY="${ROOTDIR}/agents/weather/mcp-servers/weather-mcp-server"
export WEATHER_MCP_VALUES="${MCP_HELM_CHART}/workshop-mcp-weather-values.yaml"
