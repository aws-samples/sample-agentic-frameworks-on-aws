#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

TERRAFORM_DIRECTORY="terraform"

UI_AGENT_HELM_CHART="${ROOTDIR}/weather/web/helm"
UI_AGENT_HELM_VALUES="${UI_AGENT_HELM_CHART}/workshop-ui-values.yaml"

UI_AGENT_DST_FILE_NAME="${ROOTDIR}/weather/web/.env"




TERRAFORM_OUTPUTS_MAP=$(terraform -chdir="$ROOTDIR/$TERRAFORM_DIRECTORY" output --json outputs_map)

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



ECR_REPO_AGENT_UI_URI=$(terraform -chdir="$ROOTDIR/$TERRAFORM_DIRECTORY" output -json ecr_agent_ui_repository_url)

cat <<EOF > $UI_AGENT_HELM_VALUES
image:
  repository: $ECR_REPO_AGENT_UI_URI
env:
  BASE_PATH: "${IDE_URL:+/proxy/8000}"
  BASE_URL: "${IDE_URL:-http://localhost:8000}"
EOF
