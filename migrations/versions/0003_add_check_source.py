"""Add check_source column to checklist_verdicts with default and backfill (US-20, D-019).

Revision ID: 0003
Revises: 0001
Create Date: 2026-11-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DETERMINISTIC_CHECKS = (
    "cite-doi-resolvable",
    "cite-not-retracted",
    "cite-no-duplicates",
    "code-ruff-clean",
    "code-file-loc-limit",
    "code-pylint-clean",
    "rai-section-present",
    "rai-tool-named",
    "rai-task-named",
    "struct-required-sections",
    "struct-heading-order",
    "struct-minimum-length",
)


def upgrade() -> None:
    check_source_enum = sa.Enum("deterministic", "model", name="check_source_enum")
    op.add_column(
        "checklist_verdicts",
        sa.Column(
            "check_source",
            check_source_enum,
            nullable=False,
            server_default="model",
        ),
    )

    # Backfill deterministic checks
    checks_list = ", ".join(f"'{c}'" for c in DETERMINISTIC_CHECKS)
    stmt = (
        "UPDATE checklist_verdicts SET check_source = 'deterministic' "
        f"WHERE check_id IN ({checks_list})"
    )
    op.execute(stmt)


def downgrade() -> None:
    op.drop_column("checklist_verdicts", "check_source")
