#!/bin/bash

WEB_DST_FILE_NAME=${WEB_DST_FILE_NAME:-../weather/web/.env}
echo "> Injecting values into $WEB_DST_FILE_NAME"
echo "" > $WEB_DST_FILE_NAME

echo "> Parsing Terraform outputs"
TERRAFORM_OUTPUTS_MAP=$(terraform output --json outputs_map)
#echo $TERRAFORM_OUTPUTS_MAP
OAUTH_USER_POOL_ID=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_userpool_id")
OAUTH_CLIENT_ID=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_client_id")
OAUTH_CLIENT_SECRET=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_client_secret")
OAUTH_SIGN_IN_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_sign_in_url")
OAUTH_LOGOUT_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_logout_url")
OAUTH_WELL_KNOWN_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_well_known_url")
OAUTH_JWKS_URL=$(echo "$TERRAFORM_OUTPUTS_MAP" | jq -r ".cognito_jwks_url")

echo "OAUTH_USER_POOL_ID=$OAUTH_USER_POOL_ID"
echo "OAUTH_CLIENT_ID=$OAUTH_CLIENT_ID"
echo "OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET:0:3}....redacted..."
echo "OAUTH_SIGN_IN_URL=$OAUTH_SIGN_IN_URL"
echo "OAUTH_LOGOUT_URL=$OAUTH_LOGOUT_URL"
echo "OAUTH_WELL_KNOWN_URL=$OAUTH_WELL_KNOWN_URL"
echo "OAUTH_JWKS_URL=$OAUTH_JWKS_URL"

echo "> Setting user passwords for Alice and Bob"
aws cognito-idp admin-set-user-password --user-pool-id $OAUTH_USER_POOL_ID --username Alice --password "Passw0rd@" --permanent
aws cognito-idp admin-set-user-password --user-pool-id $OAUTH_USER_POOL_ID --username Bob --password "Passw0rd@" --permanent

echo "OAUTH_CLIENT_ID=\"$OAUTH_CLIENT_ID\"" >> $WEB_DST_FILE_NAME
echo "OAUTH_CLIENT_SECRET=\"$OAUTH_CLIENT_SECRET\"" >> $WEB_DST_FILE_NAME
echo "OAUTH_LOGOUT_URL=\"$OAUTH_LOGOUT_URL\"" >> $WEB_DST_FILE_NAME
echo "OAUTH_WELL_KNOWN_URL=\"$OAUTH_WELL_KNOWN_URL\"" >> $WEB_DST_FILE_NAME
echo "OAUTH_JWKS_URL=\"$OAUTH_JWKS_URL\"" >> $WEB_DST_FILE_NAME

echo "> Done"
