"""Unit test asserting the frozen invariant for evidence verifier per INSTRUCTIONS.md §8."""

import inspect

from compliance_review.evidence.verifier import (
    FUZZY_THRESHOLD,
    PREFIX_LEN,
    normalize_span,
    verify_evidence,
)


def test_verifier_frozen_thresholds() -> None:
    """Verify prefix length and fuzzy ratio thresholds are strictly frozen."""
    assert PREFIX_LEN == 40, f"Invariant violation: PREFIX_LEN must be 40, got {PREFIX_LEN}"
    assert (
        FUZZY_THRESHOLD == 0.92
    ), f"Invariant violation: FUZZY_THRESHOLD must be 0.92, got {FUZZY_THRESHOLD}"


def test_verifier_signature() -> None:
    """Verify verify_evidence public signature is unchanged."""
    sig = inspect.signature(verify_evidence)
    params = list(sig.parameters.keys())
    assert params == ["evidence_text", "evidence_location", "submission_data"]


def test_normalization_invariant() -> None:
    """Verify normalization performs NFKC + whitespace collapse + casefold."""
    raw = "  Hello   \t\n  WORLD  "
    norm = normalize_span(raw)
    assert norm == "hello world"


def test_verifier_location_grammar_rejection() -> None:
    """Verify invalid location grammar returns location_grammar_invalid."""
    res = verify_evidence("some quote", "invalid_location", {"text": "some quote"})
    assert res.verified is False
    assert res.failure_reason == "location_grammar_invalid"


def test_verifier_success() -> None:
    """Verify exact substring match succeeds."""
    sub_data = {"text": "# Introduction\n\nThis is a clean report section."}
    res = verify_evidence("clean report", "section:introduction", sub_data)
    assert res.verified is True
    assert res.method == "substring"
