"""Persistent login attempt limits shared across replicas."""
import sqlalchemy as sa
from alembic import op

revision = "20261004_0008"
down_revision = "20261003_0007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_throttles",
        sa.Column("key", sa.String(80), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("blocked_until", sa.DateTime(timezone=True)),
    )


def downgrade():
    op.drop_table("auth_throttles")
