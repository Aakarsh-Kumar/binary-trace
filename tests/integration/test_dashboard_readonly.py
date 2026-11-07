"""Integration tests verifying read-only contract and render integrity of dashboard.

Conforms to ARCHITECTURE.md §10.2 and §10.4 (D-030, D-032).
"""

from __future__ import annotations

import importlib
import sqlite3
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT, TINYINT
from sqlalchemy.ext.compiler import compiles

from compliance_review.db import repository
from compliance_review.db.tables import metadata, submissions

@compiles(BIGINT, "sqlite")
def _compile_bigint_sqlite(type_: Any, compiler: Any, **kw: Any) -> str:
    return "INTEGER"

@compiles(TINYINT, "sqlite")
def _compile_tinyint_sqlite(type_: Any, compiler: Any, **kw: Any) -> str:
    return "INTEGER"

@compiles(LONGTEXT, "sqlite")
def _compile_longtext_sqlite(type_: Any, compiler: Any, **kw: Any) -> str:
    return "TEXT"

submission_page = importlib.import_module("compliance_review.dashboard.pages.01_submission")
render_header = submission_page.render_header
render_retrieval_trace = submission_page.render_retrieval_trace
render_findings = submission_page.render_findings
render_disagreement = submission_page.render_disagreement
render_passed_checks = submission_page.render_passed_checks
render_unsupported = submission_page.render_unsupported
render_audit_footer = submission_page.render_audit_footer
render_submission_page = submission_page.render_submission_page

# Authorized D-030 read query helpers
D030_AUTHORIZED_READS = {
    "get_submission_by_external_id",
    "get_submission_by_id",
    "get_retrieval_event_for_submission",
    "get_skill_executions_for_submission",
    "get_verdicts_for_submission",
    "get_verdicts_for_execution",
    "get_evidence_verifications_for_verdict",
    "get_reviewer_feedback_for_submission",
    "list_submissions",
}

# Known DB write functions that MUST NEVER be called during page rendering
KNOWN_WRITE_FUNCTIONS = {
    "create_submission",
    "record_retrieval_event",
    "record_reviewer_feedback",
    "append_audit",
    "record_execution",
    "record_verdict",
    "record_evidence_verification",
}


