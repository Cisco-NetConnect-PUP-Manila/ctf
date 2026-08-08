"""announcements

Revision ID: 20260808_0003
Revises: 20260807_0002
Create Date: 2026-08-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260808_0003"
down_revision: Union[str, None] = "20260807_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("created_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status in ('draft', 'published', 'archived')",
            name="ck_announcements_status",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_account_id"], ["accounts.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_announcements_status_published_at",
        "announcements",
        ["status", "published_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_announcements_status_published_at", table_name="announcements")
    op.drop_table("announcements")
