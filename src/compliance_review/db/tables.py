"""SQLAlchemy Core Table definitions conforming to ARCHITECTURE.md §4.

Core objects ONLY: Table, Column, MetaData, types.
No ORM mappings (declarative_base, mapped_column, etc.) allowed per ARCHITECTURE.md §2.2.
"""

from sqlalchemy import (
    JSON,
    TEXT,
    TIMESTAMP,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT, TINYINT

metadata = MetaData()

# 4.1 submissions
submissions = Table(
    "submissions",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column("external_id", String(128), nullable=False),
    Column(
        "submission_type",
        Enum("prose", "code", "mixed", name="submission_type_enum"),
        nullable=False,
    ),
    Column("source_path", String(512), nullable=False),
    Column("content_sha256", String(64), nullable=False),
    Column(
        "ingested_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    UniqueConstraint("external_id", name="uq_external"),
    Index("idx_type", "submission_type"),
    Index("idx_sha", "content_sha256"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

# 4.2 retrieval_events
retrieval_events = Table(
    "retrieval_events",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column(
        "submission_id",
        BIGINT(unsigned=True),
        ForeignKey("submissions.id", name="fk_re_sub"),
        nullable=False,
    ),
    Column("capability_set", JSON, nullable=False),
    Column("candidates", JSON, nullable=False),
    Column("selected", JSON, nullable=False),
    Column("token_budget", Integer, nullable=False),
    Column("latency_ms", Integer, nullable=False),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("idx_re_sub", "submission_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

# 4.3 skill_executions
skill_executions = Table(
    "skill_executions",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column(
        "submission_id",
        BIGINT(unsigned=True),
        ForeignKey("submissions.id", name="fk_se_sub"),
        nullable=False,
    ),
    Column("skill_capability", String(64), nullable=False),
    Column("skill_version", String(32), nullable=False),
    Column("run_index", TINYINT(unsigned=True), nullable=False),
    Column("model_name", String(128), nullable=False),
    Column("model_digest", String(64), nullable=False),
    Column("prompt_sha256", String(64), nullable=False),
    Column("raw_output", LONGTEXT, nullable=True),
    Column("parsed_output", JSON, nullable=True),
    Column(
        "status",
        Enum("ok", "parse_error", "schema_error", "timeout", "error", name="execution_status_enum"),
        nullable=False,
    ),
    Column("latency_ms", Integer, nullable=False),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    UniqueConstraint(
        "submission_id",
        "skill_capability",
        "skill_version",
        "run_index",
        name="uq_se",
    ),
    Index("idx_se_skill", "submission_id", "skill_capability"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

# 4.4 checklist_verdicts
checklist_verdicts = Table(
    "checklist_verdicts",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column(
        "execution_id",
        BIGINT(unsigned=True),
        ForeignKey("skill_executions.id", name="fk_cv_exec"),
        nullable=False,
    ),
    Column("check_id", String(64), nullable=False),
    Column(
        "verdict",
        Enum(
            "pass",
            "flag",
            "not_applicable",
            "unsupported_evidence",
            "execution_error",
            name="verdict_enum",
        ),
        nullable=False,
    ),
    Column(
        "severity",
        Enum("low", "medium", "high", "critical", name="severity_enum"),
        nullable=False,
    ),
    Column("evidence_text", TEXT, nullable=True),
    Column("evidence_location", String(512), nullable=True),
    Column("confidence", Numeric(3, 2), nullable=True),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("idx_cv_exec_check", "execution_id", "check_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

# 4.5 evidence_verifications
evidence_verifications = Table(
    "evidence_verifications",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column(
        "verdict_id",
        BIGINT(unsigned=True),
        ForeignKey("checklist_verdicts.id", name="fk_ev_verdict"),
        nullable=False,
    ),
    Column("verified", Boolean, nullable=False),
    Column("located_at", String(512), nullable=True),
    Column(
        "method",
        Enum("substring", "normalized", "fuzzy", "none", name="verification_method_enum"),
        nullable=False,
    ),
    Column("failure_reason", String(256), nullable=True),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("idx_ev_verdict", "verdict_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

# 4.6 reviewer_feedback
reviewer_feedback = Table(
    "reviewer_feedback",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column(
        "submission_id",
        BIGINT(unsigned=True),
        ForeignKey("submissions.id", name="fk_rf_sub"),
        nullable=False,
    ),
    Column(
        "verdict_id",
        BIGINT(unsigned=True),
        ForeignKey("checklist_verdicts.id", name="fk_rf_verdict"),
        nullable=True,
    ),
    Column("reviewer_id", String(64), nullable=False),
    Column(
        "action",
        Enum("approve", "override", "request_rerun", "escalate", name="reviewer_action_enum"),
        nullable=False,
    ),
    Column(
        "reason_code",
        Enum(
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
    Column("comment", TEXT, nullable=True),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("idx_rf_sub", "submission_id"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

# 4.7 audit_log (append-only, enforced by GRANT)
audit_log = Table(
    "audit_log",
    metadata,
    Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    Column("actor", String(64), nullable=False),
    Column("action", String(64), nullable=False),
    Column("table_name", String(64), nullable=False),
    Column("row_id", BIGINT(unsigned=True), nullable=True),
    Column("before_json", JSON, nullable=True),
    Column("after_json", JSON, nullable=True),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("idx_al_table_row", "table_name", "row_id"),
    Index("idx_al_created", "created_at"),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)
