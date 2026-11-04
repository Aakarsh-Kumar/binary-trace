"""Markdown and plain text ingestion conforming to ARCHITECTURE.md §2.5 and US-01."""

import hashlib
import unicodedata
from pathlib import Path

from compliance_review.errors import IngestError


def normalize_text(text_content: str) -> str:
    """Normalize text using Unicode NFKC and whitespace normalization."""
    normalized = unicodedata.normalize("NFKC", text_content)
    # Collapse multiple whitespace to single space, strip lines
    lines = [line.strip() for line in normalized.splitlines()]
    return "\n".join(lines)


def ingest_markdown(file_path: Path | str) -> tuple[str, str, int]:
    """Ingest markdown/text file, returning (normalized_text, sha256_hash, word_count)."""
    path = Path(file_path)
    if not path.is_file():
        raise IngestError(f"Prose file not found: {path}")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except Exception as exc:
        raise IngestError(f"Failed to read file {path}: {exc}") from exc

    norm_text = normalize_text(raw_text)
    sha256 = hashlib.sha256(norm_text.encode("utf-8")).hexdigest()
    word_count = len(norm_text.split())

    return norm_text, sha256, word_count
