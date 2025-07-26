#!/bin/bash

TRAVEL_DST_FILE_NAME=${TRAVEL_DST_FILE_NAME:-../travel/.env}
echo "> Injecting values into $TRAVEL_DST_FILE_NAME"
echo "" >$TRAVEL_DST_FILE_NAME

echo "> Parsing Terraform outputs"
TERRAFORM_OUTPUTS_MAP=$(terraform output --json outputs_map)
#echo $TERRAFORM_OUTPUTS_MAP
OAUTH_JWKS_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_jwks_url")
BEDROCK_MODEL_ID=$(terraform output -json bedrock_model_id)
SESSION_STORE_BUCKET_NAME=$(terraform output -json travel_agent_session_store_bucket_name)
echo "OAUTH_JWKS_URL=$OAUTH_JWKS_URL"
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID"
echo "SESSION_STORE_BUCKET_NAME=$SESSION_STORE_BUCKET_NAME"

echo "OAUTH_JWKS_URL=\"$OAUTH_JWKS_URL\"" >>$TRAVEL_DST_FILE_NAME
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID" >>$TRAVEL_DST_FILE_NAME
echo "SESSION_STORE_BUCKET_NAME=$SESSION_STORE_BUCKET_NAME" >>$TRAVEL_DST_FILE_NAME

echo "> Done"

TRAVEL_HELM_VALUES_DST_FILE_NAME=${TRAVEL_HELM_VALUES_DST_FILE_NAME:-../travel/helm/agent-values.yaml}
ECR_REPO_TRAVEL_AGENT_URI=$(terraform output -json ecr_travel_agent_repository_url)
echo "> Creating $TRAVEL_HELM_VALUES_DST_FILE_NAME"
echo "ECR_REPO_TRAVEL_AGENT_URI=$ECR_REPO_TRAVEL_AGENT_URI"
cat <<EOF >$TRAVEL_HELM_VALUES_DST_FILE_NAME
image:
  repository: $ECR_REPO_TRAVEL_AGENT_URI
env:
  DYNAMODB_AGENT_STATE_TABLE_NAME: $DYNAMODB_AGENT_STATE_TABLE_NAME
  OAUTH_JWKS_URL: "$OAUTH_JWKS_URL"
a2a:
  a2a_agents.json: |
    {
      "urls": [
        "http://weather-agent.weather-agent:9000/"
      ]
    }
EOF
