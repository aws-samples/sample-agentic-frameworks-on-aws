#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

# Source environment variables
source "${SCRIPTDIR}/env.sh" --skip-terraform

# Start timing
START_TIME=$(date +%s)

echo "[$(date '+%H:%M:%S')] Starting weather-mcp container..."

# Stop and remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q '^weather-mcp$'; then
    echo "[$(date '+%H:%M:%S')] Stopping and removing existing weather-mcp container..."
    docker stop weather-mcp >/dev/null 2>&1 || true
    docker rm weather-mcp >/dev/null 2>&1 || true
fi

# Run weather mcp docker in background expose port 8080 and name it weather-mcp
echo "[$(date '+%H:%M:%S')] Running weather-mcp container from ${ECR_REPO_WEATHER_MCP_URI}..."
docker run -d -p 8080:8080 --name weather-mcp "${ECR_REPO_WEATHER_MCP_URI}"

# Wait for container to be healthy
echo "[$(date '+%H:%M:%S')] Waiting for container to be ready..."
sleep 2

# Check if container is running
if docker ps --format '{{.Names}}' | grep -q '^weather-mcp$'; then
    echo "[$(date '+%H:%M:%S')] ✓ Container weather-mcp is running"
else
    echo "[$(date '+%H:%M:%S')] ✗ Container weather-mcp failed to start"
    docker logs weather-mcp
    exit 1
fi

# End timing
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "========================================="
echo "WEATHER-MCP DEPLOYMENT SUMMARY"
echo "========================================="
printf "%-25s %3ds\n" "Total deployment time" "$DURATION"
echo "========================================="
echo ""
echo "Weather MCP container started successfully!"
echo "Container name: weather-mcp"
echo "Port: 8080"
echo ""
echo "To view logs: docker logs weather-mcp"
echo "To stop: docker stop weather-mcp"
