#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"


kubectl -n ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_WEATHER_MCP_NAME}
kubectl -n ${KUBERNETES_APP_WEATHER_MCP_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_WEATHER_MCP_NAME}

kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_WEATHER_AGENT_NAME}
kubectl -n ${KUBERNETES_APP_WEATHER_AGENT_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_WEATHER_AGENT_NAME}

kubectl -n ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_TRAVEL_AGENT_NAME}
kubectl -n ${KUBERNETES_APP_TRAVEL_AGENT_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_TRAVEL_AGENT_NAME}


kubectl -n ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
   rollout restart deployment/${KUBERNETES_APP_AGENT_UI_NAME}
kubectl -n ${KUBERNETES_APP_AGENT_UI_NAMESPACE} \
   rollout status deployment/${KUBERNETES_APP_AGENT_UI_NAME}
