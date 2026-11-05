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
      "evidence_text": "<verbatim quotation from the submission text or null>",
      "evidence_location": "<location string or null>",
      "confidence": <float between 0.0 and 1.0>
    }
  ]
}

CRITICAL RULES FOR EVIDENCE:
1. When verdict is 'flag', evidence_text and evidence_location are MANDATORY.
2. evidence_text MUST be an EXACT, VERBATIM substring directly copied from the submission.
   Do not paraphrase or edit characters. Any alteration will fail automated verification.
3. evidence_location MUST strictly conform to the location grammar:
   - page:<page_number>              (e.g. page:1)
   - file:<relative_path>:<line_num> (e.g. file:src/main.py:12)
   - section:<section_slug>          (e.g. section:methods, section:disclosure)
4. When verdict is 'pass' or 'not_applicable' and no span is cited,
   evidence_text and evidence_location may be null.
5. severity must match the checklist item severity unless strong mitigating context applies.
"""

CAPABILITY_REVIEW_PROMPT_TEMPLATE = """{system_instruction}

{schema_description}

CAPABILITY TO EVALUATE: {capability}
SKILL VERSION: {version}

CHECKLIST ITEMS TO EVALUATE:
{checklist_formatted}

SUBMISSION CONTEXT ({submission_type}):
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
    return CAPABILITY_REVIEW_PROMPT_TEMPLATE.format(
        system_instruction=SYSTEM_INSTRUCTION,
        schema_description=JSON_SCHEMA_DESCRIPTION,
        capability=capability,
        version=version,
        checklist_formatted=checklist_str,
        submission_type=submission_type,
        submission_text=truncated_text,
    )


def build_retry_prompt(validation_error: str, raw_output: str) -> str:
    """Build retry prompt appending the exact schema validation failure."""
    return RETRY_PROMPT_TEMPLATE.format(
        validation_error=validation_error,
        schema_description=JSON_SCHEMA_DESCRIPTION,
        raw_output=raw_output[:2000],
    )
