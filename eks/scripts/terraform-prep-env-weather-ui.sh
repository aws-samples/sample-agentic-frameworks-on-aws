#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

TERRAFORM_DIRECTORY="${ROOTDIR}/infrastructure/terraform"

# cant get environment variables from env.sh because creates circular dependency
UI_AGENT_HELM_CHART="${ROOTDIR}/manifests/helm/ui"
UI_AGENT_HELM_VALUES="${UI_AGENT_HELM_CHART}/workshop-ui-values.yaml"

UI_AGENT_DIRECTORY="${ROOTDIR}/ui"
UI_AGENT_DST_FILE_NAME="${UI_AGENT_DIRECTORY}/.env"




TERRAFORM_OUTPUTS_MAP=$(terraform -chdir="$TERRAFORM_DIRECTORY" output --json outputs_map)

OAUTH_USER_POOL_ID=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_userpool_id")
OAUTH_CLIENT_ID=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_client_id")
OAUTH_CLIENT_SECRET=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_client_secret")
OAUTH_SIGN_IN_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_sign_in_url")
OAUTH_LOGOUT_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_logout_url")
OAUTH_WELL_KNOWN_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_well_known_url")
OAUTH_JWKS_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_jwks_url")

aws cognito-idp admin-set-user-password --user-pool-id $OAUTH_USER_POOL_ID --username Alice --password "Passw0rd@" --permanent
aws cognito-idp admin-set-user-password --user-pool-id $OAUTH_USER_POOL_ID --username Bob --password "Passw0rd@" --permanent

echo "" > $UI_AGENT_DST_FILE_NAME
echo "OAUTH_CLIENT_ID=$OAUTH_CLIENT_ID" >> $UI_AGENT_DST_FILE_NAME
echo "OAUTH_CLIENT_SECRET=$OAUTH_CLIENT_SECRET" >> $UI_AGENT_DST_FILE_NAME
echo "OAUTH_LOGOUT_URL=$OAUTH_LOGOUT_URL" >> $UI_AGENT_DST_FILE_NAME
echo "OAUTH_WELL_KNOWN_URL=$OAUTH_WELL_KNOWN_URL" >> $UI_AGENT_DST_FILE_NAME
echo "OAUTH_JWKS_URL=$OAUTH_JWKS_URL" >> $UI_AGENT_DST_FILE_NAME

BASE_URL=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath={.status.loadBalancer.ingress[0].hostname})

ECR_REPO_AGENT_UI_URI=$(terraform -chdir="$TERRAFORM_DIRECTORY" output -json ecr_agent_ui_repository_url)

cat <<EOF > $UI_AGENT_HELM_VALUES
image:
  repository: $ECR_REPO_AGENT_UI_URI
env:
  AGENT_UI_ENDPOINT_URL_1: "http://weather-agent.agents/prompt"
  AGENT_UI_ENDPOINT_URL_2: "http://travel-agent.agents/prompt"
  BASE_PATH: "/"
  BASE_URL: "http://${BASE_URL:-localhost:8000}"
  AUTH_ENABLED: "false"
fastapi:
  ingress:
    enabled: true
ingress:
  enabled: true
  className: nginx
  defaultRule:
    enabled: true

EOF
