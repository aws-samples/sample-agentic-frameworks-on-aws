#!/usr/bin/env python3
"""CLI for managing LlamaIndex Workflow deployments on AWS Bedrock AgentCore.

Covers the full lifecycle — deploy, invoke, monitor, and teardown — plus
direct access to all AgentCore entrypoint actions (run, poll, events,
human-in-the-loop, cancel, list).

Usage:
    python cli.py deploy   --deployment-role <ARN> --execution-role <ARN>
    python cli.py invoke   --gov-id doc.pdf --utility-bill doc.pdf --bank-statement doc.pdf
    python cli.py status   [--handler-id ID]
    python cli.py events   [--handler-id ID]
    python cli.py cancel   [--handler-id ID]
    python cli.py send-event --event '{"feedback": "approved"}'
    python cli.py workflows
    python cli.py handlers [--workflow NAME] [--status STATUS]
    python cli.py destroy
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import uuid
from pathlib import Path

import boto3
import httpx

from llama_agents.agentcore.deploy import AgentCoreDeployer, DeployedRuntime

PROJECT_DIR = Path(__file__).parent
METADATA_FILE = PROJECT_DIR / ".agentcore" / "deployment.json"


def _save_metadata(runtime: DeployedRuntime) -> None:
    """Persist deployment metadata for later commands."""
    METADATA_FILE.parent.mkdir(exist_ok=True)
    METADATA_FILE.write_text(json.dumps(runtime.to_dict(), indent=2))


def _load_metadata() -> DeployedRuntime:
    """Load deployment metadata from a previous deploy."""
    if not METADATA_FILE.exists():
        raise FileNotFoundError("No deployment found. Run 'deploy' first.")
    return DeployedRuntime.from_dict(json.loads(METADATA_FILE.read_text()))


def _get_deployer(profile: str | None, region: str | None = None) -> tuple[AgentCoreDeployer, DeployedRuntime]:
    """Build an AgentCoreDeployer + metadata for post-deploy commands."""
    meta = _load_metadata()
    deployer = AgentCoreDeployer(
        session=boto3.Session(region_name=region or meta.region, profile_name=profile),
        deployment_role="",
        execution_role="",
    )
    return deployer, meta


def _invoke(args: argparse.Namespace, payload: dict) -> dict:
    """Send a payload to the deployed (or local) runtime and return the response."""
    if args.local:
        resp = httpx.post("http://localhost:8080/invocations", json=payload)
        resp.raise_for_status()
        return resp.json()

    deployer, meta = _get_deployer(args.profile)
    session_id = payload.get("handler_id") or str(uuid.uuid4())
    return deployer.invoke(meta.arn, payload, session_id=session_id)


def _decode_result(data: dict) -> dict:
    """Deserialize the nested pydantic/envelope result using JsonSerializer."""
    raw = data.get("result")
    if not raw or not isinstance(raw, str):
        return data

    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return data

    from workflows.context.serializers import JsonSerializer

    deserialized = JsonSerializer().deserialize_value(parsed)

    # deserialized is an EventEnvelopeWithMetadata; extract the inner event value
    if hasattr(deserialized, "value"):
        result = deserialized.value
    else:
        result = deserialized

    data = {**data, "result": result}
    return data


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_deploy(args: argparse.Namespace) -> None:
    """Build, push, and deploy the workflow to AgentCore."""
    session = boto3.Session(region_name=args.region, profile_name=args.profile)
    deployer = AgentCoreDeployer(
        session=session,
        deployment_role=args.deployment_role,
        execution_role=args.execution_role,
    )

    runtime = deployer.deploy(project_dir=PROJECT_DIR)
    _save_metadata(runtime)

    print(f"\nDeployed successfully!")
    print(f"  Runtime: {runtime.name}")
    print(f"  ARN:     {runtime.arn}")
    print(f"\nTest with:")
    print(f"  python cli.py invoke \\")
    print(f"    --gov-id sample_docs/drivers_license.pdf \\")
    print(f"    --utility-bill sample_docs/utility_bill.pdf \\")
    print(f"    --bank-statement sample_docs/bank_statement.pdf")


def _encode_doc(file_path: str, doc_type: str) -> dict:
    """Read a file from disk and return a KYCDocument-shaped dict."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return {
        "file_b64": base64.b64encode(path.read_bytes()).decode(),
        "file_name": path.name,
        "doc_type": doc_type,
    }


def cmd_invoke(args: argparse.Namespace) -> None:
    """Run the KYC workflow with document files."""
    session_id = args.session_id or str(uuid.uuid4())
    payload: dict = {
        "action": "run" if args.wait else "run_nowait",
        "handler_id": session_id,
        "start_event": {
            "documents": [
                _encode_doc(args.gov_id, "government_id"),
                _encode_doc(args.utility_bill, "utility_bill"),
                _encode_doc(args.bank_statement, "bank_statement"),
            ]
        },
    }
    if args.workflow:
        payload["workflow"] = args.workflow

    result = _invoke(args, payload)
    _print_json(_decode_result(result))
    print(f"\nSession ID: {session_id}")
    print(f"  Re-use with: --session-id {session_id}")


def cmd_status(args: argparse.Namespace) -> None:
    """Check the status and result of a workflow handler."""
    if not args.handler_id:
        raise SystemExit("Error: --handler-id is required for 'status'")
    payload = {
        "action": "get_result",
        "handler_id": args.handler_id,
    }
    _print_json(_decode_result(_invoke(args, payload)))


