#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/../..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

export TERRAFORM_DIRECTORY="terraform"

# Setup the .env, and web/.env, and workshop-values.yaml
$ROOTDIR/$TERRAFORM_DIRECTORY/prep-env-weather-agent.sh
$ROOTDIR/$TERRAFORM_DIRECTORY/prep-env-weather-ui.sh

# AWS Configuration
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
export AWS_REGION=us-west-2

# EKS Cluster Configuration
export CLUSTER_NAME=${CLUSTER_NAME:-agentic-ai-on-eks}

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

# Agents
export MCP_HELM_CHART="${ROOTDIR}/weather/mcp-servers/weather-mcp-server/helm"
export WEATHER_MCP_VALUES="${MCP_HELM_CHART}/workshop-mcp-weather-values.yaml"

export SINGLE_AGENT_DIRECTORY="${ROOTDIR}/weather"
export AGENT_HELM_CHART="${ROOTDIR}/weather/helm"

export WEATHER_AGENT_HELM_VALUES="${AGENT_HELM_CHART}/workshop-agent-weather-values.yaml"

export UI_AGENT_DIRECTORY="${ROOTDIR}/weather/web"
export UI_AGENT_HELM_CHART="${ROOTDIR}/weather/web/helm"
export UI_AGENT_HELM_VALUES="${UI_AGENT_HELM_CHART}/workshop-ui-values.yaml"



