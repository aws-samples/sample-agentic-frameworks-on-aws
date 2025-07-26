#!/bin/bash

# Login into ECR
aws ecr get-login-password --region ${AWS_REGION} |
  podman login --username AWS --password-stdin ${ECR_REPO_HOST}

# MCP Server Image
podman build --platform linux/amd64 -t ${ECR_REPO_WEATHER_MCP_URI}:latest weather/mcp-servers/weather-mcp-server
podman push ${ECR_REPO_WEATHER_MCP_URI}:latest

# Weather Agent Image
podman build --platform linux/amd64 -t ${ECR_REPO_WEATHER_AGENT_URI}:latest weather
podman push ${ECR_REPO_WEATHER_AGENT_URI}:latest

# Travel Agent Image
podman build --platform linux/amd64 -t ${ECR_REPO_TRAVEL_AGENT_URI}:latest travel
podman push ${ECR_REPO_TRAVEL_AGENT_URI}:latest

# Travel Agent Image

# UI Image
podman build --platform linux/amd64 -t ${ECR_REPO_WEATHER_AGENT_UI_URI}:latest weather/web
podman push ${ECR_REPO_WEATHER_AGENT_UI_URI}:latest
