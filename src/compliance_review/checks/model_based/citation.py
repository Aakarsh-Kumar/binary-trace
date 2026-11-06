"""Model-based citation integrity checks conforming to ARCHITECTURE.md §3 and US-20."""

from typing import Any

from compliance_review.model.prompts import build_evaluation_prompt
from compliance_review.model.schema_validation import execute_model_evaluation_with_retry


def evaluate_citation_model_checks(
    checklist_items: list[dict[str, Any]],
    extracted_data: dict[str, Any],
    version: str = "v2",
    run_index: int = 1,
    client: Any = None,
) -> tuple[str, list[dict[str, Any]], str, int, str]:
    """Evaluate citation model-based checks (claim support, context accuracy)."""
    model_items = [item for item in checklist_items if not item.get("deterministic_only", False)]
    if not model_items:
        return "ok", [], "0" * 64, 0, ""

    submission_text = str(extracted_data.get("text", ""))
    prompt = build_evaluation_prompt(
        capability="citation-integrity",
        version=version,
        submission_type="prose",
        checklist=model_items,
        submission_text=submission_text,
    )

    status, model_output, digest, latency, raw = execute_model_evaluation_with_retry(
        prompt=prompt,
        capability="citation-integrity",
        run_index=run_index,
        client=client,
    )

    verdicts: list[dict[str, Any]] = []
    if model_output is not None:
        for v in model_output.verdicts:
            vd = v.model_dump()
            vd["check_source"] = "model"
            verdicts.append(vd)

    return status, verdicts, digest, latency, raw
