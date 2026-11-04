"""Harness orchestrator executing deterministic review conforming to PRD.md M0 and D-009."""

import time
from pathlib import Path
from typing import Any

from compliance_review.checks.deterministic.citation import check_citations
from compliance_review.checks.deterministic.code import check_code
from compliance_review.checks.deterministic.disclosure import check_disclosure
from compliance_review.checks.deterministic.structure import check_structure
from compliance_review.db.repository import (
    get_submission_by_id,
    record_deterministic_execution_and_verdicts,
    record_retrieval_event,
)
from compliance_review.errors import IngestError
from compliance_review.ingestion.orchestrator import parse_submission_content
from compliance_review.retrieval.capability_gate import determine_capability_set


def run_deterministic_review(submission_id: int) -> str:
    """Execute capability gate and deterministic checks, persisting trace and verdicts."""
    start_time = time.perf_counter()

    sub = get_submission_by_id(submission_id)
    if sub is None:
        raise IngestError(f"Submission id={submission_id} not found in database")

    source_path = Path(sub["source_path"])
    sub_type = sub["submission_type"]

    _, extracted_data = parse_submission_content(source_path, sub_type)

    # 1. Deterministic capability gate
    cap_set, gate_reasons = determine_capability_set(sub_type, extracted_data)

    candidates: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    all_verdicts: dict[str, list[dict[str, Any]]] = {}

    # 2. Execute deterministic checks for each enabled capability
    for cap, enabled in cap_set.items():
        if not enabled:
            candidates.append(
                {
                    "capability": cap,
                    "version": "v1",
                    "reason": gate_reasons[cap],
                    "score": 0.0,
                    "stage": "capability_gate",
                }
            )
            continue

        selected.append(
            {
                "capability": cap,
                "version": "v1",
                "reason": "deterministic_gate_enabled",
                "score": 1.0,
                "stage": "capability_gate",
            }
        )
        candidates.append(
            {
                "capability": cap,
                "version": "v1",
                "reason": "active_v1_seed",
                "score": 1.0,
                "stage": "capability_gate",
            }
        )

        cap_start = time.perf_counter()
        if cap == "citation-integrity":
            verdicts = check_citations(extracted_data.get("text", ""))
        elif cap == "report-structure":
            verdicts = check_structure(
                extracted_data.get("text", ""), extracted_data.get("word_count", 0)
            )
        elif cap == "code-quality":
            verdicts = check_code(
                extracted_data.get("files", {}), source_path if source_path.is_dir() else None
            )
        elif cap == "rai-disclosure":
            verdicts = check_disclosure(
                extracted_data.get("text", ""), extracted_data.get("has_disclosure_file", False)
            )
        else:
            verdicts = []

        cap_latency = int((time.perf_counter() - cap_start) * 1000)
        all_verdicts[cap] = verdicts

        record_deterministic_execution_and_verdicts(
            submission_id=submission_id,
            capability=cap,
            verdicts_data=verdicts,
            latency_ms=cap_latency,
        )

    total_latency_ms = int((time.perf_counter() - start_time) * 1000)

    # Persist retrieval event
    record_retrieval_event(
        submission_id=submission_id,
        capability_set={c: {"enabled": en, "reason": gate_reasons[c]} for c, en in cap_set.items()},
        candidates=candidates,
        selected=selected,
        token_budget=0,
        latency_ms=total_latency_ms,
    )

    # Format trace table
    ext_id = sub["external_id"]
    trace_lines = [
        f"--- Deterministic Review Trace for Submission #{submission_id} ({ext_id}) ---",
        f"Submission Type: {sub_type} | Latency: {total_latency_ms} ms",
        "\nCapabilities Gated:",
    ]
    for cap, enabled in cap_set.items():
        status = "[ENABLED] " if enabled else "[DISABLED]"
        trace_lines.append(f"  {status} {cap:20s} : {gate_reasons[cap]}")

    trace_lines.append("\nDeterministic Verdicts:")
    for cap, verdicts in all_verdicts.items():
        trace_lines.append(f"  Capability: {cap}")
        for v in verdicts:
            c_id = v["check_id"]
            verd = v["verdict"]
            sev = v["severity"]
            ev_txt = v.get("evidence_text")
            trace_lines.append(f"    - {c_id:25s} -> {verd:8s} ({sev}) : {ev_txt}")

    return "\n".join(trace_lines)
