"""Integration test verifying metrics read-only contract (US-35).

Asserts that computing metrics performs strictly SELECT queries and zero DB writes.
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

from sqlalchemy import Connection
from typer.testing import CliRunner

import compliance_review.db.repository as repo
from compliance_review.cli import app
from compliance_review.metrics.compute import compute_metrics


def test_metrics_readonly_contract_function(tmp_path: Path) -> None:
    """Ensure compute_metrics function only executes SELECT queries and never writes."""
    labels_file = Path("data/labels/sample_5.csv")
    assert labels_file.exists()

    executed_statements: list[str] = []
    original_execute = Connection.execute

    def spy_execute(self: Connection, statement: Any, *args: Any, **kwargs: Any) -> Any:
        sql_str = str(statement)
        executed_statements.append(sql_str)
        return original_execute(self, statement, *args, **kwargs)

    with patch.object(Connection, "execute", spy_execute):
        with patch.object(repo, "append_audit", wraps=repo.append_audit) as mock_audit:
            res = compute_metrics(labels_file)
            assert "summary" in res
            mock_audit.assert_not_called()

    assert len(executed_statements) > 0, "Expected at least one SQL execution"
    for stmt in executed_statements:
        norm = stmt.strip().upper()
        assert norm.startswith("SELECT"), f"Non-SELECT statement executed: {stmt}"
        assert not any(
            kw in norm
            for kw in [
                "INSERT INTO",
                "UPDATE ",
                "DELETE FROM",
                "DROP TABLE",
                "ALTER TABLE",
                "CREATE TABLE",
            ]
        ), f"Write statement detected: {stmt}"


def test_metrics_cli_readonly_contract(tmp_path: Path) -> None:
    """Ensure CLI 'compliance-review metrics --labels ...' performs only SELECT queries."""
    labels_file = Path("data/labels/sample_5.csv")
    out_file = tmp_path / "metrics.json"

    executed_statements: list[str] = []
    original_execute = Connection.execute

    def spy_execute(self: Connection, statement: Any, *args: Any, **kwargs: Any) -> Any:
        sql_str = str(statement)
        executed_statements.append(sql_str)
        return original_execute(self, statement, *args, **kwargs)

    runner = CliRunner()
    with patch.object(Connection, "execute", spy_execute):
        with patch.object(repo, "append_audit", wraps=repo.append_audit) as mock_audit:
            result = runner.invoke(
                app,
                ["metrics", "--labels", str(labels_file), "--out", str(out_file)],
            )
            assert result.exit_code == 0, f"CLI failed: {result.output}"
            mock_audit.assert_not_called()

    assert len(executed_statements) > 0, "Expected at least one SQL execution"
    for stmt in executed_statements:
        norm = stmt.strip().upper()
        assert norm.startswith("SELECT"), f"Non-SELECT statement executed: {stmt}"
        assert not any(
            kw in norm
            for kw in [
                "INSERT INTO",
                "UPDATE ",
                "DELETE FROM",
                "DROP TABLE",
                "ALTER TABLE",
                "CREATE TABLE",
            ]
        ), f"Write statement detected: {stmt}"
