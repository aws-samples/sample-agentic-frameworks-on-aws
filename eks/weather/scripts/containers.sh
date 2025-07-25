#!/bin/bash

# Login into ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REPO_HOST}

# MCP Server Image
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_MCP_URI}:latest mcp-servers/weather-mcp-server
docker push ${ECR_REPO_WEATHER_MCP_URI}:latest

# Agent Image
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_AGENT_URI}:latest .
docker push ${ECR_REPO_WEATHER_AGENT_URI}:latest

# UI Image
docker build --platform linux/amd64 -t ${ECR_REPO_WEATHER_AGENT_UI_URI}:latest web
docker push ${ECR_REPO_WEATHER_AGENT_UI_URI}:latest
