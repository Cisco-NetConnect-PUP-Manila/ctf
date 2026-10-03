"""Encrypted admin authenticator secrets and verified sessions."""
from alembic import op
import sqlalchemy as sa

revision = "20261004_0009"
down_revision = "20261004_0008"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("accounts", sa.Column("mfa_secret_encrypted", sa.String(512)))
    op.add_column("accounts", sa.Column("mfa_last_step", sa.BigInteger(), nullable=False, server_default="-1"))
    op.add_column("account_sessions", sa.Column("mfa_verified", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column("account_sessions", "mfa_verified")
    op.drop_column("accounts", "mfa_last_step")
    op.drop_column("accounts", "mfa_secret_encrypted")
