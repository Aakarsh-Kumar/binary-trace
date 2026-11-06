"""Unit tests for gold labels schema validation (US-35, D-010)."""

import csv
from pathlib import Path

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

ALLOWED_CAPABILITIES = {
    "citation-integrity",
    "report-structure",
    "code-quality",
    "rai-disclosure",
}

ALLOWED_VERDICTS = {"flag", "no_flag", "not_applicable"}
ALLOWED_STATUSES = {"pending", "agreed", "adjudicated"}


def test_template_csv_header() -> None:
    """TEMPLATE.csv must contain exactly the 12 columns in order and 0 data rows."""
    template_path = Path("data/labels/TEMPLATE.csv")
    assert template_path.exists()

    with template_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == EXPECTED_COLUMNS
        # No data rows
        rows = list(reader)
        assert len(rows) == 0


def test_sample_5_conforms_to_schema() -> None:
    """sample_5.csv conforms to the 12-column schema with valid enum values."""
    sample_path = Path("data/labels/sample_5.csv")
    assert sample_path.exists()

    with sample_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == EXPECTED_COLUMNS
        rows = list(reader)
        assert len(rows) == 5

        for r in rows:
            assert int(r["submission_id"]) > 0
            assert len(r["external_id"]) > 0
            assert r["skill_capability"] in ALLOWED_CAPABILITIES
            assert r["gold_verdict"] in ALLOWED_VERDICTS
            if r["gold_verdict"] == "flag":
                assert len(r["gold_evidence_text"]) > 0
                assert len(r["gold_evidence_location"]) > 0
            assert r["adjudication_status"] in ALLOWED_STATUSES
