"""Harness orchestrator executing full review conforming to PRD.md M1 and ARCHITECTURE.md §6."""

import time
from pathlib import Path
from typing import Any

from compliance_review.db.repository import (
    get_submission_by_id,
    record_retrieval_event,
    record_skill_execution_run,
)
from compliance_review.errors import IngestError
from compliance_review.evidence.verifier import verify_evidence
from compliance_review.harness.k_run import (
    compute_k_run_agreement,
    run_single_capability_execution,
)
from compliance_review.harness.severity_cap import apply_severity_cap_to_runs
from compliance_review.ingestion.orchestrator import parse_submission_content
from compliance_review.retrieval.capability_gate import determine_capability_set
from compliance_review.retrieval.selector import select_skill_version
from compliance_review.skills.loader import load_skill


def run_review(
    submission_id: int,
    k: int = 3,
    deterministic_only: bool = False,
    skill_status: str = "active",
    client: Any = None,
) -> str:
    """Execute full review pipeline:

    gate -> FAISS select -> checks -> evidence verify -> downgrade -> severity cap -> persist
    """
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

    # Text summary to query FAISS
    submission_text = str(extracted_data.get("text", ""))[:1000]
    query_text = f"Submission type: {sub_type}. Content: {submission_text}"

    # 2. Select skill version per enabled capability
    selected_skills_info: dict[str, dict[str, Any]] = {}

    for cap, enabled in cap_set.items():
        if not enabled:
            candidates.append(
                {
                    "capability": cap,
                    "version": "none",
                    "reason": gate_reasons[cap],
                    "score": 0.0,
                    "stage": "capability_gate",
                }
            )
            continue

        # If deterministic_only, we can select v1 directly without requiring active status
        if deterministic_only:
            sel_entry = {
                "capability": cap,
                "version": "v1",
                "reason": "deterministic_gate_enabled",
                "score": 1.0,
                "stage": "capability_gate",
            }
            selected.append(sel_entry)
            candidates.append(
                {
                    "capability": cap,
                    "version": "v1",
                    "reason": "active_v1_seed",
                    "score": 1.0,
                    "stage": "capability_gate",
                }
            )
            version_to_use = "v1"
        else:
            sel, cand_list = select_skill_version(
                capability=cap,
                query_text=query_text,
                skill_status=skill_status,
            )
            selected.append(sel.model_dump())
            for c in cand_list:
                candidates.append(c.model_dump())
            version_to_use = sel.version

        # Load skill checklist definition
        skill_file = Path("skills") / cap / version_to_use / "SKILL.md"
        frontmatter, _ = load_skill(skill_file)
        checklist_items = [item.model_dump() for item in frontmatter.checklist]
        checklist_defs = {item["id"]: item for item in checklist_items}

        selected_skills_info[cap] = {
            "version": version_to_use,
            "checklist_items": checklist_items,
            "checklist_defs": checklist_defs,
        }

    # 3. Execution, Evidence Verification, Severity Cap, and Persistence per capability
    all_final_verdicts: dict[str, list[dict[str, Any]]] = {}
    all_agreement_metrics: dict[str, dict[str, dict[str, float]]] = {}

    for cap, info in selected_skills_info.items():
        version = info["version"]
        checklist_items = info["checklist_items"]
        checklist_defs = info["checklist_defs"]

        raw_runs: list[list[dict[str, Any]]] = []
        runs_meta: list[dict[str, Any]] = []

        # Execute k runs
        for run_idx in range(1, k + 1):
            verdicts, model_name, digest, prompt_sha256, parsed, status, lat_ms = (
                run_single_capability_execution(
                    capability=cap,
                    version=version,
                    checklist_items=checklist_items,
                    extracted_data=extracted_data,
                    source_path=source_path,
                    run_index=run_idx,
                    deterministic_only=deterministic_only,
                    client=client,
                )
            )
            raw_runs.append(verdicts)
            runs_meta.append(
                {
                    "run_index": run_idx,
                    "model_name": model_name,
                    "model_digest": digest,
                    "prompt_sha256": prompt_sha256,
                    "parsed_output": parsed,
                    "status": status,
                    "latency_ms": lat_ms,
                }
            )

        # 4. Evidence Verification & Downgrade (ARCHITECTURE.md §7.2)
        for run in raw_runs:
            for v in run:
                if v["verdict"] == "flag":
                    ev_result = verify_evidence(
                        evidence_text=v.get("evidence_text"),
                        evidence_location=v.get("evidence_location"),
                        submission_data=extracted_data,
                    )
                    v["verification_result"] = ev_result
                else:
                    v["verification_result"] = None

        # 5. Severity Cap (US-22)
        capped_runs = apply_severity_cap_to_runs(raw_runs, checklist_defs)

        # 6. Compute Agreement across k runs (US-28)
        agreement = compute_k_run_agreement(capped_runs)
        all_agreement_metrics[cap] = agreement
        all_final_verdicts[cap] = capped_runs[0] if capped_runs else []

        # 7. Persist skill executions, verdicts, and evidence verifications
        for run_idx in range(1, k + 1):
            meta = runs_meta[run_idx - 1]
            record_skill_execution_run(
                submission_id=submission_id,
                capability=cap,
                version=version,
                run_index=run_idx,
                model_name=meta["model_name"],
                model_digest=meta["model_digest"],
                prompt_sha256=meta["prompt_sha256"],
                raw_output=None,
                parsed_output=meta["parsed_output"],
                status=meta["status"],
                latency_ms=meta["latency_ms"],
                verdicts_data=capped_runs[run_idx - 1],
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
    mode_str = "Deterministic-Only" if deterministic_only else f"k={k} Full Review"
    trace_lines = [
        f"--- Review Trace for Submission #{submission_id} ({ext_id}) [{mode_str}] ---",
        f"Submission Type: {sub_type} | Latency: {total_latency_ms} ms",
        "\nCapabilities Gated:",
    ]
    for cap, enabled in cap_set.items():
        status_lbl = "[ENABLED] " if enabled else "[DISABLED]"
        trace_lines.append(f"  {status_lbl} {cap:20s} : {gate_reasons[cap]}")

    trace_lines.append("\nSelected Skills:")
    for sel_item in selected:
        trace_lines.append(
            f"  - {sel_item['capability']} {sel_item['version']} "
            f"(score={sel_item['score']}, reason={sel_item['reason']})"
        )

    trace_lines.append("\nChecklist Verdicts (Run 1 / Consistency):")
    for cap, verdicts in all_final_verdicts.items():
        trace_lines.append(f"  Capability: {cap}")
        for v in verdicts:
            c_id = v["check_id"]
            verd = v["verdict"]
            sev = v["severity"]
            ev_txt = v.get("evidence_text")
            agr = all_agreement_metrics.get(cap, {}).get(c_id, {}).get("agreement", 1.0)
            trace_lines.append(
                f"    - {c_id:28s} -> {verd:20s} ({sev:8s}) [agr={agr:.2f}] : {ev_txt}"
            )

    return "\n".join(trace_lines)


def run_deterministic_review(submission_id: int) -> str:
    """Convenience wrapper for deterministic-only review."""
    return run_review(submission_id, k=1, deterministic_only=True)
