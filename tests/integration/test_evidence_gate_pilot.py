"""Integration tests for P1 evidence gate on pilot submissions (M1, US-19..US-28)."""

import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

from compliance_review.db.repository import get_engine
from compliance_review.harness.orchestrator import run_review
from compliance_review.ingestion.orchestrator import ingest_source

PILOT_CONFIGS = [
    ("pilot_clean_prose.md", "prose"),
    ("pilot_clean_code", "code"),
    ("pilot_clean_mixed", "mixed"),
    ("pilot_issue_doi.md", "prose"),
    ("pilot_issue_structure.md", "prose"),
    ("pilot_issue_code", "code"),
    ("pilot_rigged_biblio.md", "prose"),
    ("pilot_rigged_disclosure.md", "prose"),
    ("pilot_rigged_code", "code"),
    ("pilot_mixed_two_issues", "mixed"),
]


@pytest.fixture(scope="module")
def pilot_review_results() -> dict[str, int]:
    """Ingest and run k=3 review for all 10 pilot submissions."""
    pilots_dir = Path("data/pilots")
    sub_ids: dict[str, int] = {}

    for name, sub_type in PILOT_CONFIGS:
        source_path = pilots_dir / name
        assert source_path.exists(), f"Pilot missing: {source_path}"
        unique_ext_id = f"test-pilot-{name}-{uuid.uuid4().hex[:6]}"
        sub_id, _ = ingest_source(source_path, sub_type, external_id=unique_ext_id)
        run_review(sub_id, k=3, deterministic_only=False, skill_status="evaluating")
        sub_ids[name] = sub_id

    return sub_ids


def test_evidence_gate_four_conditions(pilot_review_results: dict[str, int]) -> None:
    """Verify all 4 P1 evidence gate conditions across pilot submissions."""
    engine = get_engine()
    sub_id_list = list(pilot_review_results.values())

    with engine.connect() as conn:
        # Gate Condition (a): Every checklist_verdicts row with verdict='flag'
        # has exactly one matching evidence_verifications row with verified=True
        flag_verdicts = conn.execute(
            text(
                "SELECT cv.id, cv.check_id, cv.verdict, ev.verified "
                "FROM checklist_verdicts cv "
                "JOIN skill_executions se ON cv.execution_id = se.id "
                "LEFT JOIN evidence_verifications ev ON cv.id = ev.verdict_id "
                "WHERE se.submission_id IN :sub_ids AND cv.verdict = 'flag'"
            ),
            {"sub_ids": tuple(sub_id_list)},
        ).fetchall()

        for fv in flag_verdicts:
            assert fv[3] == 1, f"Flag verdict id={fv[0]} has verified={fv[3]}, expected True"

        # Gate Condition (b): >= 1 pilot produced >= 1 unsupported_evidence row
        unsupported_rows = conn.execute(
            text(
                "SELECT cv.id, cv.check_id, se.submission_id "
                "FROM checklist_verdicts cv "
                "JOIN skill_executions se ON cv.execution_id = se.id "
                "WHERE se.submission_id IN :sub_ids AND cv.verdict = 'unsupported_evidence'"
            ),
            {"sub_ids": tuple(sub_id_list)},
        ).fetchall()

        assert len(unsupported_rows) >= 1, "Evidence gate must downgrade >= 1 ungrounded flag"

        # Gate Condition (c): k=3 rows in skill_executions per (pilot, capability)
        exec_counts = conn.execute(
            text(
                "SELECT submission_id, skill_capability, COUNT(*) as cnt "
                "FROM skill_executions "
                "WHERE submission_id IN :sub_ids "
                "GROUP BY submission_id, skill_capability"
            ),
            {"sub_ids": tuple(sub_id_list)},
        ).fetchall()

        assert len(exec_counts) > 0
        for ec in exec_counts:
            assert ec[2] == 3, f"Expected k=3 executions for sub={ec[0]} cap={ec[1]}, found {ec[2]}"

        # Gate Condition (d): Every skill_executions row has non-null model_digest
        executions = conn.execute(
            text(
                "SELECT id, model_digest, model_name FROM skill_executions "
                "WHERE submission_id IN :sub_ids"
            ),
            {"sub_ids": tuple(sub_id_list)},
        ).fetchall()

        for ex in executions:
            assert (
                ex[1] is not None and len(ex[1]) > 0
            ), f"Execution id={ex[0]} missing model_digest"
