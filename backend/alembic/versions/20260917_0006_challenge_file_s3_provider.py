"""Allow S3 challenge file storage provider.

Revision ID: 20260917_0006
Revises: 20260813_0005
Create Date: 2026-09-17
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260917_0006"
down_revision: str | None = "20260813_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_challenge_files_provider", "challenge_files", type_="check")
    op.create_check_constraint(
        "ck_challenge_files_provider",
        "challenge_files",
        "storage_provider in ('local', 's3')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_challenge_files_provider", "challenge_files", type_="check")
    op.create_check_constraint(
        "ck_challenge_files_provider",
        "challenge_files",
        "storage_provider in ('local')",
    )
