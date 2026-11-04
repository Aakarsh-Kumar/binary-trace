"""Deterministic report structure checks conforming to ARCHITECTURE.md §3."""

from typing import Any


def check_structure(prose_text: str, word_count: int) -> list[dict[str, Any]]:
    """Run deterministic structure checks."""
    verdicts: list[dict[str, Any]] = []

    text_lower = prose_text.lower()
    required = ["introduction", "method", "result", "discussion"]
    missing = [sec for sec in required if sec not in text_lower]

    # 1. struct-required-sections
    if missing:
        verdicts.append(
            {
                "check_id": "struct-required-sections",
                "verdict": "flag",
                "severity": "high",
                "evidence_text": f"Missing sections: {', '.join(missing)}",
                "evidence_location": "section:headings",
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
                "evidence_location": "section:headings",
                "confidence": 1.0,
            }
        )

    # 2. struct-heading-order
    pos = [text_lower.find(sec) for sec in required if sec in text_lower]
    if pos == sorted(pos):
        verdicts.append(
            {
                "check_id": "struct-heading-order",
                "verdict": "pass",
                "severity": "medium",
                "evidence_text": "Headings follow standard sequence",
                "evidence_location": "section:headings",
                "confidence": 1.0,
            }
        )
    else:
        verdicts.append(
            {
                "check_id": "struct-heading-order",
                "verdict": "flag",
                "severity": "medium",
                "evidence_text": "Headings appear out of standard sequence",
                "evidence_location": "section:headings",
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
                "evidence_text": f"Submission length {word_count} words is below 500 words minimum",
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
