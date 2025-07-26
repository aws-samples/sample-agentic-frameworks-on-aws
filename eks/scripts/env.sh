#!/bin/bash

# Setup the .env, and web/.env
pushd terraform
./prep-env-weather-agent.sh
./prep-env-weather-web.sh
popd

# Source the created .env files
source weather/.env
source weather/web/.env
source travel/.env

# AWS Configuration
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
export AWS_REGION=us-west-2

# EKS Cluster Configuration
export CLUSTER_NAME=agentic-ai-on-eks

# Kubernetes Configuration
export KUBERNETES_APP_WEATHER_MCP_NAMESPACE=weather-agent
export KUBERNETES_APP_WEATHER_MCP_NAME=weather-mcp

export KUBERNETES_APP_WEATHER_AGENT_NAMESPACE=weather-agent
export KUBERNETES_APP_WEATHER_AGENT_NAME=weather-agent
export KUBERNETES_APP_WEATHER_AGENT_SERVICE_ACCOUNT=weather-agent

export KUBERNETES_APP_WEATHER_AGENT_UI_NAMESPACE=agent-ui
export KUBERNETES_APP_WEATHER_AGENT_UI_NAME=agent-ui
export KUBERNETES_APP_WEATHER_AGENT_UI_SECRET_NAME=agent-ui

export KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE=travel-agent
export KUBERNETES_APP_TRAVEL_AGENT_NAME=travel-agent
export KUBERNETES_APP_TRAVEL_AGENT_SERVICE_ACCOUNT=travel-agent

# ECR Configuration
export ECR_REPO_HOST=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

export ECR_REPO_MCP_NAME=agents-on-eks/weather-mcp
export ECR_REPO_WEATHER_MCP_URI=${ECR_REPO_HOST}/${ECR_REPO_MCP_NAME}

export ECR_REPO_NAME=agents-on-eks/weather-agent
export ECR_REPO_WEATHER_AGENT_URI=${ECR_REPO_HOST}/${ECR_REPO_NAME}

export ECR_REPO_TRAVEL_NAME=agents-on-eks/travel-agent
export ECR_REPO_TRAVEL_AGENT_URI=${ECR_REPO_HOST}/${ECR_REPO_TRAVEL_NAME}

export ECR_REPO_UI_NAME=agents-on-eks/weather-agent-ui
export ECR_REPO_WEATHER_AGENT_UI_URI=${ECR_REPO_HOST}/${ECR_REPO_UI_NAME}

# Amazon Bedrock Configuration
export BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
export BEDROCK_PODIDENTITY_IAM_ROLE=${CLUSTER_NAME}-bedrock-role
