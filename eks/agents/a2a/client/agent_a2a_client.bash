alias ecr-login="aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO 2>/dev/null"

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
