"""submissions and solves

Revision ID: 20260807_0003
Revises: 20260807_0002
Create Date: 2026-08-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260807_0003"
down_revision: Union[str, None] = "20260807_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submitted_value_hash", sa.String(length=64), nullable=False),
        sa.Column("submitted_value_preview", sa.String(length=32), nullable=True),
        sa.Column("is_correct", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("ip_address_hash", sa.String(length=64), nullable=True),
        sa.Column("user_agent_hash", sa.String(length=64), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="RESTRICT"),
    )
    op.create_index(
        "ix_submissions_team_submitted_at",
        "submissions",
        ["team_id", "submitted_at"],
    )
    op.create_index(
        "ix_submissions_team_challenge_time",
        "submissions",
        ["team_id", "challenge_id", "submitted_at"],
    )
    op.create_index(
        "ix_submissions_challenge_submitted_at",
        "submissions",
        ["challenge_id", "submitted_at"],
    )

    op.create_table(
        "solves",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column("solved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("points_awarded >= 0", name="ck_solves_points_non_negative"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="RESTRICT"),
        # RESTRICT is load-bearing: it blocks hard-deleting a solved challenge.
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_solves_team_id", "solves", ["team_id"])
    op.create_index("ix_solves_challenge_id", "solves", ["challenge_id"])
    op.create_index("ix_solves_submission_id", "solves", ["submission_id"], unique=True)
    op.create_index("ix_solves_team_solved_at", "solves", ["team_id", "solved_at"])
    # The arbiter that makes concurrent correct submissions award points exactly once.
    op.create_unique_constraint("uq_solves_team_challenge", "solves", ["team_id", "challenge_id"])


def downgrade() -> None:
    op.drop_constraint("uq_solves_team_challenge", "solves", type_="unique")
    op.drop_index("ix_solves_team_solved_at", table_name="solves")
    op.drop_index("ix_solves_submission_id", table_name="solves")
    op.drop_index("ix_solves_challenge_id", table_name="solves")
    op.drop_index("ix_solves_team_id", table_name="solves")
    op.drop_table("solves")

    op.drop_index("ix_submissions_challenge_submitted_at", table_name="submissions")
    op.drop_index("ix_submissions_team_challenge_time", table_name="submissions")
    op.drop_index("ix_submissions_team_submitted_at", table_name="submissions")
    op.drop_table("submissions")
