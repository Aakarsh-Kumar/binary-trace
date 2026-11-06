"""Unit tests for labels bootstrap command (US-35, Mode B)."""

import csv
import json
from pathlib import Path

from typer.testing import CliRunner

from compliance_review.cli import app

EXPECTED_COLUMNS = [
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


def test_labels_bootstrap_cli(tmp_path: Path) -> None:
    """labels bootstrap CLI creates 12-column CSV with agent:bootstrap annotations."""
    # Create minimal submissions manifest referencing known ingested submission
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "submissions": [
                    {"submission_id": 111, "external_id": "eval_prose_01"},
                    {"submission_id": 112, "external_id": "eval_prose_02"},
                ]
            }
        ),
        encoding="utf-8",
    )

    out_csv = tmp_path / "bootstrap_test.csv"

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["labels", "bootstrap", "--submissions", str(manifest_path), "--out", str(out_csv)],
    )

    assert result.exit_code == 0, f"Bootstrap CLI failed: {result.output}"
    assert out_csv.exists()

    with out_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == EXPECTED_COLUMNS
        rows = list(reader)
        assert len(rows) > 0

        for r in rows:
            assert r["submission_id"] in ("111", "112")
            assert r["annotator_1"] == "agent:bootstrap"
            assert r["adjudication_status"] == "pending"
            assert r["gold_verdict"] in ("flag", "no_flag", "not_applicable")
