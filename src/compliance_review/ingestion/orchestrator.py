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
        elif suffix == ".pdf":
            text, sha256, pages = ingest_pdf(source)
            extracted_data.update({"text": text, "pages": pages, "word_count": len(text.split())})
        elif suffix == ".docx":
            text, sha256, wc = ingest_docx(source)
            extracted_data.update({"text": text, "word_count": wc})
        else:
            raise IngestError(f"Unsupported prose format: {suffix}")

        t_lower = text.lower()
        extracted_data["references_present"] = (
            "references" in t_lower
            or "bibliography" in t_lower
            or ".bib" in t_lower
            or ".ris" in t_lower
        )
        return sha256, extracted_data

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
        all_prose_texts: list[str] = []
        if prose_files:
            # Prefer non-DISCLOSURE files (e.g. paper.md) as primary prose
            primary_files = [f for f in prose_files if f.name.upper() != "DISCLOSURE.MD"]
            p_file = primary_files[0] if primary_files else prose_files[0]
            if p_file.suffix == ".pdf":
                p_text, _, pages = ingest_pdf(p_file)
                extracted_data["pages"] = pages
            elif p_file.suffix == ".docx":
                p_text, _, _ = ingest_docx(p_file)
            else:
                p_text, _, _ = ingest_markdown(p_file)
            prose_text = p_text

            for pf in prose_files:
                if pf.suffix in [".md", ".txt"]:
                    t, _, _ = ingest_markdown(pf)
                    all_prose_texts.append(t)
                elif pf.suffix == ".docx":
                    t, _, _ = ingest_docx(pf)
                    all_prose_texts.append(t)
                elif pf.suffix == ".pdf":
                    t, _, _ = ingest_pdf(pf)
                    all_prose_texts.append(t)

        extracted_data["text"] = prose_text
        extracted_data["word_count"] = len(prose_text.split())

        # Check for bibliography or references in directory or in all prose texts
        bib_files = list(source.glob("*.bib")) + list(source.glob("*.ris"))
        combined_prose = "\n".join(all_prose_texts).lower()
        has_bib = (
            len(bib_files) > 0
            or "references" in combined_prose
            or "bibliography" in combined_prose
            or ".bib" in combined_prose
            or ".ris" in combined_prose
        )
        extracted_data["references_present"] = has_bib

        # Look for code
        try:
            files, code_sha, loc = ingest_repo(source)
            extracted_data["files"] = files
            extracted_data["loc"] = loc
        except IngestError:
            extracted_data["files"] = {}
            extracted_data["loc"] = 0

        # Check for disclosure file or disclosure heading across prose files
        has_disc_file = (source / "DISCLOSURE.md").exists() or (source / "disclosure.md").exists()
        if has_disc_file:
            extracted_data["has_disclosure_file"] = True
        if (
            has_disc_file
            or "disclosure" in combined_prose
            or "ai use" in combined_prose
            or "responsible ai" in combined_prose
        ):
            extracted_data["disclosure_present"] = True

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
