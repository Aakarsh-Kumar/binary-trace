"""Schema validation and retry logic conforming to ARCHITECTURE.md §5.3 and US-21."""

import json
from typing import Any

from pydantic import ValidationError

from compliance_review.errors import ModelSchemaError
from compliance_review.model.prompts import build_retry_prompt
from compliance_review.model.qwen_client import call_qwen
from compliance_review.skills.schema import ModelOutput


def parse_and_validate_model_output(
    raw_text: str,
    expected_capability: str | None = None,
) -> ModelOutput:
    """Parse JSON string and validate against ModelOutput schema.

    Raises ModelSchemaError if JSON is malformed, extra keys exist, or required fields fail.
    """
    clean_text = raw_text.strip()
    # Strip markdown fenced code blocks if present
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError as exc:
        raise ModelSchemaError(f"Malformed JSON output: {exc}") from exc

    if not isinstance(data, dict):
        raise ModelSchemaError("Model output must be a JSON object")

    try:
        output = ModelOutput.model_validate(data)
    except ValidationError as exc:
        raise ModelSchemaError(f"ModelOutput schema validation failed: {exc}") from exc

    if expected_capability and output.capability != expected_capability:
        raise ModelSchemaError(
            f"Capability mismatch: expected '{expected_capability}', got '{output.capability}'"
        )

    return output


def execute_model_evaluation_with_retry(
    prompt: str,
    capability: str,
    run_index: int = 1,
    client: Any = None,
) -> tuple[str, ModelOutput | None, str, int, str]:
    """Execute model evaluation with EXACTLY one schema retry on failure.

    Returns:
      (status, model_output, model_digest, latency_ms, raw_output)
      status is 'ok' or 'schema_error'.
    """
    # Attempt 1
    try:
        raw_text, digest, latency_1 = call_qwen(prompt, run_index=run_index, client=client)
        total_latency = latency_1
    except Exception as exc:
        return "error", None, "0" * 64, 0, str(exc)

    try:
        model_output = parse_and_validate_model_output(raw_text, expected_capability=capability)
        return "ok", model_output, digest, total_latency, raw_text
    except ModelSchemaError as err1:
        error_msg = str(err1)

    # Attempt 2 (Retry EXACTLY once with validation error appended)
    retry_prompt = build_retry_prompt(validation_error=error_msg, raw_output=raw_text)
    try:
        raw_text_2, digest, latency_2 = call_qwen(retry_prompt, run_index=run_index, client=client)
        total_latency += latency_2
    except Exception as exc:
        return "schema_error", None, digest, total_latency, str(exc)

    try:
        model_output = parse_and_validate_model_output(raw_text_2, expected_capability=capability)
        return "ok", model_output, digest, total_latency, raw_text_2
    except ModelSchemaError:
        # Second failure: return status='schema_error' with no verdicts (US-21)
        return "schema_error", None, digest, total_latency, raw_text_2
