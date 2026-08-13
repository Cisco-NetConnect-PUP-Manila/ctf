"""team solve fragments

Revision ID: 20260813_0005
Revises: 20260811_0004
Create Date: 2026-08-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260813_0005"
down_revision: Union[str, None] = "20260811_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("solves", sa.Column("team_fragment_hash", sa.String(length=128), nullable=True))
    op.add_column("solves", sa.Column("team_fragment_preview", sa.String(length=40), nullable=True))


def downgrade() -> None:
    op.drop_column("solves", "team_fragment_preview")
    op.drop_column("solves", "team_fragment_hash")
