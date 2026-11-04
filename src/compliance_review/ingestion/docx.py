"""DOCX ingestion using python-docx conforming to ARCHITECTURE.md §2.5 and US-01."""

import hashlib
from pathlib import Path

import docx

from compliance_review.errors import IngestError
from compliance_review.ingestion.markdown import normalize_text


def ingest_docx(file_path: Path | str) -> tuple[str, str, int]:
    """Ingest DOCX, returning (normalized_text, sha256_hash, word_count)."""
    path = Path(file_path)
    if not path.is_file():
        raise IngestError(f"DOCX file not found: {path}")

    try:
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        raw_text = "\n\n".join(paragraphs)
    except Exception as exc:
        raise IngestError(f"Failed to read DOCX {path}: {exc}") from exc

    norm_text = normalize_text(raw_text)
    sha256 = hashlib.sha256(norm_text.encode("utf-8")).hexdigest()
    word_count = len(norm_text.split())

    return norm_text, sha256, word_count
