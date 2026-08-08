"""acts, challenges, flags, act unlocks

Revision ID: 20260807_0002
Revises: 20260807_0001
Create Date: 2026-08-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260807_0002"
down_revision: Union[str, None] = "20260807_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "acts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("act_number", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unlock_threshold_points", sa.Integer(), nullable=True),
        sa.Column("unlock_threshold_percent", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("act_number > 0", name="ck_acts_act_number_positive"),
        sa.CheckConstraint(
            "unlock_threshold_percent between 0 and 100",
            name="ck_acts_threshold_percent_range",
        ),
        sa.CheckConstraint(
            "unlock_threshold_points is null or unlock_threshold_points >= 0",
            name="ck_acts_threshold_points_non_negative",
        ),
    )
    op.create_index("ix_acts_act_number", "acts", ["act_number"], unique=True)
    op.create_index("ix_acts_slug", "acts", ["slug"], unique=True)
    op.create_index("ix_acts_sort_order", "acts", ["sort_order"], unique=True)

    op.create_table(
        "challenge_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_challenge_categories_name", "challenge_categories", ["name"], unique=True)
    op.create_index("ix_challenge_categories_slug", "challenge_categories", ["slug"], unique=True)

    op.create_table(
        "challenge_difficulties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_challenge_difficulties_name", "challenge_difficulties", ["name"], unique=True)
    op.create_index("ix_challenge_difficulties_slug", "challenge_difficulties", ["slug"], unique=True)

    op.create_table(
        "challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("act_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("difficulty_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("mission_brief", sa.Text(), nullable=False),
        sa.Column("story_context", sa.Text(), nullable=True),
        sa.Column("objectives_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_visible", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("story_fragment", sa.String(length=64), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("points >= 0", name="ck_challenges_points_non_negative"),
        sa.CheckConstraint(
            "status in ('draft', 'ready_for_review', 'published', 'archived')",
            name="ck_challenges_status",
        ),
        sa.ForeignKeyConstraint(["act_id"], ["acts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["challenge_categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["difficulty_id"], ["challenge_difficulties.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["published_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["archived_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_challenges_act_id", "challenges", ["act_id"])
    op.create_index("ix_challenges_slug", "challenges", ["slug"], unique=True)
    op.create_index("ix_challenges_act_status", "challenges", ["act_id", "status"])
    op.create_index("ix_challenges_act_sort", "challenges", ["act_id", "sort_order"])

    op.create_table(
        "challenge_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flag_hash", sa.String(length=128), nullable=False),
        sa.Column("validator_type", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("validator_type in ('exact')", name="ck_challenge_flags_validator_type"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_challenge_flags_challenge_id", "challenge_flags", ["challenge_id"])
    op.create_unique_constraint(
        "uq_challenge_flags_challenge_hash",
        "challenge_flags",
        ["challenge_id", "flag_hash"],
    )
    op.create_index(
        "ix_challenge_flags_challenge_active",
        "challenge_flags",
        ["challenge_id"],
        postgresql_where=sa.text("is_active = true"),
    )

    op.create_table(
        "act_unlocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("act_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(length=32), nullable=False),
        sa.Column("source_score", sa.Integer(), nullable=True),
        sa.Column("threshold_points", sa.Integer(), nullable=True),
        sa.Column("unlocked_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "reason in ('initial', 'score_threshold', 'admin_override')",
            name="ck_act_unlocks_reason",
        ),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["act_id"], ["acts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["unlocked_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["revoked_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_act_unlocks_team_id", "act_unlocks", ["team_id"])
    op.create_index("ix_act_unlocks_act_id", "act_unlocks", ["act_id"])
    # The arbiter for concurrent unlock creation.
    op.create_unique_constraint("uq_act_unlocks_team_act", "act_unlocks", ["team_id", "act_id"])


def downgrade() -> None:
    op.drop_constraint("uq_act_unlocks_team_act", "act_unlocks", type_="unique")
    op.drop_index("ix_act_unlocks_act_id", table_name="act_unlocks")
    op.drop_index("ix_act_unlocks_team_id", table_name="act_unlocks")
    op.drop_table("act_unlocks")

    op.drop_index("ix_challenge_flags_challenge_active", table_name="challenge_flags")
    op.drop_constraint("uq_challenge_flags_challenge_hash", "challenge_flags", type_="unique")
    op.drop_index("ix_challenge_flags_challenge_id", table_name="challenge_flags")
    op.drop_table("challenge_flags")

    op.drop_index("ix_challenges_act_sort", table_name="challenges")
    op.drop_index("ix_challenges_act_status", table_name="challenges")
    op.drop_index("ix_challenges_slug", table_name="challenges")
    op.drop_index("ix_challenges_act_id", table_name="challenges")
    op.drop_table("challenges")

    op.drop_index("ix_challenge_difficulties_slug", table_name="challenge_difficulties")
    op.drop_index("ix_challenge_difficulties_name", table_name="challenge_difficulties")
    op.drop_table("challenge_difficulties")

    op.drop_index("ix_challenge_categories_slug", table_name="challenge_categories")
    op.drop_index("ix_challenge_categories_name", table_name="challenge_categories")
    op.drop_table("challenge_categories")

    op.drop_index("ix_acts_sort_order", table_name="acts")
    op.drop_index("ix_acts_slug", table_name="acts")
    op.drop_index("ix_acts_act_number", table_name="acts")
    op.drop_table("acts")
