"""Ingestion subsystem for prose, code, and mixed student submissions."""

from compliance_review.ingestion.docx import ingest_docx
from compliance_review.ingestion.markdown import ingest_markdown, normalize_text
from compliance_review.ingestion.orchestrator import ingest_source, parse_submission_content
from compliance_review.ingestion.pdf import ingest_pdf
from compliance_review.ingestion.repo import ingest_repo

__all__ = [
    "ingest_markdown",
    "ingest_pdf",
    "ingest_docx",
    "ingest_repo",
    "ingest_source",
    "parse_submission_content",
    "normalize_text",
]
