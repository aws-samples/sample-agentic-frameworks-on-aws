#!/usr/bin/env bash
set -euo pipefail

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$(cd ${SCRIPTDIR}/..; pwd )"
[[ -n "${DEBUG:-}" ]] && set -x
[[ -n "${DEBUG:-}" ]] && echo "executing ${BASH_SOURCE[0]} from ${BASH_SOURCE[0]}"
[[ -n "${DEBUG:-}" ]] && echo "SCRIPTDIR=$SCRIPTDIR"
[[ -n "${DEBUG:-}" ]] && echo "ROOTDIR=$ROOTDIR"

# Parse command line arguments
USE_BUILDX=false
BUILDX_PLATFORM=""
for arg in "$@"; do
    case $arg in
        --buildx-both)
            USE_BUILDX=true
            BUILDX_PLATFORM="linux/amd64,linux/arm64"
            shift
            ;;
        --buildx-amd64)
            USE_BUILDX=true
            BUILDX_PLATFORM="linux/amd64"
            shift
            ;;
        --buildx-arm64)
            USE_BUILDX=true
            BUILDX_PLATFORM="linux/arm64"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--buildx-both|--buildx-amd64|--buildx-arm64] [--help]"
            echo ""
            echo "Options:"
            echo "  --buildx-both       Use docker buildx for both amd64 and arm64 platforms"
            echo "  --buildx-amd64      Use docker buildx for amd64 platform only"
            echo "  --buildx-arm64      Use docker buildx for arm64 platform only"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Note: If no buildx flag is specified, uses standard docker build/push"
            echo "Note: Terraform preparation scripts are always skipped"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Always source env.sh with --skip-terraform flag
source "${SCRIPTDIR}/env.sh" --skip-terraform

# Login into ECR, in case we need it
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REPO_HOST} || true

# Function to wait for ECR repository to be created by Terraform
wait_for_ecr_repo() {
    local repo_name=$1
    local attempt=1

    echo "Waiting for ECR repository: ${repo_name}"

    until aws ecr describe-repositories --repository-names "${repo_name}" --region ${AWS_REGION} >/dev/null 2>&1; do
        echo "  Attempt ${attempt}: Repository ${repo_name} not ready yet, waiting 10 seconds..."
        sleep 10
        ((attempt++))
    done

    echo "✓ Repository ${repo_name} is ready"
}

# Wait for all ECR repositories to be created by Terraform
echo "Waiting for ECR repositories to be created by Terraform..."
wait_for_ecr_repo "${ECR_REPO_WEATHER_MCP_NAME}"
wait_for_ecr_repo "${ECR_REPO_WEATHER_AGENT_NAME}"
wait_for_ecr_repo "${ECR_REPO_TRAVEL_AGENT_NAME}"
wait_for_ecr_repo "${ECR_REPO_AGENT_UI_NAME}"
echo "All ECR repositories are ready ✓"
echo ""

# Function to build and push a Docker image with timing
build_and_push() {
    local image_uri=$1
    local directory=$2
    local name=$3
    local start_time=$(date +%s)

    if [[ "$USE_BUILDX" == "true" ]]; then
        echo "[$(date '+%H:%M:%S')] Building and pushing ${name} with buildx (${BUILDX_PLATFORM})..."
        docker buildx build --platform ${BUILDX_PLATFORM} --push -t ${image_uri}:latest "${directory}"
    else
        echo "[$(date '+%H:%M:%S')] Building ${name} with standard docker..."
        docker build --platform linux/amd64 -t ${image_uri}:latest "${directory}"
        echo "[$(date '+%H:%M:%S')] Pushing ${name}..."
        docker push ${image_uri}:latest
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "[$(date '+%H:%M:%S')] ✓ ${name} completed in ${duration}s"

    # Write timing to temp file for summary
    echo "${name}:${duration}" >> /tmp/build_times_$$
}

# Clean up any previous timing files
rm -f /tmp/build_times_$$



# Setup buildx only if using buildx flags
if [[ "$USE_BUILDX" == "true" ]]; then
    echo "Setting up Docker buildx for platform: ${BUILDX_PLATFORM}"
    # Only create and inspect if builder is not already created
    if ! docker buildx ls | grep -q "^builder "; then
        echo "Creating buildx node builder with --driver docker-container"
        # This is need it to get qemu properly setup
        sudo -u root touch /proc/sys/fs/binfmt_misc
        docker run --privileged --rm tonistiigi/binfmt --install all

        docker buildx ls
        docker buildx create --name builder --driver docker-container --use
        docker buildx inspect --bootstrap
        docker buildx ls
    else
        docker buildx ls
        docker buildx use builder
    fi
else
    echo "Using standard docker build and push (no buildx flags specified)"
fi


# Start all builds in parallel
TOTAL_START=$(date +%s)
echo "[$(date '+%H:%M:%S')] Starting parallel Docker builds and pushes..."

build_and_push "${ECR_REPO_WEATHER_MCP_URI}" "${WEATHER_MCP_DIRECTORY}" "MCP Server" &
PID1=$!

build_and_push "${ECR_REPO_WEATHER_AGENT_URI}" "${WEATHER_AGENT_DIRECTORY}" "Weather Agent Service" &
PID2=$!

build_and_push "${ECR_REPO_TRAVEL_AGENT_URI}" "${TRAVEL_AGENT_DIRECTORY}" "Travel Agent Service" &
PID3=$!

build_and_push "${ECR_REPO_AGENT_UI_URI}" "${UI_AGENT_DIRECTORY}" "Agent UI" &
PID4=$!

# Wait for all background processes to complete
echo "[$(date '+%H:%M:%S')] Waiting for all builds to complete..."
wait $PID1
wait $PID2
wait $PID3
wait $PID4

TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

echo ""
echo "========================================="
echo "BUILD TIMING SUMMARY"
echo "========================================="

# Sort and display individual times
if [[ -f /tmp/build_times_$$ ]]; then
    sort -t: -k2 -n /tmp/build_times_$$ | while IFS=: read name duration; do
        printf "%-25s %3ds\n" "$name" "$duration"
    done
    rm -f /tmp/build_times_$$
fi

echo "========================================="
printf "%-25s %3ds\n" "TOTAL PARALLEL TIME" "$TOTAL_DURATION"
echo "========================================="
echo ""
echo "All Docker images built and pushed successfully!"
