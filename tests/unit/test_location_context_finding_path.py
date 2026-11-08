"""Unit tests verifying location context resolution for finding and unsupported paths (Bug B)."""

from __future__ import annotations

from pathlib import Path

from compliance_review.evidence.verifier import resolve_source_span


def test_location_context_finding_and_unsupported_paths() -> None:
    """Verify that both finding and unsupported paths resolve readable text without %PDF- bytes."""
    sample_pdf = Path("data/incoming/20261108T070346_Halo_Enhanced__1_.pdf")
    assert sample_pdf.exists(), f"Sample PDF must exist at {sample_pdf}"

    submission = {
        "submission_type": "prose",
        "source_path": str(sample_pdf),
    }

    # a) Finding with evidence_location="page:1"
    finding_loc = "page:1"
    finding_span = resolve_source_span(evidence_location=finding_loc, submission=submission)

    assert finding_span is not None and len(finding_span) > 0
    assert any(term in finding_span for term in ("HALO", "Hybrid"))
    assert "%PDF-" not in finding_span
    assert "obj" not in finding_span or "objective" in finding_span.lower()
    assert "stream\r" not in finding_span and "stream\n" not in finding_span
    assert "xref" not in finding_span

    # b) Unsupported verdict with evidence_location="page:1"
    unsupported_loc = "page:1"
    unsupported_span = resolve_source_span(
        evidence_location=unsupported_loc,
        submission=submission,
    )

    assert unsupported_span is not None and len(unsupported_span) > 0
    assert any(term in unsupported_span for term in ("HALO", "Hybrid"))
    assert "%PDF-" not in unsupported_span
    assert "obj" not in unsupported_span or "objective" in unsupported_span.lower()
    assert "stream\r" not in unsupported_span and "stream\n" not in unsupported_span
    assert "xref" not in unsupported_span


def test_location_context_invalid_location_handled_gracefully() -> None:
    """Verify that invalid locations return None or empty string gracefully without raising."""
    sample_pdf = Path("data/incoming/20261108T070346_Halo_Enhanced__1_.pdf")
    submission = {
        "submission_type": "prose",
        "source_path": str(sample_pdf),
    }

    # Invalid page number out of range
    res_page_oob = resolve_source_span(evidence_location="page:999", submission=submission)
    assert res_page_oob is None or res_page_oob == ""

    # Invalid location format
    res_invalid = resolve_source_span(evidence_location="invalid:foo", submission=submission)
    assert res_invalid is None or res_invalid == ""
