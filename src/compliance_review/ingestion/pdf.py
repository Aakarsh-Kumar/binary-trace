"""PDF ingestion using PyMuPDF conforming to ARCHITECTURE.md §2.5 and US-01."""

import hashlib
from pathlib import Path

import pymupdf  # type: ignore[import-untyped]  # reason: pymupdf ships without bundled typed marker

from compliance_review.errors import IngestError
from compliance_review.ingestion.markdown import normalize_text


def ingest_pdf(file_path: Path | str) -> tuple[str, str, dict[int, str]]:
    """Ingest PDF, returning (normalized_text, sha256_hash, pages_dict).

    pages_dict is 1-indexed to match location grammar page:N.
    """
    path = Path(file_path)
    if not path.is_file():
        raise IngestError(f"PDF file not found: {path}")

    try:
        doc = pymupdf.open(str(path))
    except Exception as exc:
        raise IngestError(f"Failed to open PDF {path}: {exc}") from exc

    full_text_parts: list[str] = []
    pages: dict[int, str] = {}

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_text = normalize_text(page.get_text())
        pages[page_idx + 1] = page_text
        full_text_parts.append(page_text)

    full_normalized = "\n\n".join(full_text_parts)
    sha256 = hashlib.sha256(full_normalized.encode("utf-8")).hexdigest()

    return full_normalized, sha256, pages
