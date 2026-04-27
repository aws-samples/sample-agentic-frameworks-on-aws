"""KYC Document Verification Workflow for AgentCore deployment.

Processes KYC documents (Government ID, Utility Bill, Bank Statement) through
LlamaParse Extract, uses Claude for cross-document validation, and returns
a structured KYC decision.

Flow:
    StartEvent → extract 3 docs in parallel → collect results →
    Claude cross-validation → StopEvent with KYC decision
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import sys
from typing import Literal

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

import boto3
from llama_cloud import AsyncLlamaCloud
from pydantic import BaseModel, Field

from workflows import Context, Workflow, step
from workflows.events import Event, StartEvent, StopEvent


# =====================================================================
# Pydantic Extraction Schemas
# =====================================================================


class GovernmentID(BaseModel):
    full_name: str = Field(description="Full legal name on the ID")
    date_of_birth: str = Field(description="Date of birth (MM/DD/YYYY)")
    address: str = Field(
        description="Full residential address including apartment/unit number, city, state, and ZIP"
    )
    id_number: str = Field(description="Driver's license or ID number")
    expiration_date: str = Field(description="Document expiration date")
    document_type: str = Field(
        description="Type of ID: driver_license, passport, or state_id"
    )


class UtilityBill(BaseModel):
    account_holder_name: str = Field(description="Name of the account holder")
    service_address: str = Field(
        description="Full service address including apartment/unit, city, state, ZIP"
    )
    billing_date: str = Field(description="Date the bill was issued")
    due_date: str = Field(description="Payment due date")
    total_amount_due: float = Field(description="Total amount due in dollars")
    account_number: str = Field(description="Utility account number")
    utility_provider: str = Field(description="Name of the utility company")


class BankStatement(BaseModel):
    account_holder_name: str = Field(description="Name on the account")
    address: str = Field(
        description="Full mailing address of account holder including city, state, ZIP"
    )
    account_number: str = Field(
        description="Account number (may be partially masked)"
    )
    statement_period: str = Field(
        description="Statement date range (e.g. 'March 1 - March 31, 2026')"
    )
    opening_balance: float = Field(description="Beginning balance in dollars")
    closing_balance: float = Field(description="Ending balance in dollars")
    total_deposits: float = Field(description="Total deposits/credits in dollars")
    total_withdrawals: float = Field(
        description="Total withdrawals/debits in dollars"
    )


# =====================================================================
# Validation Schemas
# =====================================================================


class FieldComparison(BaseModel):
    check_name: str = Field(
        description="Human-readable label, e.g. 'Name Match: ID vs Utility Bill'"
    )
    doc_a_label: str = Field(description="Label of first document")
    doc_a_value: str = Field(description="The raw extracted value from document A")
    doc_b_label: str = Field(description="Label of second document")
    doc_b_value: str = Field(description="The raw extracted value from document B")
    passed: bool = Field(
        description="Whether the values plausibly refer to the same person/address"
    )
    reasoning: str = Field(
        description="Brief explanation of why this is a match or mismatch"
    )
    check_type: Literal["name", "address"] = Field(
        description="Type of comparison"
    )


class KYCDecision(BaseModel):
    checks: list[FieldComparison] = Field(
        description="All cross-document comparisons"
    )
    decision: Literal["PASS", "REVIEW", "FAIL"] = Field(
        description="PASS if all checks pass, REVIEW if mixed, FAIL if critical identity mismatch"
    )
    decision_reasoning: str = Field(
        description="Overall rationale for the KYC decision"
    )


# =====================================================================
# Workflow Events
# =====================================================================

DocType = Literal["government_id", "utility_bill", "bank_statement"]

DOC_TYPE_LABELS: dict[DocType, str] = {
    "government_id": "Government ID",
    "utility_bill": "Utility Bill",
    "bank_statement": "Bank Statement",
}

DOC_SCHEMAS: dict[str, type[BaseModel]] = {
    "Government ID": GovernmentID,
    "Utility Bill": UtilityBill,
    "Bank Statement": BankStatement,
}

REQUIRED_DOC_TYPES: set[DocType] = {"government_id", "utility_bill", "bank_statement"}


class KYCDocument(BaseModel):
    """A single KYC document submitted for verification."""

    file_b64: str = Field(description="Base64-encoded file content")
    file_name: str = Field(description="Original filename (e.g. 'drivers_license.pdf')")
    doc_type: DocType = Field(
        description="Document type: government_id, utility_bill, or bank_statement"
    )


class ExtractDocEvent(Event):
    """Request to extract a single document."""

    doc_label: str
    file_data_b64: str
    file_name: str


class ExtractionDoneEvent(Event):
    """Result of extracting a single document."""

    doc_label: str
    extracted_data: dict
    metadata: dict


class ValidationDoneEvent(Event):
    """Result of cross-document validation."""

    kyc_decision: KYCDecision
    extraction_results: dict


# =====================================================================
# Helpers
# =====================================================================


async def _extract_document(
    client: AsyncLlamaCloud,
    file_data: bytes,
    file_name: str,
    schema_class: type[BaseModel],
    label: str = "",
) -> tuple[dict, dict]:
    """Upload a document, extract with schema, return (result_dict, metadata_dict)."""
    logger.info(f"[{label}] Uploading file '{file_name}' to LlamaCloud...")
    file_obj = await client.files.create(
        file=(file_name, file_data), purpose="extract"
    )
    logger.info(f"[{label}] File uploaded (id={file_obj.id}). Starting extraction...")

    job = await client.extract.create(
        file_input=file_obj.id,
        configuration={
            "data_schema": schema_class.model_json_schema(),
            "tier": "agentic",
            "cite_sources": True,
            "confidence_scores": True,
        },
    )

    poll_count = 0
    while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):
        poll_count += 1
        logger.info(f"[{label}] Polling extraction job (attempt {poll_count}, status={job.status})...")
        await asyncio.sleep(3)
        job = await client.extract.get(job.id, expand=["extract_metadata"])

    logger.info(f"[{label}] Extraction finished with status={job.status}")
    if job.status != "COMPLETED":
        raise RuntimeError(f"Extraction failed for {label}: {job.status}")

    result = job.extract_result or {}

    metadata = {}
    if job.extract_metadata:
        em = job.extract_metadata
        if hasattr(em, "field_metadata") and em.field_metadata is not None:
            fm = em.field_metadata
            if hasattr(fm, "document_metadata") and fm.document_metadata:
                metadata = fm.document_metadata
            elif isinstance(fm, dict):
                metadata = fm
        elif isinstance(em, dict):
            metadata = em.get("field_metadata", {})

    if isinstance(result, list) and len(result) == 1:
        result = result[0]

    return result, metadata


BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-6"


async def _validate_documents_with_llm(
    id_data: dict,
    bill_data: dict,
    stmt_data: dict,
) -> KYCDecision:
    """Use Claude via Bedrock Converse to compare identity fields across documents."""
    logger.info("Starting cross-document validation with Claude via Bedrock...")

    prompt = f"""You are a KYC compliance analyst. Compare the extracted data from three
