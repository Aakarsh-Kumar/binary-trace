"""Deterministic capability gate conforming to ARCHITECTURE.md §6.2 and US-13.

FROZEN INVARIANT:
This module MUST NOT import any model module, sentence_transformers, torch, or faiss.
Capability set is determined entirely from deterministic signals.
"""

from typing import Any


def determine_capability_set(
    submission_type: str,
    extracted_data: dict[str, Any],
) -> tuple[dict[str, bool], dict[str, str]]:
    """Determine enabled capabilities and gate reasons based strictly on deterministic signals.

    Returns:
        capability_set: dict mapping capability name to bool
        gate_reasons: dict mapping capability name to explanation reason
    """
    capabilities: dict[str, bool] = {
        "citation-integrity": False,
        "report-structure": False,
        "code-quality": False,
        "rai-disclosure": False,
    }
    reasons: dict[str, str] = {}

    if submission_type == "prose":
        capabilities["citation-integrity"] = True
        reasons["citation-integrity"] = "prose submission requires citation integrity check"

        capabilities["report-structure"] = True
        reasons["report-structure"] = "prose submission requires structural compliance check"

        capabilities["rai-disclosure"] = True
        reasons["rai-disclosure"] = "prose submission requires AI disclosure check"

        capabilities["code-quality"] = False
        reasons["code-quality"] = "code-quality disabled for pure prose submissions"

    elif submission_type == "code":
        capabilities["code-quality"] = True
        reasons["code-quality"] = "code submission requires Python code quality static check"

        capabilities["citation-integrity"] = False
        reasons["citation-integrity"] = "citation-integrity disabled for code submissions per US-13"

        capabilities["report-structure"] = False
        reasons["report-structure"] = "report-structure disabled for code submissions"

        capabilities["rai-disclosure"] = False
        reasons["rai-disclosure"] = "rai-disclosure disabled for code submissions per US-13"

    elif submission_type == "mixed":
        # All four are candidates, subject to §6.2 preconditions within mixed
        capabilities["code-quality"] = True
        reasons["code-quality"] = "code present in mixed submission"

        prose_text = extracted_data.get("text", "")
        text_lower = prose_text.lower()
        word_count = extracted_data.get("word_count", 0)

        # citation-integrity requires bibliography detected
        has_bib = (
            "references" in text_lower
            or "bibliography" in text_lower
            or ".bib" in text_lower
            or ".ris" in text_lower
        )
        if has_bib:
            capabilities["citation-integrity"] = True
            reasons["citation-integrity"] = "bibliography detected in mixed submission"
        else:
            capabilities["citation-integrity"] = False
            reasons["citation-integrity"] = "no bibliography or references detected"

        # report-structure requires prose length >= 500 words
        if word_count >= 500:
            capabilities["report-structure"] = True
            reasons["report-structure"] = f"prose length {word_count} >= 500 words"
        else:
            capabilities["report-structure"] = False
            reasons["report-structure"] = f"prose length {word_count} < 500 words"

        # rai-disclosure requires disclosure heading or DISCLOSURE.md
        has_disclosure = (
            extracted_data.get("has_disclosure_file", False)
            or "disclosure" in text_lower
            or "ai use" in text_lower
            or "responsible ai" in text_lower
        )
        if has_disclosure:
            capabilities["rai-disclosure"] = True
            reasons["rai-disclosure"] = "AI disclosure section or DISCLOSURE.md detected"
        else:
            capabilities["rai-disclosure"] = False
            reasons["rai-disclosure"] = "no disclosure section or DISCLOSURE.md present"

    else:
        raise ValueError(f"Unknown submission type: {submission_type}")

    return capabilities, reasons
