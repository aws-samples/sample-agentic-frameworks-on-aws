#!/bin/bash

echo "Login with username: Alice and password: Passw0rd@"

kubectl  port-forward svc/${KUBERNETES_APP_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
  8000:fastapi