identity documents submitted by an applicant. For each pair of documents, check whether
the name and address refer to the same person/location. Handle abbreviations
(e.g., "J." for "Jason"), name ordering ("SAMPLE, ANDREW" vs "ANDREW SAMPLE"),
and address format differences ("Street" vs "St", with/without zip+4) intelligently.

Document 1 — Government ID:
{json.dumps(id_data, indent=2)}

Document 2 — Utility Bill:
{json.dumps(bill_data, indent=2)}

Document 3 — Bank Statement:
{json.dumps(stmt_data, indent=2)}

Perform these 4 comparisons:
1. Name: Government ID vs Utility Bill
2. Name: Government ID vs Bank Statement
3. Address: Government ID vs Utility Bill
4. Address: Government ID vs Bank Statement

Then decide:
- PASS: All checks pass — auto-approve
- REVIEW: Some checks fail — send to analyst for review
- FAIL: All name checks fail — different individuals, reject"""

    # Use tool-use to enforce structured output matching KYCDecision schema
    tool_name = "kyc_decision"
    client = boto3.client("bedrock-runtime")
    response = await asyncio.to_thread(
        client.converse,
        modelId=BEDROCK_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 4096},
        toolConfig={
            "tools": [
                {
                    "toolSpec": {
                        "name": tool_name,
                        "description": "Record the KYC verification decision with all cross-document comparisons.",
                        "inputSchema": {
                            "json": KYCDecision.model_json_schema()
                        },
                    }
                }
            ],
            "toolChoice": {"tool": {"name": tool_name}},
        },
    )

    logger.info("Received Bedrock response, parsing KYC decision...")
    # Extract the tool use input from the response
    for block in response["output"]["message"]["content"]:
        if "toolUse" in block and block["toolUse"]["name"] == tool_name:
            return KYCDecision.model_validate(block["toolUse"]["input"])

    raise RuntimeError("Bedrock response did not contain expected tool use output")


# =====================================================================
# KYC Workflow
# =====================================================================


class KYCWorkflow(Workflow):
    """KYC document verification workflow.

    Extracts identity data from 3 documents in parallel using LlamaParse,
    cross-validates with Claude, and returns a structured KYC decision.

    Steps:
        StartEvent → start (fan-out 3 ExtractDocEvents)
        ExtractDocEvent → extract_document (parallel, num_workers=3)
        ExtractionDoneEvent → validate_documents (collect 3, then Claude validation)
        ValidationDoneEvent → finalize → StopEvent
    """

    @step
    async def start(
        self, ctx: Context, ev: StartEvent
    ) -> ExtractDocEvent | None:
        """Decode base64 documents and fan out extraction requests.

        Expected StartEvent fields:
            documents: list[dict] - each with file_b64, file_name, and doc_type
        """
        logger.info("=== KYC Workflow START ===")
        raw_docs = ev.get("documents")
        if not raw_docs:
            raise ValueError("Must provide 'documents' list in StartEvent")

        documents = [KYCDocument.model_validate(d) for d in raw_docs]

        # --- Alternative: read files from S3 instead of base64 on the event ---
        # Expected StartEvent fields when using S3:
        #     documents: list[dict] - each with s3_bucket, s3_key, file_name, doc_type
        #
        # s3 = boto3.client("s3")
        # for doc in documents:
        #     s3_bucket = doc.get("s3_bucket")
        #     s3_key = doc.get("s3_key")
        #     logger.info(f"Downloading s3://{s3_bucket}/{s3_key}...")
        #     s3_obj = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        #     file_bytes = s3_obj["Body"].read()
        #     doc["file_b64"] = base64.b64encode(file_bytes).decode()
        # ---

        logger.info(f"Validated {len(documents)} documents: {[d.doc_type for d in documents]}")

        provided_types = {d.doc_type for d in documents}
        missing = REQUIRED_DOC_TYPES - provided_types
        if missing:
            raise ValueError(f"Missing required document types: {missing}")

        logger.info("Fanning out extraction requests for all documents...")
        for doc in documents:
            label = DOC_TYPE_LABELS[doc.doc_type]
            ctx.send_event(
                ExtractDocEvent(
                    doc_label=label, file_data_b64=doc.file_b64, file_name=doc.file_name
                )
            )

    @step(num_workers=3)
    async def extract_document(
        self, ctx: Context, ev: ExtractDocEvent
    ) -> ExtractionDoneEvent:
        """Extract structured data from a single document using LlamaParse."""
        logger.info(f"[{ev.doc_label}] Starting extraction for '{ev.file_name}'...")
        schema_class = DOC_SCHEMAS[ev.doc_label]
        client = AsyncLlamaCloud()
        file_bytes = base64.b64decode(ev.file_data_b64)

        result, metadata = await _extract_document(
            client, file_bytes, ev.file_name, schema_class, ev.doc_label
        )

        logger.info(f"[{ev.doc_label}] Extraction complete.")
        return ExtractionDoneEvent(
            doc_label=ev.doc_label,
            extracted_data=result,
            metadata=metadata,
        )

    @step
    async def validate_documents(
        self, ctx: Context, ev: ExtractionDoneEvent
    ) -> ValidationDoneEvent | None:
        """Collect all 3 extraction results, then run Claude cross-validation."""
        logger.info(f"Collected extraction result for '{ev.doc_label}', waiting for all 3...")
        results = ctx.collect_events(ev, [ExtractionDoneEvent] * 3)
        if results is None:
            return None

        logger.info("All 3 extractions collected. Starting cross-document validation...")
        extraction_results = {r.doc_label: r.extracted_data for r in results}

        kyc_decision = await _validate_documents_with_llm(
            extraction_results["Government ID"],
            extraction_results["Utility Bill"],
            extraction_results["Bank Statement"],
        )

        logger.info(f"Validation complete. Decision: {kyc_decision.decision}")
        return ValidationDoneEvent(
            kyc_decision=kyc_decision,
            extraction_results=extraction_results,
        )

    @step
    async def finalize(
        self, ctx: Context, ev: ValidationDoneEvent
    ) -> StopEvent:
        """Return the final KYC decision and all extracted data."""
        logger.info(f"=== KYC Workflow COMPLETE === Decision: {ev.kyc_decision.decision}")
        return StopEvent(
            result={
                "decision": ev.kyc_decision.decision,
                "decision_reasoning": ev.kyc_decision.decision_reasoning,
                "checks": [c.model_dump() for c in ev.kyc_decision.checks],
                "extraction_results": ev.extraction_results,
            }
        )


# Workflow instance for deployment — referenced in pyproject.toml [tool.llamadeploy.workflows]
# timeout=600s: LlamaParse agentic extraction (3 docs in parallel) + Claude
# cross-validation can realistically take 1–3 minutes. Default is 45s.
workflow = KYCWorkflow(timeout=600)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    async def main() -> None:
        docs = []
        doc_types: dict[DocType, str] = {
            "government_id": "sample_docs/drivers_license.pdf",
            "utility_bill": "sample_docs/utility_bill.pdf",
            "bank_statement": "sample_docs/bank_statement.pdf",
        }

        for doc_type, path_str in doc_types.items():
            path = Path(path_str)
            if not path.exists():
                print(f"ERROR: {path} not found")
                sys.exit(1)

            docs.append(
                {
                    "file_b64": base64.b64encode(path.read_bytes()).decode(),
                    "file_name": path.name,
                    "doc_type": doc_type,
                }
            )

        print("Running KYC workflow...")
        result = await workflow.run(documents=docs)

        print(f"\nKYC Decision: {result['decision']}")
        print(f"Reasoning: {result['decision_reasoning']}")
        print("\nChecks:")
        for check in result["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            print(f"  [{status}] {check['check_name']}")
            print(f"         {check['doc_a_label']}: {check['doc_a_value']}")
            print(f"         {check['doc_b_label']}: {check['doc_b_value']}")
            print(f"         Reasoning: {check['reasoning']}")

    asyncio.run(main())
