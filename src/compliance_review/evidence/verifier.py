"""Evidence verifier conforming to ARCHITECTURE.md §7.1.

FROZEN INVARIANT (INSTRUCTIONS.md §8.1):
Thresholds and normalization are frozen and MUST NOT be modified:
  - prefix_len = 40
  - fuzzy_threshold = 0.92
  - normalization = NFKC + whitespace collapse + casefold
"""

import difflib
import re
import unicodedata
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


def resolve_source_span(kind: str, groups: Any, submission_data: dict[str, Any]) -> str:
    """Resolve the source text span corresponding to the location."""
    if kind == "page":
        page_num = int(groups[0])
        pages = submission_data.get("pages", {})
        return str(pages.get(page_num, submission_data.get("text", "")))

    elif kind == "file":
        rel_path, line_no_str = groups[0], groups[1]
        line_no = int(line_no_str)
        files = submission_data.get("files", {})
        content = files.get(rel_path, "")
        lines = content.splitlines()
        if 1 <= line_no <= len(lines):
            return str(lines[line_no - 1])
        return str(content)

    elif kind == "section":
        slug = groups[0].lower()
        full_text = str(submission_data.get("text", ""))
        idx = full_text.lower().find(slug)
        if idx != -1:
            return full_text[idx : idx + 1000]
        return full_text

    elif kind == "table":
        return str(submission_data.get("text", ""))

    elif kind == "bbox":
        return str(submission_data.get("text", ""))

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
