"""Unit tests asserting read-only contract for D-030 repository helpers."""

from typing import Any
from unittest.mock import MagicMock, patch

from compliance_review.db.repository import (
    get_evidence_verifications_for_verdict,
    get_retrieval_event_for_submission,
    get_reviewer_feedback_for_submission,
    get_skill_executions_for_submission,
    get_submission_by_external_id,
    get_submission_by_id,
    get_verdicts_for_execution,
    get_verdicts_for_submission,
    list_submissions,
)


def test_repository_read_helpers_are_strictly_readonly() -> None:
    """Verify that all D-030 read helpers execute only SELECT statements without writes."""
    executed_statements: list[str] = []

    mock_conn = MagicMock()

    def fake_execute(statement: Any, *args: Any, **kwargs: Any) -> MagicMock:
        sql_str = str(statement).strip().upper()
        executed_statements.append(sql_str)
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = {"id": 1}
        mock_result.mappings.return_value.all.return_value = [{"id": 1}]
        return mock_result

    mock_conn.execute.side_effect = fake_execute

    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    with patch("compliance_review.db.repository.get_engine", return_value=mock_engine):
        get_submission_by_id(1)
        get_submission_by_external_id("sub_01")
        get_retrieval_event_for_submission(1)
        get_skill_executions_for_submission(1)
        get_verdicts_for_execution(1)
        get_verdicts_for_submission(1)
        get_evidence_verifications_for_verdict(1)
        get_reviewer_feedback_for_submission(1)
        list_submissions(limit=10, offset=0)

    assert len(executed_statements) == 9

    for sql in executed_statements:
        assert sql.startswith("SELECT"), f"Statement is not a SELECT: {sql}"
        assert "INSERT" not in sql
        assert "UPDATE" not in sql
        assert "DELETE" not in sql
        assert "DROP" not in sql


def test_retrieval_event_ordered_by_id_desc() -> None:
    """Verify get_retrieval_event_for_submission orders by id DESC limit 1 (D-030)."""
    executed_statements: list[str] = []

    mock_conn = MagicMock()

    def fake_execute(statement: Any, *args: Any, **kwargs: Any) -> MagicMock:
        sql_str = str(statement).strip().upper()
        executed_statements.append(sql_str)
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = {"id": 2, "submission_id": 1}
        return mock_result

    mock_conn.execute.side_effect = fake_execute

    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    with patch("compliance_review.db.repository.get_engine", return_value=mock_engine):
        res = get_retrieval_event_for_submission(1)

    assert res == {"id": 2, "submission_id": 1}
    assert len(executed_statements) == 1
    stmt = executed_statements[0]
    assert "ORDER BY RETRIEVAL_EVENTS.ID DESC" in stmt
    assert "LIMIT" in stmt
