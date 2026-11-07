"""Cached repository queries conforming to ARCHITECTURE.md §10.4 and D-030."""

from typing import Any

import streamlit as st

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


@st.cache_data(ttl=60)
def cached_list_submissions(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """Cached wrapper around list_submissions (D-030)."""
    return list_submissions(limit=limit, offset=offset)


@st.cache_data(ttl=60)
def cached_get_submission_by_external_id(external_id: str) -> dict[str, Any] | None:
    """Cached wrapper around get_submission_by_external_id (D-030)."""
    return get_submission_by_external_id(external_id)


@st.cache_data(ttl=60)
def cached_get_submission_by_id(submission_id: int) -> dict[str, Any] | None:
    """Cached wrapper around get_submission_by_id (D-030)."""
    return get_submission_by_id(submission_id)


@st.cache_data(ttl=60)
def cached_get_retrieval_event_for_submission(submission_id: int) -> dict[str, Any] | None:
    """Cached wrapper around get_retrieval_event_for_submission (D-030)."""
    return get_retrieval_event_for_submission(submission_id)


@st.cache_data(ttl=60)
def cached_get_skill_executions_for_submission(submission_id: int) -> list[dict[str, Any]]:
    """Cached wrapper around get_skill_executions_for_submission (D-030)."""
    return get_skill_executions_for_submission(submission_id)


@st.cache_data(ttl=60)
def cached_get_verdicts_for_execution(execution_id: int) -> list[dict[str, Any]]:
    """Cached wrapper around get_verdicts_for_execution (D-030)."""
    return get_verdicts_for_execution(execution_id)


@st.cache_data(ttl=60)
def cached_get_verdicts_for_submission(submission_id: int) -> list[dict[str, Any]]:
    """Cached wrapper around get_verdicts_for_submission (D-030)."""
    return get_verdicts_for_submission(submission_id)


@st.cache_data(ttl=60)
def cached_get_evidence_verifications_for_verdict(verdict_id: int) -> list[dict[str, Any]]:
    """Cached wrapper around get_evidence_verifications_for_verdict (D-030)."""
    return get_evidence_verifications_for_verdict(verdict_id)


@st.cache_data(ttl=60)
def cached_get_reviewer_feedback_for_submission(submission_id: int) -> list[dict[str, Any]]:
    """Cached wrapper around get_reviewer_feedback_for_submission (D-030)."""
    return get_reviewer_feedback_for_submission(submission_id)
