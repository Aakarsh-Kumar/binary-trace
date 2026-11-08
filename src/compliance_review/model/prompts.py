"""Prompt templates for model-based checks conforming to ARCHITECTURE.md §5.3 and US-19."""

from typing import Any

SYSTEM_INSTRUCTION = """You are an objective academic and technical compliance review auditor.
You must evaluate the provided student submission against a specific checklist of items.
Return ONLY a valid JSON object matching the requested schema.
Do not add markdown formatting or commentary outside the JSON."""

JSON_SCHEMA_DESCRIPTION = """Your output MUST be a JSON object with this exact structure:
{
  "capability": "<capability_name>",
  "verdicts": [
    {
      "check_id": "<exact_check_id>",
      "verdict": "pass" | "flag" | "not_applicable",
      "severity": "low" | "medium" | "high" | "critical",
      "evidence_text": "<verbatim quotation from submission, 20-200 chars, or null>",
      "evidence_location": "<exact location grammar or null>",
      "confidence": 0.87
    }
  ]
}

CRITICAL RULES:
1. "confidence" is MANDATORY on EVERY verdict (including pass and not_applicable).
   It MUST be a bare float between 0.0 and 1.0 (e.g. 0.87 or 0.95).
   Never omit confidence, never enclose it in quotes, and never prefix it with colons.
2. When verdict is 'flag', evidence_text and evidence_location are MANDATORY:
   - evidence_text MUST be a verbatim substring directly copied from the submission.
   - Evidence length must be between 20 and 200 characters.
   - QUOTATION ONLY, NO SUMMARIES: Do NOT explain or describe the issue in evidence_text.
     For example, do NOT write "syntax error" or "missing try/except".
     Copy the exact offending text or code line directly from the source.
   - Any alteration, paraphrase, or hallucination will fail automated verification.
3. evidence_location MUST strictly follow one of these three exact formats:
   - file:<relative_path>:<line_number> (e.g. file:broken.py:6 or file:server.py:9)
   - section:<slug>                     (e.g. section:methods or section:disclosure)
   - page:<page_number>                 (e.g. page:1)
4. NEGATIVE EXAMPLES OF REJECTED LOCATIONS:
   - "file:broken.py" (REJECTED: missing line number)
   - "broken.py:6" or "line:6" (REJECTED: missing file: prefix)
   - "section:References [1]" (REJECTED: invalid characters in slug)
5. When verdict is 'pass' or 'not_applicable' and no span is cited:
   - set "evidence_text": null
   - set "evidence_location": null
6. Assign a confidence in [0.5, 0.99] that reflects how clearly the evidence supports the verdict. Only use values above 0.95 when the evidence is a literal match.
"""

CAPABILITY_REVIEW_PROMPT_TEMPLATE = """{system_instruction}

{schema_description}

CAPABILITY TO EVALUATE: {capability}
SKILL VERSION: {version}

CHECKLIST ITEMS TO EVALUATE:
{checklist_formatted}

SUBMISSION CONTEXT ({submission_type}):
{type_hint}

{submission_text}

Evaluate all listed checklist items. Output the final JSON object:
"""

RETRY_PROMPT_TEMPLATE = """The previous output failed JSON or schema validation:
ERROR: {validation_error}

Please correct the output so that it strictly adheres to the schema:
{schema_description}

PREVIOUS RAW OUTPUT:
{raw_output}

Output ONLY the corrected JSON object:
"""


def format_checklist_items(checklist: list[dict[str, Any]]) -> str:
    """Format checklist items for injection into prompt."""
    lines: list[str] = []
    for item in checklist:
        guardrails = item.get("false_positive_guardrails", [])
        gr_str = f" Guardrails: {'; '.join(guardrails)}" if guardrails else ""
        lines.append(
            f"- Check ID: {item['id']}\n"
            f"  Question: {item['question']}\n"
            f"  Required Evidence Form: {item['evidence_requirement']}\n"
            f"  Severity: {item['severity']}{gr_str}"
        )
    return "\n".join(lines)


def build_evaluation_prompt(
    capability: str,
    version: str,
    submission_type: str,
    checklist: list[dict[str, Any]],
    submission_text: str,
) -> str:
    """Build the full evaluation prompt for Qwen."""
    checklist_str = format_checklist_items(checklist)
    # Truncate submission text if extremely large to respect context
    truncated_text = submission_text[:12000] if len(submission_text) > 12000 else submission_text
    type_hint = (
        "NOTE: This is a prose document. Use location format 'page:1'."
        if submission_type in ("prose", "pdf", "disclosure_section")
        else "NOTE: This is a code repository. Use location 'file:<relative_path>:<line_number>'."
    )
    return CAPABILITY_REVIEW_PROMPT_TEMPLATE.format(
        system_instruction=SYSTEM_INSTRUCTION,
        schema_description=JSON_SCHEMA_DESCRIPTION,
        capability=capability,
        version=version,
        checklist_formatted=checklist_str,
        submission_type=submission_type,
        type_hint=type_hint,
        submission_text=truncated_text,
    )


def build_retry_prompt(validation_error: str, raw_output: str) -> str:
    """Build retry prompt appending the exact schema validation failure."""
    return RETRY_PROMPT_TEMPLATE.format(
        validation_error=validation_error,
        schema_description=JSON_SCHEMA_DESCRIPTION,
        raw_output=raw_output[:2000],
    )
