"""Database repository enforcing transaction atomicity and append-only audit trail."""

from typing import Any

from sqlalchemy import Connection, select

from compliance_review.db.engine import get_engine
from compliance_review.db.tables import (
    audit_log,
    checklist_verdicts,
    evidence_verifications,
    retrieval_events,
    skill_executions,
    submissions,
)
from compliance_review.errors import DatabaseError


def append_audit(
    conn: Connection,
    actor: str,
    action: str,
    table_name: str,
    row_id: int | None,
    before_json: dict[str, Any] | None = None,
    after_json: dict[str, Any] | None = None,
) -> int:
    """The ONLY function in codebase authorised to insert into audit_log (INSTRUCTIONS.md §7)."""
    stmt = audit_log.insert().values(
        actor=actor,
        action=action,
        table_name=table_name,
        row_id=row_id,
        before_json=before_json,
        after_json=after_json,
    )
    result = conn.execute(stmt)
    pk = result.inserted_primary_key
    inserted_id = pk[0] if pk is not None else 0
    return int(inserted_id)


def create_submission(
    external_id: str,
    submission_type: str,
    source_path: str,
    content_sha256: str,
    actor: str = "operator:cli",
) -> int:
    """Insert a new submission and audit record within a single transaction."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            stmt = submissions.insert().values(
                external_id=external_id,
                submission_type=submission_type,
                source_path=source_path,
                content_sha256=content_sha256,
            )
            result = conn.execute(stmt)
            pk = result.inserted_primary_key
            sub_id = int(pk[0]) if pk is not None else 0

            after_state = {
                "id": sub_id,
                "external_id": external_id,
                "submission_type": submission_type,
                "source_path": source_path,
                "content_sha256": content_sha256,
            }
            append_audit(
                conn,
                actor=actor,
                action="create_submission",
                table_name="submissions",
                row_id=sub_id,
                before_json=None,
                after_json=after_state,
            )
            return sub_id
    except Exception as exc:
        raise DatabaseError(f"Failed to create submission {external_id}: {exc}") from exc


def get_submission_by_id(submission_id: int) -> dict[str, Any] | None:
    """Retrieve submission by primary key."""
    engine = get_engine()
    with engine.connect() as conn:
        stmt = select(submissions).where(submissions.c.id == submission_id)
        row = conn.execute(stmt).mappings().first()
        return dict(row) if row else None


def get_submission_by_external_id(external_id: str) -> dict[str, Any] | None:
    """Retrieve submission by external identifier."""
    engine = get_engine()
    with engine.connect() as conn:
        stmt = select(submissions).where(submissions.c.external_id == external_id)
        row = conn.execute(stmt).mappings().first()
        return dict(row) if row else None


def record_retrieval_event(
    submission_id: int,
    capability_set: dict[str, Any],
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    token_budget: int,
    latency_ms: int,
    actor: str = "agent:retrieval",
) -> int:
    """Insert retrieval event and audit record."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            stmt = retrieval_events.insert().values(
                submission_id=submission_id,
                capability_set=capability_set,
                candidates=candidates,
                selected=selected,
                token_budget=token_budget,
                latency_ms=latency_ms,
            )
            result = conn.execute(stmt)
            pk = result.inserted_primary_key
            event_id = int(pk[0]) if pk is not None else 0

            append_audit(
                conn,
                actor=actor,
                action="record_retrieval_event",
                table_name="retrieval_events",
                row_id=event_id,
                before_json=None,
                after_json={"id": event_id, "submission_id": submission_id},
            )
            return event_id
    except Exception as exc:
        raise DatabaseError(f"Failed to record retrieval event: {exc}") from exc


