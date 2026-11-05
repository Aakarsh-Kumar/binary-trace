"""Model-based code quality checks conforming to ARCHITECTURE.md §3 and US-20."""

from typing import Any

from compliance_review.model.prompts import build_evaluation_prompt
from compliance_review.model.schema_validation import execute_model_evaluation_with_retry


def evaluate_code_model_checks(
    checklist_items: list[dict[str, Any]],
    extracted_data: dict[str, Any],
    version: str = "v2",
    run_index: int = 1,
    client: Any = None,
) -> tuple[str, list[dict[str, Any]], str, int, str]:
    """Evaluate code model-based checks (error handling, modularity)."""
    model_items = [item for item in checklist_items if not item.get("deterministic_only", False)]
    if not model_items:
        return "ok", [], "0" * 64, 0, ""

    files_dict = extracted_data.get("files", {})
    code_snippets: list[str] = []
    for rel_path, content in list(files_dict.items())[:10]:
        code_snippets.append(f"--- File: {rel_path} ---\n{content[:2000]}")
    submission_text = "\n\n".join(code_snippets)

    prompt = build_evaluation_prompt(
        capability="code-quality",
        version=version,
        submission_type="code_repo",
        checklist=model_items,
        submission_text=submission_text,
    )

    status, model_output, digest, latency, raw = execute_model_evaluation_with_retry(
        prompt=prompt,
        capability="code-quality",
        run_index=run_index,
        client=client,
    )

    verdicts: list[dict[str, Any]] = []
    if model_output is not None:
        for v in model_output.verdicts:
            verdicts.append(v.model_dump())

    return status, verdicts, digest, latency, raw
