"""Add an explicit solo/team participant type."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261003_0007"
down_revision: str | None = "20260917_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "teams",
        sa.Column(
            "participant_type",
            sa.String(length=16),
            nullable=False,
            server_default="team",
        ),
    )
    op.alter_column("teams", "participant_type", server_default=None)
    op.create_check_constraint(
        "ck_teams_participant_type",
        "teams",
        "participant_type in ('solo', 'team')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_teams_participant_type", "teams", type_="check")
    op.drop_column("teams", "participant_type")
