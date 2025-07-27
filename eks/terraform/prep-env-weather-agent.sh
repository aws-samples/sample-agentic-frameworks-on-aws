#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

TERRAFORM_DIRECTORY="terraform"

MCP_HELM_CHART="${ROOTDIR}/weather/mcp-servers/weather-mcp-server/helm"
WEATHER_MCP_VALUES="${MCP_HELM_CHART}/workshop-mcp-weather-values.yaml"

AGENT_HELM_CHART="${ROOTDIR}/weather/helm"
WEATHER_AGENT_HELM_VALUES="${AGENT_HELM_CHART}/workshop-agent-weather-values.yaml"

WEATHER_AGENT_DST_FILE_NAME="${ROOTDIR}/weather/.env"



TERRAFORM_OUTPUTS_MAP=$(terraform -chdir=$ROOTDIR/$TERRAFORM_DIRECTORY output --json outputs_map)

OAUTH_JWKS_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_jwks_url")
BEDROCK_MODEL_ID=$(terraform -chdir=$ROOTDIR/$TERRAFORM_DIRECTORY output -json bedrock_model_id)
SESSION_STORE_BUCKET_NAME=$(terraform -chdir=$ROOTDIR/$TERRAFORM_DIRECTORY output -json weather_agent_session_store_bucket_name)

echo "" > $WEATHER_AGENT_DST_FILE_NAME
echo "OAUTH_JWKS_URL=\"$OAUTH_JWKS_URL\"" >> $WEATHER_AGENT_DST_FILE_NAME
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID" >> $WEATHER_AGENT_DST_FILE_NAME
echo "SESSION_STORE_BUCKET_NAME=$SESSION_STORE_BUCKET_NAME" >> $WEATHER_AGENT_DST_FILE_NAME



ECR_REPO_WEATHER_MCP_URI=$(terraform -chdir=$ROOTDIR/$TERRAFORM_DIRECTORY output -json ecr_weather_mcp_repository_url)

cat <<EOF > $WEATHER_MCP_VALUES
image:
  repository: $ECR_REPO_WEATHER_MCP_URI

EOF


ECR_REPO_WEATHER_AGENT_URI=$(terraform -chdir=$ROOTDIR/$TERRAFORM_DIRECTORY output -json ecr_weather_agent_repository_url)

cat <<EOF > $WEATHER_AGENT_HELM_VALUES
agent:
  agent.md: |
    # Weather Assistant Agent Configuration

    ## Agent Name
    Weather Assistant

    ## Agent Description
    Weather Assistant that provides weather forecasts(US City, State) and alerts(US State)

    ## System Prompt
    You are Weather Assistant that helps the user with forecasts or alerts:
    - Provide weather forecasts for US cities for the next 3 days if no specific period is mentioned
    - When returning forecasts, always include whether the weather is good for outdoor activities for each day
    - Provide information about weather alerts for US cities when requested

mcp:
  mcp.json: |
    {
      "mcpServers": {
        "weather-mcp-http": {
          "url": "http://weather-mcp.mcp-servers:8080/mcp"
        }
      }
    }

image:
  repository: $ECR_REPO_WEATHER_AGENT_URI
env:
  OAUTH_JWKS_URL: $OAUTH_JWKS_URL
  SESSION_STORE_BUCKET_NAME: $SESSION_STORE_BUCKET_NAME

EOF
