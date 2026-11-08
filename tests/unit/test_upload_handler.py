"""Unit tests for dashboard upload handler conforming to US-39."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from compliance_review.dashboard.upload_handler import handle_upload
from compliance_review.errors import DuplicateSubmissionError, ModelError


def test_upload_valid() -> None:
    """Verify valid upload writes incoming file and triggers ingest & review."""
    mock_ingest = MagicMock(return_value=42)
    mock_review = MagicMock(return_value=None)
    created_file: Path | None = None

    try:
        ok, ext_id, err = handle_upload(
            file_bytes=b"%PDF-1.4 fake content",
            filename="test_doc.pdf",
            submission_type="prose",
            ingest_fn=mock_ingest,
            review_fn=mock_review,
        )

        assert ok is True
        assert ext_id is not None
        assert ext_id.startswith("upload-")
        assert "test_doc" in ext_id
        assert err is None

        mock_ingest.assert_called_once()
        call_kwargs = mock_ingest.call_args.kwargs
        created_file = call_kwargs["source"]
        assert isinstance(created_file, Path)
        assert created_file.exists()
        assert created_file.read_bytes() == b"%PDF-1.4 fake content"

        mock_review.assert_called_once_with(submission_id=42, skill_status="evaluating")
    finally:
        if created_file and created_file.exists():
            created_file.unlink()


def test_upload_oversized() -> None:
    """Verify oversized payload (>50MB) is rejected without invoking ingest."""
    mock_ingest = MagicMock(return_value=42)
    mock_review = MagicMock(return_value=None)

    oversized_bytes = b"0" * (51 * 1024 * 1024)

    ok, ext_id, err = handle_upload(
        file_bytes=oversized_bytes,
        filename="oversized.pdf",
        submission_type="prose",
        ingest_fn=mock_ingest,
        review_fn=mock_review,
    )

    assert ok is False
    assert ext_id is None
    assert err is not None
    assert "50 MB" in err
    mock_ingest.assert_not_called()
    mock_review.assert_not_called()


def test_upload_duplicate() -> None:
    """Verify duplicate submission error is captured cleanly without invoking review."""
    mock_ingest = MagicMock(side_effect=DuplicateSubmissionError("Submission exists"))
    mock_review = MagicMock(return_value=None)
    created_file: Path | None = None

    try:
        ok, ext_id, err = handle_upload(
            file_bytes=b"sample duplicate data",
            filename="duplicate.md",
            submission_type="prose",
            ingest_fn=mock_ingest,
            review_fn=mock_review,
        )

        assert ok is False
        assert ext_id is None
        assert err is not None
        assert "already exists" in err

        mock_ingest.assert_called_once()
        created_file = mock_ingest.call_args.kwargs["source"]
        mock_review.assert_not_called()
    finally:
        if created_file and created_file.exists():
            created_file.unlink()


def test_upload_model_error() -> None:
    """Verify model error returns mapped error mentioning model stage."""
    mock_ingest = MagicMock(return_value=42)
    mock_review = MagicMock(side_effect=ModelError("Ollama inference timeout"))
    created_file: Path | None = None

    try:
        ok, ext_id, err = handle_upload(
            file_bytes=b"sample model error data",
            filename="broken_model.md",
            submission_type="prose",
            ingest_fn=mock_ingest,
            review_fn=mock_review,
        )

        assert ok is False
        assert ext_id is None
        assert err is not None
        assert "model stage" in err

        mock_ingest.assert_called_once()
        created_file = mock_ingest.call_args.kwargs["source"]
        mock_review.assert_called_once()
    finally:
        if created_file and created_file.exists():
            created_file.unlink()

