"""intel requests and hint penalties

Revision ID: 20260817_0006
Revises: 20260813_0005
Create Date: 2026-08-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260817_0006"
down_revision: Union[str, None] = "20260813_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hints",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("penalty_points", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("penalty_points >= 0", name="ck_hints_penalty_non_negative"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hints_challenge_id", "hints", ["challenge_id"])
    op.create_index("ix_hints_challenge_sort", "hints", ["challenge_id", "sort_order"])

    op.create_table(
        "intel_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("penalty_points", sa.Integer(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("penalty_points >= 0", name="ck_intel_requests_penalty_non_negative"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hint_id"], ["hints.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "hint_id", name="uq_intel_requests_team_hint"),
    )
    op.create_index("ix_intel_requests_team_id", "intel_requests", ["team_id"])
    op.create_index("ix_intel_requests_challenge_id", "intel_requests", ["challenge_id"])
    op.create_index("ix_intel_requests_hint_id", "intel_requests", ["hint_id"])
    op.create_index(
        "ix_intel_requests_team_challenge", "intel_requests", ["team_id", "challenge_id"]
    )


def downgrade() -> None:
    op.drop_table("intel_requests")
    op.drop_table("hints")
