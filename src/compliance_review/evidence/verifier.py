"""Evidence verifier conforming to ARCHITECTURE.md §7.1.

FROZEN INVARIANT (INSTRUCTIONS.md §8.1):
Thresholds and normalization are frozen and MUST NOT be modified:
  - prefix_len = 40
  - fuzzy_threshold = 0.92
  - normalization = NFKC + whitespace collapse + casefold
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from pathlib import Path
from typing import Any, NamedTuple

PREFIX_LEN: int = 40
FUZZY_THRESHOLD: float = 0.92


class EvidenceResult(NamedTuple):
    """Result of evidence verification."""

    verified: bool
    method: str
    located_at: str | None = None
    failure_reason: str | None = None


# Grammar regexes per ARCHITECTURE.md §5.3
GRAMMAR_REGEXES = {
    "page": re.compile(r"^page:(\d+)$"),
    "file": re.compile(r"^file:([^:]+):(\d+)$"),
    "section": re.compile(r"^section:([a-zA-Z0-9_\-]+)$"),
    "table": re.compile(r"^table:([a-zA-Z0-9_\-]+)$"),
    "bbox": re.compile(r"^bbox:(\d+),(\d+),(\d+),(\d+)$"),
}


def normalize_span(text: str) -> str:
    """Normalize text span using NFKC + whitespace collapse + casefold."""
    nfkc = unicodedata.normalize("NFKC", text)
    collapsed = " ".join(nfkc.split())
    return collapsed.casefold()


def parse_location_grammar(location: str) -> tuple[str, Any] | None:
    """Validate and parse location string according to §5.3 grammar."""
    for kind, pattern in GRAMMAR_REGEXES.items():
        match = pattern.match(location)
        if match:
            return kind, match.groups()
    return None


def resolve_source_span(
    location: str | None = None,
    submission: Any = None,
    submission_data: dict[str, Any] | None = None,
    *,
    evidence_location: str | None = None,
    kind: str | None = None,
    groups: Any = None,
) -> str:
    """Resolve the source text span corresponding to the location."""
    data: dict[str, Any] | None = submission_data

    # Handle legacy 3-positional-arg call: resolve_source_span(kind, groups, submission_data)
    if kind is None and groups is None:
        if (
            location is not None
            and submission is not None
            and isinstance(submission, tuple | list)
        ):
            kind = str(location)
            groups = submission
            data = submission_data or {}
        else:
            loc = evidence_location or location
            if not loc:
                return ""
            parsed = parse_location_grammar(loc)
            if not parsed:
                return ""
            kind, groups = parsed
            if data is None:
                if isinstance(submission, dict) and (
                    "pages" in submission or "files" in submission or "text" in submission
                ):
                    data = submission
                elif submission is not None:
                    source_path = (
                        submission.get("source_path")
                        if isinstance(submission, dict)
                        else getattr(submission, "source_path", None)
                    )
                    sub_type = (
                        submission.get("submission_type", "prose")
                        if isinstance(submission, dict)
                        else getattr(submission, "submission_type", "prose")
                    )
                    if source_path:
                        from compliance_review.ingestion.orchestrator import (
                            parse_submission_content,
                        )

                        _, data = parse_submission_content(Path(source_path), sub_type)

    if not data or not kind or not groups:
        return ""

    if kind == "page":
        page_num = int(groups[0])
        pages = data.get("pages", {})
        return str(pages.get(page_num, data.get("text", "")))

    elif kind == "file":
        rel_path, line_no_str = groups[0], groups[1]
        line_no = int(line_no_str)
        files = data.get("files", {})
        content = files.get(rel_path, "")
        lines = content.splitlines()
        if 1 <= line_no <= len(lines):
            return str(lines[line_no - 1])
        return str(content)

    elif kind == "section":
        slug = groups[0].lower()
        full_text = str(data.get("text", ""))
        idx = full_text.lower().find(slug)
        if idx != -1:
            return full_text[idx : idx + 1000]
        return full_text

    elif kind in ("table", "bbox"):
        return str(data.get("text", ""))

    return ""


def verify_evidence(
    evidence_text: str | None,
    evidence_location: str | None,
    submission_data: dict[str, Any],
) -> EvidenceResult:
    """Verify evidence text against submission source per §7.1.

    Public signature is frozen.
    """
    if not evidence_text or not evidence_location:
        return EvidenceResult(verified=False, method="none", failure_reason="missing_evidence")

    # 1. Parse location grammar
    parsed = parse_location_grammar(evidence_location)
    if not parsed:
        return EvidenceResult(
            verified=False, method="none", failure_reason="location_grammar_invalid"
        )

    kind, groups = parsed

    # 2. Resolve source span
    source_span = resolve_source_span(kind, groups, submission_data)
    if not source_span:
        return EvidenceResult(verified=False, method="none", failure_reason="not_located")

    # 3. Normalize
    norm_source = normalize_span(source_span)
    norm_evidence = normalize_span(evidence_text)

    if not norm_evidence or not norm_source:
        return EvidenceResult(verified=False, method="none", failure_reason="not_located")

    # 4. Exact substring match
    if norm_evidence in norm_source:
        return EvidenceResult(verified=True, method="substring", located_at=evidence_location)

    # 5. First 40 normalized characters prefix match
    prefix = norm_evidence[:PREFIX_LEN]
    if len(prefix) >= 20 and prefix in norm_source:
        return EvidenceResult(verified=True, method="normalized", located_at=evidence_location)

    # 6. Fuzzy SequenceMatcher ratio >= 0.92
    ratio = difflib.SequenceMatcher(None, norm_evidence, norm_source).ratio()
    if ratio >= FUZZY_THRESHOLD:
        return EvidenceResult(verified=True, method="fuzzy", located_at=evidence_location)

    # 7. Fallback failure
    return EvidenceResult(verified=False, method="none", failure_reason="not_located")
