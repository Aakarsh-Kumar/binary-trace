"""Unit tests for location context resolution in finding and unsupported paths (P4.7-fix-2)."""

from __future__ import annotations

import inspect
import re
from pathlib import Path
from unittest.mock import patch

from compliance_review.evidence.verifier import resolve_source_span


def test_finding_and_unsupported_use_same_resolver_signature() -> None:
    """Verify finding and unsupported paths use identical positional resolver signatures."""
    sig = inspect.signature(resolve_source_span)
    param_names = list(sig.parameters.keys())
    assert param_names[0] == "location"
    assert param_names[1] == "submission"

    # Inspect call sites in 01_submission.py source
    src_file = Path("src/compliance_review/dashboard/pages/01_submission.py")
    assert src_file.exists()
    content = src_file.read_text(encoding="utf-8")

    # Both call sites in render_findings and render_unsupported must be positional:
    # span = resolve_source_span(..., submission)
    finding_calls = re.findall(r"span = resolve_source_span\(([^,\)]+),\s*submission\)", content)
    assert len(finding_calls) >= 2, (
        f"Expected >= 2 uniform positional call sites in 01_submission.py, "
        f"found {len(finding_calls)}: {finding_calls}"
    )
    # Ensure no calls pass unexpected keyword argument evidence_location=
    kw_calls = re.findall(r"resolve_source_span\([^)]*evidence_location\s*=", content)
    assert len(kw_calls) == 0, f"Found call with evidence_location= keyword argument: {kw_calls}"


def test_finding_location_context_renders_text() -> None:
    """Verify that finding location context resolves readable text without %PDF- bytes."""
    sample_pdf = Path("data/incoming/20261108T070346_Halo_Enhanced__1_.pdf")
    assert sample_pdf.exists(), f"Sample PDF must exist at {sample_pdf}"

    submission = {
        "id": 252,
        "submission_type": "prose",
        "source_path": str(sample_pdf),
    }
    verdict = {
        "id": 100,
        "check_id": "struct-required-sections",
        "skill_capability": "report-structure",
        "verdict": "flag",
        "severity": "high",
        "confidence": 0.95,
        "evidence_location": "page:1",
        "evidence_text": "HALO: A Hybrid Deep Reinforcement Learning",
    }

    # Verify direct resolver output
    span = resolve_source_span(verdict["evidence_location"], submission)
    assert span is not None and len(span) > 0
    assert any(term in span for term in ("HALO", "Hybrid"))
    assert "%PDF-" not in span
    assert "stream\r" not in span and "stream\n" not in span
    assert "xref" not in span

    # Verify that invoking render_findings does not raise TypeError
    import importlib

    sub_page = importlib.import_module("compliance_review.dashboard.pages.01_submission")

    with patch("streamlit.code") as mock_code:
        sub_page.render_findings([verdict], submission=submission)
        # Verify st.code was called with the resolved span
        mock_code.assert_called()
        rendered_code = mock_code.call_args[0][0]
        assert "HALO" in rendered_code
        assert "%PDF-" not in rendered_code


def test_unsupported_location_context_renders_text() -> None:
    """Verify that unsupported location context resolves readable text without %PDF- bytes."""
    sample_pdf = Path("data/incoming/20261108T070346_Halo_Enhanced__1_.pdf")
    submission = {
        "id": 252,
        "submission_type": "prose",
        "source_path": str(sample_pdf),
    }
    unsupported_item = {
        "id": 101,
        "check_id": "struct-heading-order",
        "skill_capability": "report-structure",
        "verdict": "unsupported_evidence",
        "evidence_location": "page:1",
        "evidence_text": "methods [4]",
        "failure_reason": "not_located",
    }

    import importlib

    sub_page = importlib.import_module("compliance_review.dashboard.pages.01_submission")

    with patch("streamlit.code") as mock_code:
        sub_page.render_unsupported([unsupported_item], submission=submission)
        mock_code.assert_called()
        calls = [c[0][0] for c in mock_code.call_args_list if c[0]]
        assert any("HALO" in c for c in calls)


def test_location_context_invalid_location_handled_gracefully() -> None:
    """Verify that invalid locations return None or empty string gracefully without raising."""
    sample_pdf = Path("data/incoming/20261108T070346_Halo_Enhanced__1_.pdf")
    submission = {
        "submission_type": "prose",
        "source_path": str(sample_pdf),
    }

    # Invalid page number out of range
    res_page_oob = resolve_source_span("page:999", submission)
    assert res_page_oob is None or res_page_oob == ""

    # Invalid location format
    res_invalid = resolve_source_span("invalid:foo", submission)
    assert res_invalid is None or res_invalid == ""