@pytest.fixture
def forbidden_st_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monkeypatch st.write to raise an AssertionError if ever invoked."""

    def _fail_on_write(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("st.write() was called! Dashboard invariant violated.")

    monkeypatch.setattr(st, "write", _fail_on_write)


def test_render_functions_empty_and_mock_data_no_st_write(
    forbidden_st_write: None,
) -> None:
    """Requirement 1 & 4: All 7 render functions can be called with empty/mock data and never call st.write."""
    # 1. Header
    render_header(None)
    render_header({
        "id": 1,
        "external_id": "test_01",
        "submission_type": "code",
        "ingested_at": "2026-11-08T00:00:00Z",
    })

    # 2. Retrieval trace
    render_retrieval_trace(None)
    render_retrieval_trace({
        "selected_skills": ["skills/code_quality/v1"],
        "gate_conditions": ["has_python_files"],
        "duration_ms": 120,
    })

    # 3. Findings
    render_findings([])
    render_findings(
        [
            {
                "id": 10,
                "skill_capability": "code-style",
                "check_id": "code-ruff-clean",
                "severity": "high",
                "confidence": 0.95,
                "evidence_text": "def test():\n    pass",
                "evidence_location": "test.py:1",
            }
        ],
        submission={"id": 1, "source_path": "test.py"},
        existing_feedback=[],
    )

    # 4. Disagreement
    render_disagreement([], {})
    render_disagreement(
        [
            {
                "check_id": "code-ruff-clean",
                "capability": "code-style",
                "agreement": 0.67,
            }
        ],
        {
            "code-style": [
                {
                    "run_number": 1,
                    "verdicts": [
                        {
                            "check_id": "code-ruff-clean",
                            "verdict": "flag",
                            "confidence": 0.9,
                            "evidence_text": "bad",
                        }
                    ],
                },
                {
                    "run_number": 2,
                    "verdicts": [
                        {
                            "check_id": "code-ruff-clean",
                            "verdict": "pass",
                            "confidence": 0.8,
                            "evidence_text": "",
                        }
                    ],
                },
                {
                    "run_number": 3,
                    "verdicts": [
                        {
                            "check_id": "code-ruff-clean",
                            "verdict": "flag",
                            "confidence": 0.95,
                            "evidence_text": "bad",
                        }
                    ],
                },
            ]
        },
    )

    # 5. Passed checks
    render_passed_checks([])
    render_passed_checks([
        {
            "id": 20,
            "check_id": "cite-doi-resolvable",
            "skill_capability": "citation-integrity",
            "verdict": "pass",
            "confidence": 0.99,
        }
    ])

    # 6. Unsupported evidence
    render_unsupported([])
    render_unsupported([
        {
            "id": 30,
            "check_id": "cite-no-duplicates",
            "skill_capability": "citation-integrity",
            "evidence_text": "phantom reference",
            "failure_reason": "fuzzy_below_threshold",
        }
    ])

    # 7. Audit footer
    render_audit_footer({
        "model_name": "qwen3:4b",
        "model_digest": "sha256:1234abcd",
        "skill_versions": {"citation-integrity": "1.0.0"},
        "prompt_hashes": {"citation-integrity": "hash123"},
        "harness_version": "0.1.0",
    })


def test_render_submission_page_read_only_contract(
    monkeypatch: pytest.MonkeyPatch,
    forbidden_st_write: None,
) -> None:
    """Requirement 2: render_submission_page calls only D-030 reads and zero DB writes."""
    called_repository_funcs: list[str] = []

    def make_spy(func_name: str, return_value: Any) -> Any:
        def spy(*args: Any, **kwargs: Any) -> Any:
            called_repository_funcs.append(func_name)
            return return_value

        return spy

    # Spy and mock all D-030 query helpers in compliance_review.db.repository
    mock_submission = {
        "id": 1,
        "external_id": "eval_test_001",
        "submission_type": "code",
        "source_path": "README.md",
        "ingested_at": "2026-11-08T00:00:00Z",
    }
    mock_retrieval = {
        "id": 1,
        "submission_id": 1,
        "selected_skills": ["skills/code_quality/v1"],
        "gate_conditions": ["has_python_files"],
        "duration_ms": 100,
    }
    mock_executions = [
        {
            "id": 100,
            "submission_id": 1,
            "skill_id": 1,
            "skill_name": "code_quality",
            "skill_version": "1.0.0",
            "skill_capability": "code-style",
            "run_number": 1,
            "model_name": "qwen3:4b",
            "model_digest": "sha256:mockdigest",
            "prompt_sha256": "sha256:prompthash",
        }
    ]
    mock_verdicts = [
        {
            "id": 200,
            "execution_id": 100,
            "check_id": "code-ruff-clean",
            "skill_capability": "code-style",
            "verdict": "flag",
            "confidence": 0.9,
            "evidence_text": "import os",
            "evidence_location": "README.md:1",
            "verified": True,
        }
    ]
    mock_evidence = [
        {
            "id": 300,
            "verdict_id": 200,
            "verified": True,
            "fuzzy_score": 1.0,
            "failure_reason": None,
        }
    ]

    for read_fn in D030_AUTHORIZED_READS:
        if hasattr(repository, read_fn):
            ret: Any = []
            if "submission_by" in read_fn:
                ret = mock_submission
            elif "retrieval_event" in read_fn:
                ret = mock_retrieval
            elif "executions" in read_fn:
                ret = mock_executions
            elif "verdicts" in read_fn:
                ret = mock_verdicts
            elif "evidence" in read_fn:
                ret = mock_evidence
            elif "list_submissions" in read_fn:
                ret = [mock_submission]
            monkeypatch.setattr(repository, read_fn, make_spy(read_fn, ret))

    # Also spy on all write functions to assert they are NEVER called
    for write_fn in KNOWN_WRITE_FUNCTIONS:
        if hasattr(repository, write_fn):
            monkeypatch.setattr(repository, write_fn, make_spy(write_fn, None))

    # Clear streamlit cache data to ensure spies are reached
    st.cache_data.clear()

    # Render submission page with external_id
    render_submission_page("eval_test_001")

    # Assertions
    # 1. Zero writes called
    for write_fn in KNOWN_WRITE_FUNCTIONS:
        assert write_fn not in called_repository_funcs, (
            f"Write function {write_fn} was called during page rendering!"
        )

    # 2. All called repository functions must be in D030_AUTHORIZED_READS
    for called_fn in called_repository_funcs:
        assert called_fn in D030_AUTHORIZED_READS, (
            f"Unauthorized repository function {called_fn} was called!"
        )


def test_reviewer_feedback_action_handler_isolated_write(tmp_path: Any) -> None:
    """Requirement 3: Reviewer feedback writes exactly 1 feedback + 1 audit_log entry via real SQLite fixture."""
    # Create isolated sqlite database
    db_file = tmp_path / "test_feedback.db"
    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url)
    metadata.create_all(engine)

    # Insert prerequisite submission row
    with engine.begin() as conn:
        conn.execute(
            submissions.insert().values(
                external_id="test_sub_fb_01",
                submission_type="code",
                source_path=str(tmp_path),
                content_sha256="mockcontenthash",
            )
        )

    with patch("compliance_review.db.repository.get_engine", return_value=engine):
        # Verify initial state of reviewer_feedback
        initial_fb = repository.get_reviewer_feedback_for_submission(1)
        assert len(initial_fb) == 0

        # Call record_reviewer_feedback
        fb_id = repository.record_reviewer_feedback(
            submission_id=1,
            verdict_id=None,
            reviewer_id="reviewer:alice",
            action="override",
            reason_code="policy_exception",
            comment="Authorized exception for test module",
        )
        assert fb_id > 0

    # Verify exact count in database using raw SQLite inspection
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM reviewer_feedback WHERE submission_id = ?", (1,))
    fb_count = cur.fetchone()[0]
    assert fb_count == 1, f"Expected exactly 1 reviewer_feedback row, found {fb_count}"

    cur.execute(
        "SELECT COUNT(*) FROM audit_log WHERE table_name = 'reviewer_feedback' AND row_id = ?",
        (fb_id,),
    )
    audit_count = cur.fetchone()[0]
    assert audit_count == 1, f"Expected exactly 1 audit_log row, found {audit_count}"

    conn.close()
