"""Ingestion orchestrator managing ingestion and persistence per US-01..US-05."""

from pathlib import Path
from typing import Any

from compliance_review.db.repository import create_submission, get_submission_by_external_id
from compliance_review.errors import DuplicateSubmissionError, IngestError
from compliance_review.ingestion.docx import ingest_docx
from compliance_review.ingestion.markdown import ingest_markdown
from compliance_review.ingestion.pdf import ingest_pdf
from compliance_review.ingestion.repo import ingest_repo


def parse_submission_content(source: Path, sub_type: str) -> tuple[str, dict[str, Any]]:
    """Parse submission file or directory according to type."""
    extracted_data: dict[str, Any] = {"submission_type": sub_type}

    if sub_type == "prose":
        suffix = source.suffix.lower()
        if suffix in [".md", ".txt"]:
            text, sha256, wc = ingest_markdown(source)
            extracted_data.update({"text": text, "word_count": wc})
            return sha256, extracted_data
        elif suffix == ".pdf":
            text, sha256, pages = ingest_pdf(source)
            extracted_data.update({"text": text, "pages": pages, "word_count": len(text.split())})
            return sha256, extracted_data
        elif suffix == ".docx":
            text, sha256, wc = ingest_docx(source)
            extracted_data.update({"text": text, "word_count": wc})
            return sha256, extracted_data
        else:
            raise IngestError(f"Unsupported prose format: {suffix}")

    elif sub_type == "code":
        files, sha256, loc = ingest_repo(source)
        extracted_data.update({"files": files, "loc": loc})
        return sha256, extracted_data

    elif sub_type == "mixed":
        if not source.is_dir():
            raise IngestError(
                f"Mixed submission must be a directory containing prose and code: {source}"
            )

        # Look for prose
        prose_files = (
            list(source.glob("*.pdf")) + list(source.glob("*.md")) + list(source.glob("*.docx"))
        )
        prose_text = ""
        if prose_files:
            p_file = prose_files[0]
            if p_file.suffix == ".pdf":
                p_text, _, pages = ingest_pdf(p_file)
                extracted_data["pages"] = pages
            elif p_file.suffix == ".docx":
                p_text, _, _ = ingest_docx(p_file)
            else:
                p_text, _, _ = ingest_markdown(p_file)
            prose_text = p_text

        extracted_data["text"] = prose_text
        extracted_data["word_count"] = len(prose_text.split())

        # Look for code
        try:
            files, code_sha, loc = ingest_repo(source)
            extracted_data["files"] = files
            extracted_data["loc"] = loc
        except IngestError:
            extracted_data["files"] = {}
            extracted_data["loc"] = 0

        # Check for disclosure file
        if (source / "DISCLOSURE.md").exists():
            extracted_data["has_disclosure_file"] = True

        combined_hash_input = prose_text + str(extracted_data.get("files", {}))
        import hashlib

        sha256 = hashlib.sha256(combined_hash_input.encode("utf-8")).hexdigest()
        return sha256, extracted_data

    else:
        raise IngestError(f"Invalid submission type: {sub_type}. Expected prose, code, or mixed.")


def ingest_source(
    source_path: Path | str, sub_type: str, external_id: str | None = None
) -> tuple[int, str]:
    """Ingest a submission source, check duplicates, and record to database."""
    source = Path(source_path)
    if not source.exists():
        raise IngestError(f"Source path not found: {source}")

    ext_id = external_id or source.stem

    # US-04: reject duplicate external_id
    existing = get_submission_by_external_id(ext_id)
    if existing is not None:
        raise DuplicateSubmissionError(
            f"Submission with external_id '{ext_id}' already exists (id={existing['id']})"
        )

    sha256, _ = parse_submission_content(source, sub_type)

    # Persist to database
    sub_id = create_submission(
        external_id=ext_id,
        submission_type=sub_type,
        source_path=str(source.resolve()),
        content_sha256=sha256,
    )

    return sub_id, sha256
