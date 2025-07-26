#!/bin/bash

# Uninstall the Weather Web UI from the cluster:
helm uninstall ${KUBERNETES_APP_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE}
kubectl delete secret ${KUBERNETES_APP_AGENT_UI_NAME} \
  --namespace ${KUBERNETES_APP_AGENT_UI_NAMESPACE}

# Uninstall the Weather Agent from the cluster:
helm uninstall ${KUBERNETES_APP_WEATHER_AGENT_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE}

# Uninstall the Weather MCP Server from the cluster:
helm uninstall ${KUBERNETES_APP_WEATHER_MCP_NAME} \
  --namespace ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE}
