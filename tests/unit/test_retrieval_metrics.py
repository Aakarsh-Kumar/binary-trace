"""Unit tests for retrieval metrics computation (US-18, D-027).

Assertions:
a) Formula correctness on a synthetic fixture (10 fake submissions with
   known-correct gold -> expect recall=1.0, p@1=1.0, over-retrieval=0.0).
b) HSR@K sensitivity: if a 'draft' skill is added to candidates above 0.30,
   HSR@K increases monotonically.
c) Read-only contract: assert no INSERT/UPDATE/DELETE queries are executed.
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))
from compute_retrieval_metrics import (  # noqa: E402
    calculate_retrieval_metrics,
    main,
)

FixtureData = tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[tuple[str, str], str],
]


@pytest.fixture
def synthetic_perfect_fixture() -> FixtureData:
    """Fixture with 10 submissions where retrieval perfectly matches gold."""
    gold_subs = []
    db_events = {}
    skill_statuses = {
        ("code-quality", "v2"): "evaluating",
        ("code-quality", "v1"): "draft",
        ("citation-integrity", "v2"): "evaluating",
        ("citation-integrity", "v1"): "draft",
    }

    for i in range(1, 11):
        ext_id = f"fake_code_{i:02d}"
        gold_subs.append(
            {
                "external_id": ext_id,
                "submission_type": "code",
                "word_count": 0,
                "references_present": False,
                "disclosure_present": False,
            }
        )
        db_events[ext_id] = {
            "selected": [{"capability": "code-quality", "version": "v2"}],
            "candidates": [
                {"capability": "code-quality", "version": "v2", "score": 0.85},
                {"capability": "code-quality", "version": "v1", "score": 0.15},  # below 0.30
            ],
            "latency_ms": 120,
        }

    return gold_subs, db_events, skill_statuses


def test_retrieval_metrics_formula_correctness(
    synthetic_perfect_fixture: FixtureData,
) -> None:
    """Assertion (a): Verify formula correctness on synthetic fixture."""
    gold_subs, db_events, skill_statuses = synthetic_perfect_fixture

    res = calculate_retrieval_metrics(
        submissions_gold=gold_subs,
        db_events=db_events,
        skill_statuses=skill_statuses,
        min_candidate_score=0.30,
    )

    summary = res["summary"]
    assert (
        summary["capability_recall"] == 1.0
    ), f"Expected recall=1.0, got {summary['capability_recall']}"
    assert (
        summary["version_precision@1"] == 1.0
    ), f"Expected p@1=1.0, got {summary['version_precision@1']}"
    assert (
        summary["over_retrieval_rate"] == 0.0
    ), f"Expected over_retrieval=0.0, got {summary['over_retrieval_rate']}"
    assert summary["HSR@K"] == 0.0, f"Expected HSR@K=0.0, got {summary['HSR@K']}"


def test_hsr_at_k_sensitivity(
    synthetic_perfect_fixture: FixtureData,
) -> None:
    """Assertion (b): Verify HSR@K sensitivity: adding draft candidate increases HSR@K."""
    gold_subs, db_events, skill_statuses = synthetic_perfect_fixture

    # Baseline HSR@K with candidate score 0.15 (< 0.30)
    res_base = calculate_retrieval_metrics(
        submissions_gold=gold_subs,
        db_events=db_events,
        skill_statuses=skill_statuses,
        min_candidate_score=0.30,
    )
    assert res_base["summary"]["HSR@K"] == 0.0

    # Add a draft skill with score 0.40 (>= 0.30) to 3 submissions
    for i in range(1, 4):
        ext_id = f"fake_code_{i:02d}"
        db_events[ext_id]["candidates"].append(
            {"capability": "code-quality", "version": "v1", "score": 0.40}
        )

    res_step1 = calculate_retrieval_metrics(
        submissions_gold=gold_subs,
        db_events=db_events,
        skill_statuses=skill_statuses,
        min_candidate_score=0.30,
    )
    assert res_step1["summary"]["HSR@K"] == 0.3  # 3 of 10 queries
    assert res_step1["summary"]["HSR@K"] > res_base["summary"]["HSR@K"]

    # Add draft candidate with score >= 0.30 to 4 more submissions
    for i in range(4, 8):
        ext_id = f"fake_code_{i:02d}"
        db_events[ext_id]["candidates"].append(
            {"capability": "code-quality", "version": "v1", "score": 0.45}
        )

    res_step2 = calculate_retrieval_metrics(
        submissions_gold=gold_subs,
        db_events=db_events,
        skill_statuses=skill_statuses,
        min_candidate_score=0.30,
    )
    assert res_step2["summary"]["HSR@K"] == 0.7  # 7 of 10 queries
    assert res_step2["summary"]["HSR@K"] > res_step1["summary"]["HSR@K"]


def test_retrieval_metrics_read_only_contract(tmp_path: Path) -> None:
    """Assertion (c): Read-only contract: verify no INSERT/UPDATE/DELETE queries are executed."""
    mock_conn = MagicMock()
    executed_statements: list[str] = []

    def fake_execute(statement: Any, *args: Any, **kwargs: Any) -> MagicMock:
        sql_str = str(statement).strip().upper()
        executed_statements.append(sql_str)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        return mock_result

    mock_conn.execute.side_effect = fake_execute

    main(
        conn=mock_conn,
        out_json=tmp_path / "mock_eval.json",
        out_md=tmp_path / "mock_eval.md",
    )

    assert len(executed_statements) > 0, "Expected at least one SELECT query"
    for sql in executed_statements:
        assert not sql.startswith("INSERT"), f"Read-only violation: INSERT detected: {sql}"
        assert not sql.startswith("UPDATE"), f"Read-only violation: UPDATE detected: {sql}"
        assert not sql.startswith("DELETE"), f"Read-only violation: DELETE detected: {sql}"
        assert not sql.startswith("DROP"), f"Read-only violation: DROP detected: {sql}"
        assert not sql.startswith("ALTER"), f"Read-only violation: ALTER detected: {sql}"
        assert sql.startswith("SELECT"), f"Expected SELECT query, got: {sql}"
