"""Unit tests for insufficient sample guard in metrics computation (US-35)."""

import csv
from pathlib import Path
from unittest.mock import MagicMock

from compliance_review.metrics.compute import compute_metrics


def test_insufficient_sample_under_10(tmp_path: Path) -> None:
    """When a check has fewer than 10 gold flags, emit 'insufficient_sample'."""
    csv_path = tmp_path / "under_10.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "submission_id",
                "external_id",
                "skill_capability",
                "skill_version",
                "check_id",
                "gold_verdict",
                "gold_evidence_text",
                "gold_evidence_location",
                "annotator_1",
                "annotator_2",
                "adjudicator",
                "adjudication_status",
            ]
        )
        # 5 gold flags, 5 clean
        for i in range(1, 6):
            writer.writerow(
                [
                    i,
                    f"sub_{i}",
                    "citation-integrity",
                    "v1",
                    "cite-doi-resolvable",
                    "flag",
                    "10.0000/err",
                    "section:ref",
                    "a1",
                    "a2",
                    "",
                    "agreed",
                ]
            )
        for i in range(6, 11):
            writer.writerow(
                [
                    i,
                    f"sub_{i}",
                    "citation-integrity",
                    "v1",
                    "cite-doi-resolvable",
                    "no_flag",
                    "",
                    "section:ref",
                    "a1",
                    "a2",
                    "",
                    "agreed",
                ]
            )

    # Mock DB connection returning mock row results
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = []

    res = compute_metrics(csv_path, conn=mock_conn)
    check_m = res["capabilities"]["citation-integrity"]["checks"]["cite-doi-resolvable"]
    assert check_m["gold_flags"] == 5
    assert check_m["pre_verifier_precision"] == "insufficient_sample"
    assert check_m["pre_verifier_recall"] == "insufficient_sample"
    assert check_m["post_verifier_precision"] == "insufficient_sample"
    assert check_m["post_verifier_recall"] == "insufficient_sample"
    assert check_m["post_verifier_ffr"] == "insufficient_sample"


def test_sufficient_sample_at_or_over_10(tmp_path: Path) -> None:
    """When a check has >= 10 gold flags, emit numeric floats."""
    csv_path = tmp_path / "over_10.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "submission_id",
                "external_id",
                "skill_capability",
                "skill_version",
                "check_id",
                "gold_verdict",
                "gold_evidence_text",
                "gold_evidence_location",
                "annotator_1",
                "annotator_2",
                "adjudicator",
                "adjudication_status",
            ]
        )
        # 12 gold flags
        for i in range(1, 13):
            writer.writerow(
                [
                    i,
                    f"sub_{i}",
                    "citation-integrity",
                    "v1",
                    "cite-doi-resolvable",
                    "flag",
                    "10.0000/err",
                    "section:ref",
                    "a1",
                    "a2",
                    "",
                    "agreed",
                ]
            )

    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = []

    res = compute_metrics(csv_path, conn=mock_conn)
    check_m = res["capabilities"]["citation-integrity"]["checks"]["cite-doi-resolvable"]
    assert check_m["gold_flags"] == 12
    assert isinstance(check_m["pre_verifier_precision"], float)
    assert isinstance(check_m["pre_verifier_recall"], float)
    assert isinstance(check_m["post_verifier_precision"], float)
    assert isinstance(check_m["post_verifier_recall"], float)
    assert isinstance(check_m["post_verifier_ffr"], float)
