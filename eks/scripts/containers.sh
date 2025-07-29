#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/../..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

source "${SCRIPTDIR}/env.sh"

# Login into ECR, in case we need it
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REPO_HOST} || true

# Build and push MCP Server
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_MCP_URI}:latest "${SINGLE_AGENT_DIRECTORY}/mcp-servers/weather-mcp-server"
docker push ${ECR_REPO_WEATHER_MCP_URI}:latest

# Build and push Agent Service
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_AGENT_URI}:latest "${SINGLE_AGENT_DIRECTORY}"
docker push ${ECR_REPO_WEATHER_AGENT_URI}:latest

# Build and push Agent UI
docker build --platform linux/amd64 -t ${ECR_REPO_AGENT_UI_URI}:latest "${UI_AGENT_DIRECTORY}"
docker push ${ECR_REPO_AGENT_UI_URI}:latest

