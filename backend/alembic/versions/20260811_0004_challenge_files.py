"""challenge files

Revision ID: 20260811_0004
Revises: 20260808_0003
Create Date: 2026-08-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260811_0004"
down_revision: Union[str, None] = "20260808_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "challenge_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("challenge_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_provider", sa.String(length=40), nullable=False, server_default="local"),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("extension", sa.String(length=16), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_by_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("storage_provider in ('local')", name="ck_challenge_files_provider"),
        sa.CheckConstraint(
            "extension in ('.raw', '.pcap', '.dd', '.png', '.txt', '.pkz', '.pka')",
            name="ck_challenge_files_extension",
        ),
        sa.CheckConstraint("size_bytes between 0 and 104857600", name="ck_challenge_files_size"),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_account_id"], ["accounts.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_challenge_files_challenge_id", "challenge_files", ["challenge_id"])
    op.create_index("ix_challenge_files_storage_key", "challenge_files", ["storage_key"], unique=True)
    op.create_index(
        "ix_challenge_files_challenge_active",
        "challenge_files",
        ["challenge_id"],
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.drop_index("ix_challenge_files_challenge_active", table_name="challenge_files")
    op.drop_index("ix_challenge_files_storage_key", table_name="challenge_files")
    op.drop_index("ix_challenge_files_challenge_id", table_name="challenge_files")
    op.drop_table("challenge_files")
