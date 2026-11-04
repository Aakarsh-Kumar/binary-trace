"""Initial schema with 7 tables conforming to ARCHITECTURE.md §4.

Revision ID: 0001
Revises:
Create Date: 2026-11-04 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT, TINYINT

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 4.1 submissions
    op.create_table(
        "submissions",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("external_id", sa.String(128), nullable=False),
        sa.Column(
            "submission_type",
            sa.Enum("prose", "code", "mixed", name="submission_type_enum"),
            nullable=False,
        ),
        sa.Column("source_path", sa.String(512), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column(
            "ingested_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("external_id", name="uq_external"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_type", "submissions", ["submission_type"])
    op.create_index("idx_sha", "submissions", ["content_sha256"])

    # 4.2 retrieval_events
    op.create_table(
        "retrieval_events",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column(
            "submission_id",
            BIGINT(unsigned=True),
            sa.ForeignKey("submissions.id", name="fk_re_sub"),
            nullable=False,
        ),
        sa.Column("capability_set", sa.JSON(), nullable=False),
        sa.Column("candidates", sa.JSON(), nullable=False),
        sa.Column("selected", sa.JSON(), nullable=False),
        sa.Column("token_budget", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_re_sub", "retrieval_events", ["submission_id"])

    # 4.3 skill_executions
    op.create_table(
        "skill_executions",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column(
            "submission_id",
            BIGINT(unsigned=True),
            sa.ForeignKey("submissions.id", name="fk_se_sub"),
            nullable=False,
        ),
        sa.Column("skill_capability", sa.String(64), nullable=False),
        sa.Column("skill_version", sa.String(32), nullable=False),
        sa.Column("run_index", TINYINT(unsigned=True), nullable=False),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("model_digest", sa.String(64), nullable=False),
        sa.Column("prompt_sha256", sa.String(64), nullable=False),
        sa.Column("raw_output", LONGTEXT(), nullable=True),
        sa.Column("parsed_output", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ok", "parse_error", "schema_error", "timeout", "error", name="execution_status_enum"),
            nullable=False,
        ),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "submission_id",
            "skill_capability",
            "skill_version",
            "run_index",
            name="uq_se",
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_se_skill", "skill_executions", ["submission_id", "skill_capability"])

    # 4.4 checklist_verdicts
    op.create_table(
        "checklist_verdicts",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column(
            "execution_id",
            BIGINT(unsigned=True),
            sa.ForeignKey("skill_executions.id", name="fk_cv_exec"),
            nullable=False,
        ),
        sa.Column("check_id", sa.String(64), nullable=False),
        sa.Column(
            "verdict",
            sa.Enum(
                "pass",
                "flag",
                "not_applicable",
                "unsupported_evidence",
                "execution_error",
                name="verdict_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum("low", "medium", "high", "critical", name="severity_enum"),
            nullable=False,
        ),
        sa.Column("evidence_text", sa.TEXT(), nullable=True),
        sa.Column("evidence_location", sa.String(512), nullable=True),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_cv_exec_check", "checklist_verdicts", ["execution_id", "check_id"])

    # 4.5 evidence_verifications
    op.create_table(
        "evidence_verifications",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column(
            "verdict_id",
            BIGINT(unsigned=True),
            sa.ForeignKey("checklist_verdicts.id", name="fk_ev_verdict"),
            nullable=False,
        ),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("located_at", sa.String(512), nullable=True),
        sa.Column(
            "method",
            sa.Enum("substring", "normalized", "fuzzy", "none", name="verification_method_enum"),
            nullable=False,
        ),
        sa.Column("failure_reason", sa.String(256), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_ev_verdict", "evidence_verifications", ["verdict_id"])

    # 4.6 reviewer_feedback
    op.create_table(
        "reviewer_feedback",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column(
            "submission_id",
            BIGINT(unsigned=True),
            sa.ForeignKey("submissions.id", name="fk_rf_sub"),
            nullable=False,
        ),
        sa.Column(
            "verdict_id",
            BIGINT(unsigned=True),
            sa.ForeignKey("checklist_verdicts.id", name="fk_rf_verdict"),
            nullable=True,
        ),
        sa.Column("reviewer_id", sa.String(64), nullable=False),
        sa.Column(
            "action",
            sa.Enum("approve", "override", "request_rerun", "escalate", name="reviewer_action_enum"),
            nullable=False,
        ),
        sa.Column(
            "reason_code",
            sa.Enum(
                "evidence_insufficient",
                "check_not_applicable",
                "model_misread",
                "policy_exception",
                "severity_mismatch",
                "other",
                name="reason_code_enum",
            ),
            nullable=True,
        ),
        sa.Column("comment", sa.TEXT(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_rf_sub", "reviewer_feedback", ["submission_id"])

    # 4.7 audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("actor", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("table_name", sa.String(64), nullable=False),
        sa.Column("row_id", BIGINT(unsigned=True), nullable=True),
        sa.Column("before_json", sa.JSON(), nullable=True),
        sa.Column("after_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("idx_al_table_row", "audit_log", ["table_name", "row_id"])
    op.create_index("idx_al_created", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("reviewer_feedback")
    op.drop_table("evidence_verifications")
    op.drop_table("checklist_verdicts")
    op.drop_table("skill_executions")
    op.drop_table("retrieval_events")
    op.drop_table("submissions")

