"""Deterministic report structure checks conforming to ARCHITECTURE.md §3."""

import re
from typing import Any

HEADING_PATTERNS = {
    "introduction": re.compile(r"(?m)^#+\s*introduction\b", re.IGNORECASE),
    "method": re.compile(r"(?m)^#+\s*(?:methods?|methodology)\b", re.IGNORECASE),
    "result": re.compile(r"(?m)^#+\s*results?\b", re.IGNORECASE),
    "discussion": re.compile(r"(?m)^#+\s*discussion\b", re.IGNORECASE),
}


def check_structure(prose_text: str, word_count: int) -> list[dict[str, Any]]:
    """Run deterministic structure checks."""
    verdicts: list[dict[str, Any]] = []

    present_headings: dict[str, int] = {}
    for sec, pat in HEADING_PATTERNS.items():
        m = pat.search(prose_text)
        if m:
            present_headings[sec] = m.start()

    required = ["introduction", "method", "result", "discussion"]
    missing = [sec for sec in required if sec not in present_headings]

    first_span = prose_text.splitlines()[0].strip() if prose_text else "Title"

    # 1. struct-required-sections
    if missing:
        verdicts.append(
            {
                "check_id": "struct-required-sections",
                "verdict": "flag",
                "severity": "high",
                "evidence_text": first_span,
                "evidence_location": "page:1",
                "confidence": 0.95,
            }
        )
    else:
        verdicts.append(
            {
                "check_id": "struct-required-sections",
                "verdict": "pass",
                "severity": "high",
                "evidence_text": "All required sections present",
                "evidence_location": "page:1",
                "confidence": 1.0,
            }
        )

    # 2. struct-heading-order
    pos = [present_headings[sec] for sec in required if sec in present_headings]
    if pos == sorted(pos):
        verdicts.append(
            {
                "check_id": "struct-heading-order",
                "verdict": "pass",
                "severity": "medium",
                "evidence_text": "Headings follow standard sequence",
                "evidence_location": "page:1",
                "confidence": 1.0,
            }
        )
    else:
        order_flag_span = ""
        for idx in range(len(pos) - 1):
            if pos[idx] > pos[idx + 1]:
                order_flag_span = prose_text[pos[idx] : pos[idx] + 80].strip()
                break
        if not order_flag_span:
            order_flag_span = first_span

        verdicts.append(
            {
                "check_id": "struct-heading-order",
                "verdict": "flag",
                "severity": "medium",
                "evidence_text": order_flag_span,
                "evidence_location": "page:1",
                "confidence": 0.90,
            }
        )

    # 3. struct-minimum-length
    if word_count < 500:
        verdicts.append(
            {
                "check_id": "struct-minimum-length",
                "verdict": "flag",
                "severity": "medium",
                "evidence_text": first_span,
                "evidence_location": "page:1",
                "confidence": 1.0,
            }
        )
    else:
        verdicts.append(
            {
                "check_id": "struct-minimum-length",
                "verdict": "pass",
                "severity": "medium",
                "evidence_text": f"Submission contains {word_count} words",
                "evidence_location": "page:1",
                "confidence": 1.0,
            }
        )

    return verdicts
