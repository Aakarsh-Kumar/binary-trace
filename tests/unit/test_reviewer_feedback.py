"""Unit tests for reviewer feedback persistence and audit logging (US-31/32)."""

from sqlalchemy import select

from compliance_review.db.engine import get_engine
from compliance_review.db.repository import create_submission, record_reviewer_feedback
from compliance_review.db.tables import audit_log, reviewer_feedback


def test_record_reviewer_feedback_and_audit() -> None:
    """Reviewer feedback is inserted and produces an audit_log row."""
    import uuid

    unique_ext = f"test-rf-{uuid.uuid4().hex[:8]}"
    # Create test submission
    sub_id = create_submission(
        external_id=unique_ext,
        submission_type="prose",
        source_path="tests/fixtures/sample.md",
        content_sha256="abc1234567890123456789012345678901234567890123456789012345678901",
    )

    feedback_id = record_reviewer_feedback(
        submission_id=sub_id,
        verdict_id=None,
        reviewer_id="reviewer_alice",
        action="override",
        reason_code="policy_exception",
        comment="Allowed exemption per department guideline",
    )

    assert feedback_id > 0

    engine = get_engine()
    with engine.connect() as conn:
        # Verify reviewer_feedback row
        rf_row = conn.execute(
            select(reviewer_feedback).where(reviewer_feedback.c.id == feedback_id)
        ).fetchone()
        assert rf_row is not None
        assert rf_row.submission_id == sub_id
        assert rf_row.reviewer_id == "reviewer_alice"
        assert rf_row.action == "override"
        assert rf_row.reason_code == "policy_exception"
        assert rf_row.comment == "Allowed exemption per department guideline"

        # Verify audit_log row
        al_row = conn.execute(
            select(audit_log)
            .where(
                audit_log.c.table_name == "reviewer_feedback",
                audit_log.c.row_id == feedback_id,
            )
            .order_by(audit_log.c.id.desc())
        ).fetchone()
        assert al_row is not None
        assert al_row.actor == "reviewer_alice"
        assert al_row.action == "create_reviewer_feedback"
        assert al_row.after_json["action"] == "override"
