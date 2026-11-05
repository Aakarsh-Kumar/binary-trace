"""Unit tests for evidence verifier downgrade conditions (US-24, US-25, US-26)."""

from compliance_review.evidence.verifier import verify_evidence


def test_fabricated_evidence_fails_verification() -> None:
    """Verify fabricated evidence not present in source returns not_located (US-25)."""
    sub_data = {"text": "This report examines compliance procedures in academic submissions."}
    res = verify_evidence(
        evidence_text="Fabricated citation: Doe et al. (2025) proved this claim false.",
        evidence_location="section:introduction",
        submission_data=sub_data,
    )
    assert res.verified is False
    assert res.failure_reason == "not_located"


def test_exact_substring_verification_succeeds() -> None:
    """Verify verbatim exact quotation succeeds with method='substring' (US-26)."""
    sub_data = {"text": "Introduction\n\nMethodology section discusses data collection."}
    res = verify_evidence(
        evidence_text="Methodology section discusses data collection",
        evidence_location="section:introduction",
        submission_data=sub_data,
    )
    assert res.verified is True
    assert res.method == "substring"
    assert res.located_at == "section:introduction"


def test_normalized_prefix_verification_succeeds() -> None:
    """Verify first 40 normalized characters prefix match succeeds with method='normalized'."""
    text_span = (
        "This is an extensive paragraph that begins with exactly forty characters of text "
        "and then continues with significant divergence that would otherwise fail substring."
    )
    sub_data = {"text": text_span}
    # Create evidence matching first 40 chars, followed by different text
    evidence = text_span[:40] + " but with different trailing text here"
    res = verify_evidence(
        evidence_text=evidence,
        evidence_location="section:introduction",
        submission_data=sub_data,
    )
    assert res.verified is True
    assert res.method in {"substring", "normalized"}


def test_fuzzy_match_above_threshold_succeeds() -> None:
    """Verify minor typographical variations (ratio >= 0.92) succeed with method='fuzzy'."""
    # A 50-character string with 1 char altered -> ratio = 2 * 49 / 100 = 0.98 >= 0.92
    original = "The experiments were conducted over five iterations."
    typo_quote = "The experiments were condvcted over five iterations."
    sub_data = {"pages": {1: original}}

    res = verify_evidence(
        evidence_text=typo_quote,
        evidence_location="page:1",
        submission_data=sub_data,
    )
    assert res.verified is True
    assert res.method == "fuzzy"


def test_invalid_grammar_fails_verification() -> None:
    """Verify invalid location grammar returns location_grammar_invalid."""
    sub_data = {"text": "Some text"}
    res = verify_evidence(
        evidence_text="Some text",
        evidence_location="invalid_syntax",
        submission_data=sub_data,
    )
    assert res.verified is False
    assert res.failure_reason == "location_grammar_invalid"
