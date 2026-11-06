"""Unit tests verifying pre vs post verifier metrics computation (US-35, D-018)."""

import csv
from collections import namedtuple
from pathlib import Path
from unittest.mock import MagicMock

from compliance_review.metrics.compute import compute_metrics

DbRow = namedtuple(
    "DbRow",
    [
        "submission_id",
        "check_id",
        "skill_capability",
        "verdict",
        "evidence_text",
        "check_source",
        "run_index",
    ],
)


def test_pre_post_metrics_separation(tmp_path: Path) -> None:
    """Pre-verifier treats unsupported_evidence as flag; post-verifier treats it as non-flag."""
    csv_path = tmp_path / "labels.csv"
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
        # 10 gold flag items (to pass insufficient sample guard)
        for i in range(1, 11):
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

    # In DB:
    # Submissions 1..6: verdict = 'flag' (verified)
    # Submissions 7..10: verdict = 'unsupported_evidence' (unverified model flag)
    mock_db_rows = []
    for i in range(1, 7):
        mock_db_rows.append(
            DbRow(
                submission_id=i,
                check_id="cite-doi-resolvable",
                skill_capability="citation-integrity",
                verdict="flag",
                evidence_text="10.0000/err",
                check_source="model",
                run_index=1,
            )
        )
    for i in range(7, 11):
        mock_db_rows.append(
            DbRow(
                submission_id=i,
                check_id="cite-doi-resolvable",
                skill_capability="citation-integrity",
                verdict="unsupported_evidence",
                evidence_text="hallucinated",
                check_source="model",
                run_index=1,
            )
        )

    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = mock_db_rows

    res = compute_metrics(csv_path, conn=mock_conn)
    check_m = res["capabilities"]["citation-integrity"]["checks"]["cite-doi-resolvable"]

    # Pre-verifier saw 10 flags out of 10 gold flags -> recall = 1.0, TP = 10
    assert check_m["pre_confusion_matrix_2x2"]["tp"] == 10
    assert check_m["pre_confusion_matrix_2x2"]["fn"] == 0
    assert check_m["pre_verifier_recall"] == 1.0

    # Post-verifier saw only 6 verified flags out of 10 gold flags -> recall = 0.6, TP = 6, FN = 4
    assert check_m["post_confusion_matrix_2x2"]["tp"] == 6
    assert check_m["post_confusion_matrix_2x2"]["fn"] == 4
    assert check_m["post_verifier_recall"] == 0.6
