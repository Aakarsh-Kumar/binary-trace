"""Unit tests verifying dashboard agreement source conforms to D-031.

Agreement values MUST come from harness/k_run.compute_agreement() and never be recomputed inline.
"""

from pathlib import Path
from unittest.mock import patch

from compliance_review.dashboard.agreement import get_cached_agreement


def test_dashboard_agreement_calls_k_run() -> None:
    """Verify get_cached_agreement delegates directly to harness.k_run.compute_agreement."""
    runs = [
        [{"check_id": "c1", "verdict": "flag", "evidence_text": "e1"}],
        [{"check_id": "c1", "verdict": "flag", "evidence_text": "e1"}],
    ]
    with patch("compliance_review.dashboard.agreement.compute_agreement") as mock_calc:
        mock_calc.return_value = {"c1": {"agreement": 1.0, "evidence_jaccard": 1.0}}
        res = get_cached_agreement(runs)
        assert mock_calc.called
        assert res == {"c1": {"agreement": 1.0, "evidence_jaccard": 1.0}}


def test_no_inline_agreement_recomputation_in_dashboard() -> None:
    """Verify that no dashboard file computes agreement inline via len/sum/division."""
    dashboard_dir = Path("src/compliance_review/dashboard")
    py_files = list(dashboard_dir.glob("*.py")) + list((dashboard_dir / "pages").glob("*.py"))

    assert len(py_files) > 0, "Expected dashboard python files to exist"

    # Forbidden patterns in dashboard code indicating inline agreement recomputation
    forbidden_tokens = [
        "sum(1 for",
        "sum([1 for",
        "/ len(runs",
        "/ len(v_list",
        "/ len(verdicts",
        "/ k",
    ]

    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert (
                token not in content
            ), f"Forbidden inline agreement calculation token '{token}' found in {py_file}"
