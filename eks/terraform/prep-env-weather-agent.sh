#!/bin/bash

WEATHER_DST_FILE_NAME=${WEATHER_DST_FILE_NAME:-../weather/.env}
echo "> Injecting values into $WEATHER_DST_FILE_NAME"
echo "" > $WEATHER_DST_FILE_NAME

echo "> Parsing Terraform outputs"
TERRAFORM_OUTPUTS_MAP=$(terraform output --json outputs_map)
#echo $TERRAFORM_OUTPUTS_MAP
OAUTH_JWKS_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_jwks_url")
BEDROCK_MODEL_ID=$(terraform output -json bedrock_model_id)
SESSION_STORE_BUCKET_NAME=$(terraform output -json weather_agent_session_store_bucket_name)

echo "OAUTH_JWKS_URL=$OAUTH_JWKS_URL"
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID"
echo "SESSION_STORE_BUCKET_NAME=$SESSION_STORE_BUCKET_NAME"

echo "OAUTH_JWKS_URL=\"$OAUTH_JWKS_URL\"" >> $WEATHER_DST_FILE_NAME
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID" >> $WEATHER_DST_FILE_NAME
echo "SESSION_STORE_BUCKET_NAME=$SESSION_STORE_BUCKET_NAME" >> $WEATHER_DST_FILE_NAME
echo "> Done"

WEATHER_MCP_HELM_VALUES_DST_FILE_NAME=${WEATHER_MCP_HELM_VALUES_DST_FILE_NAME:-../weather/mcp-servers/weather-mcp-server/helm/workshop-values.yaml}
ECR_REPO_WEATHER_MCP_URI=$(terraform output -json ecr_weather_mcp_repository_url)
echo "> Creating $WEATHER_MCP_HELM_VALUES_DST_FILE_NAME"
echo "ECR_REPO_WEATHER_MCP_URI=$ECR_REPO_WEATHER_MCP_URI"
cat <<EOF > $WEATHER_MCP_HELM_VALUES_DST_FILE_NAME
image:
  repository: $ECR_REPO_WEATHER_MCP_URI

EOF

WEATHER_AGENT_HELM_VALUES_DST_FILE_NAME=${WEATHER_AGENT_HELM_VALUES_DST_FILE_NAME:-../weather/helm/workshop-values.yaml}
ECR_REPO_WEATHER_AGENT_URI=$(terraform output -json ecr_weather_agent_repository_url)
echo "> Creating $WEATHER_AGENT_HELM_VALUES_DST_FILE_NAME"
echo "ECR_REPO_WEATHER_AGENT_URI=$ECR_REPO_WEATHER_AGENT_URI"
cat <<EOF > $WEATHER_AGENT_HELM_VALUES_DST_FILE_NAME
image:
  repository: $ECR_REPO_WEATHER_AGENT_URI
env:
  OAUTH_JWKS_URL: "$OAUTH_JWKS_URL"
  SESSION_STORE_BUCKET_NAME: $SESSION_STORE_BUCKET_NAME
mcp:
  mcp.json: |
    {
      "mcpServers": {
        "weather-mcp-http": {
          "url": "http://weather-mcp.mcp-servers:8080/mcp"
        }
      }
    }
EOF
