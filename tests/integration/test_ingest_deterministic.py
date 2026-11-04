"""Integration tests for ingestion, duplicate detection, and deterministic review trace."""

import uuid
from pathlib import Path

import pytest

from compliance_review.db.repository import get_submission_by_id
from compliance_review.errors import DuplicateSubmissionError
from compliance_review.harness.orchestrator import run_deterministic_review
from compliance_review.ingestion.orchestrator import ingest_source


def test_ingest_prose_and_duplicate_rejection(tmp_path: Path) -> None:
    """Verify prose ingestion, SHA256 storage, and duplicate rejection (US-01, US-04)."""
    prose_file = tmp_path / "paper.md"
    prose_file.write_text(
        "# Title\n\nIntroduction\n\nThis is a research report.\n\nReferences\n10.1234/test.5678",
        encoding="utf-8",
    )

    ext_id = f"test-prose-{uuid.uuid4().hex[:8]}"
    sub_id, sha256 = ingest_source(prose_file, "prose", external_id=ext_id)
    assert sub_id > 0
    assert len(sha256) == 64

    sub = get_submission_by_id(sub_id)
    assert sub is not None
    assert sub["content_sha256"] == sha256
    assert sub["submission_type"] == "prose"

    # US-04: DuplicateSubmissionError on repeated external_id
    with pytest.raises(DuplicateSubmissionError):
        ingest_source(prose_file, "prose", external_id=ext_id)


def test_ingest_code_submission(tmp_path: Path) -> None:
    """Verify python code repo ingestion and hashing (US-02)."""
    repo_dir = tmp_path / "student_repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("def run():\n    print('hello')\n", encoding="utf-8")
    (repo_dir / "utils.py").write_text("x = 42\n", encoding="utf-8")

    ext_id = f"test-code-{uuid.uuid4().hex[:8]}"
    sub_id, sha256 = ingest_source(repo_dir, "code", external_id=ext_id)
    assert sub_id > 0
    assert len(sha256) == 64

    sub = get_submission_by_id(sub_id)
    assert sub is not None
    assert sub["submission_type"] == "code"


def test_ingest_mixed_and_deterministic_review(tmp_path: Path) -> None:
    """Verify mixed submission ingestion and deterministic review trace output (US-03, D-009)."""
    mixed_dir = tmp_path / "mixed_project"
    mixed_dir.mkdir()
    mixed_text = (
        "Introduction\n\nMethod\n\nResult\n\nDiscussion\n\n"
        "References\n10.1234/mixed.1\n\n"
        "Disclosure: used copilot for debugging\n" + "content " * 520
    )
    (mixed_dir / "report.md").write_text(mixed_text, encoding="utf-8")
    (mixed_dir / "model.py").write_text("import os\n", encoding="utf-8")

    ext_id = f"test-mixed-{uuid.uuid4().hex[:8]}"
    sub_id, sha256 = ingest_source(mixed_dir, "mixed", external_id=ext_id)
    assert sub_id > 0

    trace = run_deterministic_review(sub_id)
    assert "Deterministic Review Trace for Submission" in trace
    assert "Capabilities Gated:" in trace
    assert "Deterministic Verdicts:" in trace
    assert "code-quality" in trace
    assert "citation-integrity" in trace