def cmd_events(args: argparse.Namespace) -> None:
    """Retrieve recorded events for a workflow handler."""
    if not args.handler_id:
        raise SystemExit("Error: --handler-id is required for 'events'")
    payload: dict = {
        "action": "get_events",
        "handler_id": args.handler_id,
    }
    if args.after_sequence is not None:
        payload["after_sequence"] = args.after_sequence
    if args.limit is not None:
        payload["limit"] = args.limit
    _print_json(_invoke(args, payload))


def cmd_send_event(args: argparse.Namespace) -> None:
    """Send an event into a running workflow (human-in-the-loop)."""
    if not args.handler_id:
        raise SystemExit("Error: --handler-id is required for 'send-event'")
    event_data = json.loads(args.event)
    payload: dict = {
        "action": "send_event",
        "handler_id": args.handler_id,
        "event": event_data,
    }
    if args.step:
        payload["step"] = args.step
    _print_json(_invoke(args, payload))


def cmd_cancel(args: argparse.Namespace) -> None:
    """Cancel a running workflow handler."""
    if not args.handler_id:
        raise SystemExit("Error: --handler-id is required for 'cancel'")
    payload: dict = {
        "action": "cancel",
        "handler_id": args.handler_id,
        "purge": args.purge,
    }
    _print_json(_invoke(args, payload))


def cmd_workflows(args: argparse.Namespace) -> None:
    """List registered workflows."""
    _print_json(_invoke(args, {"action": "list_workflows"}))


def cmd_handlers(args: argparse.Namespace) -> None:
    """List workflow handlers, optionally filtered."""
    payload: dict = {"action": "list_handlers"}
    if args.workflow:
        payload["workflow"] = args.workflow
    if args.status:
        payload["status"] = args.status
    _print_json(_invoke(args, payload))


def cmd_destroy(args: argparse.Namespace) -> None:
    """Tear down the deployment and clean up AWS resources."""
    deployer, meta = _get_deployer(args.profile)
    deployer.destroy_from_metadata(meta)
    print("Cleanup complete.")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add --local and --profile flags shared across invoke-style commands."""
    parser.add_argument("--local", action="store_true", help="Target localhost:8080 instead of deployed runtime")
    parser.add_argument("--profile", default=None, help="AWS CLI profile name")


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Manage LlamaIndex Workflow deployments on AWS Bedrock AgentCore"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- deploy --
    deploy_p = sub.add_parser("deploy", help="Build, push, and deploy to AgentCore")
    deploy_p.add_argument("--deployment-role", required=True, help="IAM role ARN for CodeBuild")
    deploy_p.add_argument("--execution-role", required=True, help="IAM role ARN for AgentCore Runtime")
    deploy_p.add_argument("--region", default="us-east-1", help="AWS region")
    deploy_p.add_argument("--profile", default=None, help="AWS CLI profile name")

    # -- invoke --
    invoke_p = sub.add_parser("invoke", help="Run the KYC workflow with document files")
    invoke_p.add_argument("--gov-id", required=True, help="Path to Government ID PDF")
    invoke_p.add_argument("--utility-bill", required=True, help="Path to Utility Bill PDF")
    invoke_p.add_argument("--bank-statement", required=True, help="Path to Bank Statement PDF")
    invoke_p.add_argument("--workflow", help="Specific workflow name (default: auto-detected)")
    invoke_p.add_argument("--session-id", default=None, help="Session ID (reuse to get cached results)")
    invoke_p.add_argument("--no-wait", dest="wait", action="store_false", default=True,
                          help="Return immediately without waiting for completion")
    _add_common_args(invoke_p)

    # -- status --
    status_p = sub.add_parser("status", help="Check handler status and result")
    status_p.add_argument("--handler-id", required=True, help="Handler/session ID to check")
    _add_common_args(status_p)

    # -- events --
    events_p = sub.add_parser("events", help="Retrieve recorded workflow events")
    events_p.add_argument("--handler-id", required=True, help="Handler/session ID")
    events_p.add_argument("--after-sequence", type=int, default=None, help="Only events after this sequence number")
    events_p.add_argument("--limit", type=int, default=None, help="Max events to return")
    _add_common_args(events_p)

    # -- send-event --
    send_event_p = sub.add_parser("send-event", help="Send event into a running workflow (human-in-the-loop)")
    send_event_p.add_argument("--handler-id", required=True, help="Handler/session ID")
    send_event_p.add_argument("--event", required=True, help="JSON event payload")
    send_event_p.add_argument("--step", default=None, help="Target step name")
    _add_common_args(send_event_p)

    # -- cancel --
    cancel_p = sub.add_parser("cancel", help="Cancel a running workflow handler")
    cancel_p.add_argument("--handler-id", required=True, help="Handler/session ID to cancel")
    cancel_p.add_argument("--purge", action="store_true", help="Also purge handler data")
    _add_common_args(cancel_p)

    # -- workflows --
    workflows_p = sub.add_parser("workflows", help="List registered workflows")
    _add_common_args(workflows_p)

    # -- handlers --
    handlers_p = sub.add_parser("handlers", help="List workflow handlers")
    handlers_p.add_argument("--workflow", default=None, help="Filter by workflow name")
    handlers_p.add_argument("--status", default=None, help="Filter by status")
    _add_common_args(handlers_p)

    # -- destroy --
    destroy_p = sub.add_parser("destroy", help="Tear down deployment and clean up")
    destroy_p.add_argument("--profile", default=None, help="AWS CLI profile name")

    args = parser.parse_args()
    commands = {
        "deploy": cmd_deploy,
        "invoke": cmd_invoke,
        "status": cmd_status,
        "events": cmd_events,
        "send-event": cmd_send_event,
        "cancel": cmd_cancel,
        "workflows": cmd_workflows,
        "handlers": cmd_handlers,
        "destroy": cmd_destroy,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
