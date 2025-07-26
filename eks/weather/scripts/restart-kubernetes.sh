#!/bin/bash


kubectl -n ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_WEATHER_MCP_NAME}
kubectl -n ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_WEATHER_MCP_NAME}

kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_WEATHER_AGENT_NAME}
kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_WEATHER_AGENT_NAME}

kubectl -n ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_AGENT_UI_NAME}
kubectl -n ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_AGENT_UI_NAME}