def record_deterministic_execution_and_verdicts(
    submission_id: int,
    capability: str,
    verdicts_data: list[dict[str, Any]],
    latency_ms: int,
    actor: str = "agent:deterministic_check",
) -> int:
    """Record a deterministic skill execution and its checklist verdicts with audit logs."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            exec_stmt = skill_executions.insert().values(
                submission_id=submission_id,
                skill_capability=capability,
                skill_version="v1",
                run_index=1,
                model_name="deterministic_harness",
                model_digest="0" * 64,
                prompt_sha256="0" * 64,
                raw_output=None,
                parsed_output={"verdicts": verdicts_data},
                status="ok",
                latency_ms=latency_ms,
            )
            exec_res = conn.execute(exec_stmt)
            exec_pk = exec_res.inserted_primary_key
            execution_id = int(exec_pk[0]) if exec_pk is not None else 0

            append_audit(
                conn,
                actor=actor,
                action="create_skill_execution",
                table_name="skill_executions",
                row_id=execution_id,
                before_json=None,
                after_json={
                    "id": execution_id,
                    "submission_id": submission_id,
                    "capability": capability,
                },
            )

            for vd in verdicts_data:
                cv_stmt = checklist_verdicts.insert().values(
                    execution_id=execution_id,
                    check_id=vd["check_id"],
                    verdict=vd["verdict"],
                    severity=vd["severity"],
                    evidence_text=vd.get("evidence_text"),
                    evidence_location=vd.get("evidence_location"),
                    confidence=vd.get("confidence", 1.0),
                )
                cv_res = conn.execute(cv_stmt)
                cv_pk = cv_res.inserted_primary_key
                cv_id = int(cv_pk[0]) if cv_pk is not None else 0

                append_audit(
                    conn,
                    actor=actor,
                    action="create_checklist_verdict",
                    table_name="checklist_verdicts",
                    row_id=cv_id,
                    before_json=None,
                    after_json={
                        "id": cv_id,
                        "execution_id": execution_id,
                        "check_id": vd["check_id"],
                    },
                )

            return execution_id
    except Exception as exc:
        raise DatabaseError(f"Failed to record execution and verdicts: {exc}") from exc


def write_evidence_verification(
    conn: Connection,
    verdict_id: int,
    verified: bool,
    method: str,
    located_at: str | None = None,
    failure_reason: str | None = None,
    actor: str = "agent:evidence_verifier",
) -> int:
    """Insert a row into evidence_verifications and record to audit_log (US-24, US-26)."""
    stmt = evidence_verifications.insert().values(
        verdict_id=verdict_id,
        verified=verified,
        method=method,
        located_at=located_at,
        failure_reason=failure_reason,
    )
    res = conn.execute(stmt)
    pk = res.inserted_primary_key
    ev_id = int(pk[0]) if pk is not None else 0

    append_audit(
        conn,
        actor=actor,
        action="verify_evidence",
        table_name="evidence_verifications",
        row_id=ev_id,
        before_json=None,
        after_json={
            "id": ev_id,
            "verdict_id": verdict_id,
            "verified": verified,
            "method": method,
        },
    )
    return ev_id


def apply_evidence_downgrade(
    conn: Connection,
    verdict_id: int,
    actor: str = "agent:evidence_verifier",
) -> None:
    """Downgrade a checklist_verdicts row to 'unsupported_evidence' and audit (US-25, §7.2)."""
    stmt = (
        checklist_verdicts.update()
        .where(checklist_verdicts.c.id == verdict_id)
        .values(verdict="unsupported_evidence")
    )
    conn.execute(stmt)

    append_audit(
        conn,
        actor=actor,
        action="evidence_downgrade",
        table_name="checklist_verdicts",
        row_id=verdict_id,
        before_json={"verdict": "flag"},
        after_json={"verdict": "unsupported_evidence"},
    )


def record_skill_execution_run(
    submission_id: int,
    capability: str,
    version: str,
    run_index: int,
    model_name: str,
    model_digest: str,
    prompt_sha256: str,
    raw_output: str | None,
    parsed_output: dict[str, Any] | None,
    status: str,
    latency_ms: int,
    verdicts_data: list[dict[str, Any]],
    actor: str = "agent:harness",
) -> int:
    """Record a skill execution run, its verdicts, and evidence verifications atomically."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            exec_stmt = skill_executions.insert().values(
                submission_id=submission_id,
                skill_capability=capability,
                skill_version=version,
                run_index=run_index,
                model_name=model_name,
                model_digest=model_digest,
                prompt_sha256=prompt_sha256,
                raw_output=raw_output,
                parsed_output=parsed_output,
                status=status,
                latency_ms=latency_ms,
            )
            exec_res = conn.execute(exec_stmt)
            exec_pk = exec_res.inserted_primary_key
            execution_id = int(exec_pk[0]) if exec_pk is not None else 0

            append_audit(
                conn,
                actor=actor,
                action="create_skill_execution",
                table_name="skill_executions",
                row_id=execution_id,
                before_json=None,
                after_json={
                    "id": execution_id,
                    "submission_id": submission_id,
                    "capability": capability,
                    "run_index": run_index,
                },
            )

            for vd in verdicts_data:
                cv_stmt = checklist_verdicts.insert().values(
                    execution_id=execution_id,
                    check_id=vd["check_id"],
                    verdict=vd["verdict"],
                    severity=vd["severity"],
                    evidence_text=vd.get("evidence_text"),
                    evidence_location=vd.get("evidence_location"),
                    confidence=vd.get("confidence", 1.0),
                )
                cv_res = conn.execute(cv_stmt)
                cv_pk = cv_res.inserted_primary_key
                cv_id = int(cv_pk[0]) if cv_pk is not None else 0

                append_audit(
                    conn,
                    actor=actor,
                    action="create_checklist_verdict",
                    table_name="checklist_verdicts",
                    row_id=cv_id,
                    before_json=None,
                    after_json={
                        "id": cv_id,
                        "execution_id": execution_id,
                        "check_id": vd["check_id"],
                    },
                )

                # If this verdict carries evidence verification result
                ev_res = vd.get("verification_result")
                if ev_res is not None:
                    write_evidence_verification(
                        conn=conn,
                        verdict_id=cv_id,
                        verified=ev_res.verified,
                        method=ev_res.method,
                        located_at=ev_res.located_at,
                        failure_reason=ev_res.failure_reason,
                        actor=actor,
                    )
                    # If verification failed on a flag verdict, apply downgrade
                    if vd["verdict"] == "flag" and not ev_res.verified:
                        apply_evidence_downgrade(conn=conn, verdict_id=cv_id, actor=actor)

            return execution_id
    except Exception as exc:
        raise DatabaseError(f"Failed to record skill execution run: {exc}") from exc
