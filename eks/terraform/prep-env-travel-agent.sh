#!/bin/bash

TRAVEL_DST_FILE_NAME=${TRAVEL_DST_FILE_NAME:-../travel/.env}
echo "> Injecting values into $TRAVEL_DST_FILE_NAME"
echo "" >$TRAVEL_DST_FILE_NAME

echo "> Parsing Terraform outputs"
TERRAFORM_OUTPUTS_MAP=$(terraform output --json outputs_map)
#echo $TERRAFORM_OUTPUTS_MAP
OAUTH_JWKS_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_jwks_url")
BEDROCK_MODEL_ID=$(terraform output -json bedrock_model_id)
DYNAMODB_AGENT_STATE_TABLE_NAME=$(terraform output -json travel_agent_table_name)
echo "OAUTH_JWKS_URL=$OAUTH_JWKS_URL"
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID"
echo "DYNAMODB_AGENT_STATE_TABLE_NAME=$DYNAMODB_AGENT_STATE_TABLE_NAME"

echo "OAUTH_JWKS_URL=\"$OAUTH_JWKS_URL\"" >>$TRAVEL_DST_FILE_NAME
echo "BEDROCK_MODEL_ID=$BEDROCK_MODEL_ID" >>$TRAVEL_DST_FILE_NAME
echo "DYNAMODB_AGENT_STATE_TABLE_NAME=$DYNAMODB_AGENT_STATE_TABLE_NAME" >>$TRAVEL_DST_FILE_NAME

echo "> Done"

# I want to create the following file in ../weather/helm/agent-values.yaml with the following content
# image:
#   repository: 015299085168.dkr.ecr.us-west-2.amazonaws.com/agents-on-eks/weather-agent
# env:
#   DYNAMODB_AGENT_STATE_TABLE_NAME: weather-agent-huge-fish
#   OAUTH_JWKS_URL: https://cognito-idp.us-west-2.amazonaws.com/us-west-2_sel2iyxmz/.well-known/jwks.json
TRAVEL_HELM_VALUES_DST_FILE_NAME=${TRAVEL_HELM_VALUES_DST_FILE_NAME:-../travel/.env}
ECR_REPO_TRAVEL_AGENT_URI=$(terraform output -json ecr_travel_agent_repository_url)
echo "> Creating $TRAVEL_HELM_VALUES_DST_FILE_NAME"
echo "ECR_REPO_TRAVEL_AGENT_URI=$ECR_REPO_TRAVEL_AGENT_URI"
cat <<EOF >../travel/helm/agent-values.yaml
image:
  repository: $ECR_REPO_TRAVEL_AGENT_URI
env:
  DYNAMODB_AGENT_STATE_TABLE_NAME: $DYNAMODB_AGENT_STATE_TABLE_NAME
  OAUTH_JWKS_URL: "$OAUTH_JWKS_URL"
a2a:
  a2a_agents.json: |
    {
      "urls": [
        "http://REPLACE_ME_WITH_SERVICE:9000/"
      ]
    }
EOF
