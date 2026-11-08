"""Unit tests for location context viewer and shared source resolver (D-043)."""

from __future__ import annotations

import importlib
import tempfile
from pathlib import Path

import pymupdf  # type: ignore[import-untyped]

from compliance_review.evidence.verifier import resolve_source_span, verify_evidence
from compliance_review.ingestion.orchestrator import parse_submission_content

_sub_mod = importlib.import_module("compliance_review.dashboard.pages.01_submission")
extract_context_lines = _sub_mod.extract_context_lines


class DummySubmission:
    """Mock submission object with source_path attribute."""

    def __init__(self, source_path: str, submission_type: str = "prose") -> None:
        self.source_path = source_path
        self.submission_type = submission_type


def _create_sample_pdf(tmp_dir: Path) -> Path:
    """Helper to create a single-page PDF with readable text."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "HALO: A Hybrid Deep Reinforcement Learning Framework\n"
        "Abstract\n"
        "This paper introduces an energy-aware load balancing system.",
        fontsize=11,
    )
    pdf_path = tmp_dir / "sample_paper.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_location_context_shows_extracted_text() -> None:
    """Verify location context renders extracted readable text, not raw %PDF- bytes."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = _create_sample_pdf(Path(tmp_dir))
        sub = DummySubmission(source_path=str(pdf_path), submission_type="prose")

        # Test both direct resolver and dashboard context extractor
        resolved_span = resolve_source_span(evidence_location="page:1", submission=sub)
        assert "%PDF-" not in resolved_span
        assert "HALO" in resolved_span
        assert "Abstract" in resolved_span

        context_output = extract_context_lines(
            source_path_str=str(pdf_path),
            location="page:1",
            submission=sub,
            evidence_text="HALO",
        )
        assert "%PDF-" not in context_output
        assert "HALO" in context_output
        assert "->" in context_output


def test_location_context_matches_verifier_resolution() -> None:
    """Verify that dashboard resolver matches what verify_evidence resolves."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = _create_sample_pdf(Path(tmp_dir))
        sub = {"source_path": str(pdf_path), "submission_type": "prose"}

        # 1. Parse via standard ingestion orchestrator
        _, sub_data = parse_submission_content(pdf_path, "prose")

        # 2. Call verify_evidence with a string on page 1
        target_quote = "HALO: A Hybrid Deep Reinforcement Learning"
        res = verify_evidence(
            evidence_text=target_quote,
            evidence_location="page:1",
            submission_data=sub_data,
        )
        assert res.verified is True

        # 3. Call resolve_source_span with the same location
        span = resolve_source_span(evidence_location="page:1", submission=sub)

        # 4. Assert string found by verifier is in the resolved span
        assert target_quote in span
