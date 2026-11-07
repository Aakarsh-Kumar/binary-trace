"""K-run execution loop and agreement computation conforming to US-19, US-28."""

import hashlib
from typing import Any

from compliance_review.checks.deterministic.citation import check_citations
from compliance_review.checks.deterministic.code import check_code
from compliance_review.checks.deterministic.disclosure import check_disclosure
from compliance_review.checks.deterministic.structure import check_structure
from compliance_review.checks.model_based.citation import evaluate_citation_model_checks
from compliance_review.checks.model_based.code import evaluate_code_model_checks
from compliance_review.checks.model_based.disclosure import (
    evaluate_disclosure_model_checks,
)
from compliance_review.checks.model_based.structure import (
    evaluate_structure_model_checks,
)
from compliance_review.evidence.verifier import normalize_span


def compute_k_run_agreement(
    runs_verdicts: list[list[dict[str, Any]]],
) -> dict[str, dict[str, float]]:
    """Compute per-check verdict agreement and evidence Jaccard similarity across k runs (US-28)."""
    if not runs_verdicts:
        return {}

    k = len(runs_verdicts)
    # Collect verdicts by check_id across runs
    check_runs: dict[str, list[dict[str, Any]]] = {}
    for run in runs_verdicts:
        for v in run:
            c_id = v["check_id"]
            check_runs.setdefault(c_id, []).append(v)

    agreement_metrics: dict[str, dict[str, float]] = {}

    for c_id, v_list in check_runs.items():
        # 1. Verdict agreement: frequency of most common verdict / k
        verdict_counts: dict[str, int] = {}
        for v in v_list:
            verd = v["verdict"]
            verdict_counts[verd] = verdict_counts.get(verd, 0) + 1
        max_verdict_count = max(verdict_counts.values()) if verdict_counts else 0
        agreement = max_verdict_count / k

        # 2. Evidence Jaccard similarity across runs that flagged
        flagged_evidences: list[set[str]] = []
        for v in v_list:
            if v["verdict"] == "flag" and v.get("evidence_text"):
                norm = normalize_span(str(v["evidence_text"]))
                words = set(norm.split())
                if words:
                    flagged_evidences.append(words)

        if len(flagged_evidences) >= 2:
            pairwise_jaccard: list[float] = []
            for i in range(len(flagged_evidences)):
                for j in range(i + 1, len(flagged_evidences)):
                    s1 = flagged_evidences[i]
                    s2 = flagged_evidences[j]
                    intersection = len(s1 & s2)
                    union = len(s1 | s2)
                    pairwise_jaccard.append(intersection / union if union > 0 else 1.0)
            avg_jaccard = sum(pairwise_jaccard) / len(pairwise_jaccard) if pairwise_jaccard else 1.0
        else:
            avg_jaccard = 1.0

        agreement_metrics[c_id] = {
            "agreement": round(float(agreement), 4),
            "evidence_jaccard": round(float(avg_jaccard), 4),
        }

    return agreement_metrics


# Alias per D-031
compute_agreement = compute_k_run_agreement


def run_single_capability_execution(
    capability: str,
    version: str,
    checklist_items: list[dict[str, Any]],
    extracted_data: dict[str, Any],
    source_path: Any,
    run_index: int = 1,
    deterministic_only: bool = False,
    client: Any = None,
) -> tuple[list[dict[str, Any]], str, str, str, dict[str, Any], str, int]:
    """Execute deterministic and model checks for a single run_index.

    Returns:
      (verdicts, model_name, model_digest, prompt_sha256, parsed_output, status, latency_ms)
    """
    # 1. Deterministic checks
    deterministic_verdicts: list[dict[str, Any]] = []
    if capability == "citation-integrity":
        deterministic_verdicts = check_citations(extracted_data.get("text", ""))
    elif capability == "report-structure":
        deterministic_verdicts = check_structure(
            extracted_data.get("text", ""), extracted_data.get("word_count", 0)
        )
    elif capability == "code-quality":
        files_dict = extracted_data.get("files", {})
        dir_path = source_path if getattr(source_path, "is_dir", lambda: False)() else None
        deterministic_verdicts = check_code(files_dict, dir_path)
    elif capability == "rai-disclosure":
        deterministic_verdicts = check_disclosure(
            extracted_data.get("text", ""),
            extracted_data.get("has_disclosure_file", False),
        )

    # Filter to only the checks present in this skill's checklist
    skill_check_ids = {c["id"] for c in checklist_items}
    active_det_verdicts = [v for v in deterministic_verdicts if v["check_id"] in skill_check_ids]

    # 2. Model-based checks (if not deterministic_only and model items exist)
    model_items = [c for c in checklist_items if not c.get("deterministic_only", False)]
    if deterministic_only or not model_items:
        prompt_sha256 = hashlib.sha256(b"deterministic_only").hexdigest()
        return (
            active_det_verdicts,
            "deterministic_harness",
            "0" * 64,
            prompt_sha256,
            {"verdicts": active_det_verdicts},
            "ok",
            10,
        )

    # Execute model-based checks for this capability
    status: str = "ok"
    model_verdicts: list[dict[str, Any]] = []
    digest: str = "0" * 64
    latency_ms: int = 0
    raw_output: str = ""

    if capability == "citation-integrity":
        status, model_verdicts, digest, latency_ms, raw_output = evaluate_citation_model_checks(
            checklist_items,
            extracted_data,
            version=version,
            run_index=run_index,
            client=client,
        )
    elif capability == "report-structure":
        status, model_verdicts, digest, latency_ms, raw_output = evaluate_structure_model_checks(
            checklist_items,
            extracted_data,
            version=version,
            run_index=run_index,
            client=client,
        )
    elif capability == "code-quality":
        status, model_verdicts, digest, latency_ms, raw_output = evaluate_code_model_checks(
            checklist_items,
            extracted_data,
            version=version,
            run_index=run_index,
            client=client,
        )
    elif capability == "rai-disclosure":
        status, model_verdicts, digest, latency_ms, raw_output = evaluate_disclosure_model_checks(
            checklist_items,
            extracted_data,
            version=version,
            run_index=run_index,
            client=client,
        )

    prompt_sha256 = hashlib.sha256(raw_output.encode("utf-8")).hexdigest()
    combined_verdicts = active_det_verdicts + model_verdicts

    return (
        combined_verdicts,
        "qwen3:4b",
        digest,
        prompt_sha256,
        {"verdicts": combined_verdicts},
        status,
        latency_ms,
    )
