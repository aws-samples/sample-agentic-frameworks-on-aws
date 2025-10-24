export TF_VAR_name=$CLUSTER_NAME
export TF_VAR_cognito_additional_redirect_uri=$IDE_URL/proxy/8000/callback
export TF_VAR_cognito_additional_logout_uri=$IDE_URL/proxy/8000/

# Set the environment variables for the workshop
. $HOME/environment/scripts/env.sh

export GOPATH=~/go
export GOROOT=/usr/local/go
PATH=$PATH:$HOME/.local/bin
PATH=~/bin:~/.pyenv/shims:$PATH:/usr/local/sbin:$GOPATH/bin:$GOROOT/bin
PATH=$PATH:/usr/local/kubebuilder/bin
PATH=$HOME/.krew/bin:$PATH:~/.fzf/bin/
PATH=$PATH:/usr/local/aws-codeguru-cli/bin
PATH=$HOME/.krew/bin:$PATH
export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH

alias code=/usr/lib/code-server/bin/code-server
alias k=kubectl
alias kgn='kubectl get nodes -L beta.kubernetes.io/arch -L eks.amazonaws.com/capacityType -L beta.kubernetes.io/instance-type -L eks.amazonaws.com/nodegroup -L topology.kubernetes.io/zone -L karpenter.sh/provisioner-name -L karpenter.sh/capacity-type'
alias ll='ls -la'
alias ktx=kubectx
alias kctx=kubectx
alias kns=kubens
alias python=python3
alias pip=pip3
alias tfi='terraform init'
alias tfp='terraform plan'
alias tfy='terraform apply --auto-approve'
alias eks-node-viewer='eks-node-viewer -extra-labels=karpenter.sh/nodepool,beta.kubernetes.io/arch,topology.kubernetes.io/zone'
alias dfimage='docker run -v /var/run/docker.sock:/var/run/docker.sock --rm ghcr.io/laniksj/dfimage'
alias k=kubectl
alias kl='kubectl logs deploy/karpenter -n karpenter -f --tail=20'
alias emacs=emacs-nox
alias kns=kubens
alias kctx=kubectx

alias ecr-login="aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO 2>/dev/null"
ecr-login

alias eks-kubeconfig="aws eks --region $AWS_REGION update-kubeconfig --name $CLUSTER_NAME"
eks-kubeconfig

unset PROMPT_COMMAND
export PS1='\w:$ '

killport() {
    if [ -z "$1" ]; then
        echo "Usage: killport <port_number>"
        return 1
    fi
    lsof -ti:$1 | xargs -r kill -9
}

run_in_background() {
    if [ -z "$1" ]; then
        echo "Usage: run_in_background <port> <command>"
        return 1
    fi
    killport $1
    shift
    echo "nohup $@ >/dev/null 2>&1 &"
    nohup $@ >/dev/null 2>&1 &
    sleep 10
}

a2a_client_in_k8s() {
  local AGENT_URL="$1"
  local MESSAGE="$2"

  if [ -z "$AGENT_URL" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: a2a_client <AGENT_URL> <MESSAGE>"
    echo "Example: a2a_client http://weather-agent.agents:9000 'What is the weather in New York City?'"
    return 1
  fi

  kubectl run agent-a2a-client-temp \
    --rm -it \
    --image=ghcr.io/astral-sh/uv:python3.13-alpine \
    --restart=Never \
    --env="AGENT_URL=$AGENT_URL" \
    --env="MESSAGE=$MESSAGE" \
    -- sh -c '
      uv run --no-project --with "a2a-sdk>=0.3.8" --with httpx python - "$AGENT_URL" "$MESSAGE" <<'"'"'SCRIPT'"'"'
import asyncio
import sys
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, MessageSendParams, Part, Role, SendStreamingMessageRequest, SendStreamingMessageSuccessResponse, TaskStatusUpdateEvent, TextPart

async def send_message(agent_url: str, msg: str):
    async with httpx.AsyncClient(timeout=300) as client:
        resolver = A2ACardResolver(httpx_client=client, base_url=agent_url)
        card = await resolver.get_agent_card()
        a2a = A2AClient(client, agent_card=card)
        message = Message(kind="message", role=Role.user, parts=[Part(TextPart(kind="text", text=msg))], message_id=uuid4().hex)
        req = SendStreamingMessageRequest(id=uuid4().hex, params=MessageSendParams(message=message))
        async for chunk in a2a.send_message_streaming(req):
            if isinstance(chunk.root, SendStreamingMessageSuccessResponse) and isinstance(chunk.root.result, TaskStatusUpdateEvent):
                if chunk.root.result.status.message:
                    print(chunk.root.result.status.message.parts[0].root.text, end="", flush=True)
        print()

asyncio.run(send_message(sys.argv[1], sys.argv[2]))
SCRIPT
    '
}

a2a_client_local() {
  local AGENT_URL="$1"
  local MESSAGE="$2"

  if [ -z "$AGENT_URL" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: a2a_client_local <AGENT_URL> <MESSAGE>"
    echo "Example: a2a_client_local http://localhost:9000 'What is the weather in New York City?'"
    return 1
  fi

  uv run --no-project --with "a2a-sdk>=0.3.8" --with httpx python - "$AGENT_URL" "$MESSAGE" <<'SCRIPT'
import asyncio
import sys
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import Message, MessageSendParams, Part, Role, SendStreamingMessageRequest, SendStreamingMessageSuccessResponse, TaskStatusUpdateEvent, TextPart

async def send_message(agent_url: str, msg: str):
    async with httpx.AsyncClient(timeout=300) as client:
        resolver = A2ACardResolver(httpx_client=client, base_url=agent_url)
        card = await resolver.get_agent_card()
        a2a = A2AClient(client, agent_card=card)
        message = Message(kind="message", role=Role.user, parts=[Part(TextPart(kind="text", text=msg))], message_id=uuid4().hex)
        req = SendStreamingMessageRequest(id=uuid4().hex, params=MessageSendParams(message=message))
        async for chunk in a2a.send_message_streaming(req):
            if isinstance(chunk.root, SendStreamingMessageSuccessResponse) and isinstance(chunk.root.result, TaskStatusUpdateEvent):
                if chunk.root.result.status.message:
                    print(chunk.root.result.status.message.parts[0].root.text, end="", flush=True)
        print()

asyncio.run(send_message(sys.argv[1], sys.argv[2]))
SCRIPT
}
