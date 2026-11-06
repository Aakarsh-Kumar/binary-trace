"""Deterministic Responsible-AI disclosure checks conforming to ARCHITECTURE.md §3."""

import re
from typing import Any

KNOWN_DISCLOSURE_HEADINGS = ["disclosure", "ai use", "responsible ai", "ai assistance"]
KNOWN_AI_TOOLS = ["chatgpt", "copilot", "claude", "gemini", "gpt-4", "qwen", "llama"]


def check_disclosure(prose_text: str, has_disclosure_file: bool = False) -> list[dict[str, Any]]:
    """Run deterministic RAI disclosure checks."""
    verdicts: list[dict[str, Any]] = []
    text_lower = prose_text.lower()

    # 1. rai-section-present
    has_section = has_disclosure_file or any(h in text_lower for h in KNOWN_DISCLOSURE_HEADINGS)
    if not has_section:
        verdicts.append(
            {
                "check_id": "rai-section-present",
                "verdict": "flag",
                "severity": "high",
                "evidence_text": "No AI disclosure section or DISCLOSURE.md located",
                "evidence_location": "section:disclosure",
                "confidence": 0.95,
            }
        )
        verdicts.append(
            {
                "check_id": "rai-tool-named",
                "verdict": "not_applicable",
                "severity": "medium",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 1.0,
            }
        )
        verdicts.append(
            {
                "check_id": "rai-task-named",
                "verdict": "not_applicable",
                "severity": "medium",
                "evidence_text": None,
                "evidence_location": None,
                "confidence": 1.0,
            }
        )
        return verdicts

    verdicts.append(
        {
            "check_id": "rai-section-present",
            "verdict": "pass",
            "severity": "high",
            "evidence_text": "AI disclosure section present",
            "evidence_location": "section:disclosure",
            "confidence": 1.0,
        }
    )

    # Extract verbatim disclosure sample for evidence grounding
    disc_sample = ""
    for h in KNOWN_DISCLOSURE_HEADINGS:
        pos = text_lower.find(h)
        if pos != -1:
            disc_sample = prose_text[pos : pos + 120].strip()
            break
    if not disc_sample:
        disc_sample = prose_text[:100].strip()

    is_negative_disclosure = bool(
        re.search(r"\bno\s+(?:generative\s+)?ai\b", text_lower)
        or "did not use" in text_lower
        or "no ai" in text_lower
        or "not used" in text_lower
        or "without generative ai" in text_lower
    )

    # 2. rai-tool-named
    tools_found = [t for t in KNOWN_AI_TOOLS if t in text_lower]
    if tools_found:
        verdicts.append(
            {
                "check_id": "rai-tool-named",
                "verdict": "pass",
                "severity": "medium",
                "evidence_text": f"Disclosed AI tools: {', '.join(tools_found)}",
                "evidence_location": "section:disclosure",
                "confidence": 1.0,
            }
        )
    else:
        # Check if negative disclosure
        if is_negative_disclosure:
            verdicts.append(
                {
                    "check_id": "rai-tool-named",
                    "verdict": "pass",
                    "severity": "medium",
                    "evidence_text": "Negative disclosure stating no AI tools utilized",
                    "evidence_location": "section:disclosure",
                    "confidence": 1.0,
                }
            )
        else:
            verdicts.append(
                {
                    "check_id": "rai-tool-named",
                    "verdict": "flag",
                    "severity": "medium",
                    "evidence_text": disc_sample,
                    "evidence_location": "section:disclosure",
                    "confidence": 0.90,
                }
            )

    # 3. rai-task-named
    task_keywords = ["debugging", "writing", "drafting", "translating", "brainstorming", "editing"]
    tasks_found = [k for k in task_keywords if k in text_lower]
    if tasks_found or is_negative_disclosure:
        tasks_desc = ", ".join(tasks_found) if tasks_found else "None"
        verdicts.append(
            {
                "check_id": "rai-task-named",
                "verdict": "pass",
                "severity": "medium",
                "evidence_text": f"Tasks specified: {tasks_desc}",
                "evidence_location": "section:disclosure",
                "confidence": 1.0,
            }
        )
    else:
        verdicts.append(
            {
                "check_id": "rai-task-named",
                "verdict": "flag",
                "severity": "medium",
                "evidence_text": disc_sample,
                "evidence_location": "section:disclosure",
                "confidence": 0.85,
            }
        )

    return verdicts
