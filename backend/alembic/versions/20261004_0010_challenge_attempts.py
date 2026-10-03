"""Optional per-team challenge attempt budget."""
from alembic import op
import sqlalchemy as sa

revision = "20261004_0010"
down_revision = "20261004_0009"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('challenges', sa.Column('max_attempts', sa.Integer(), nullable=True))
    op.create_check_constraint('ck_challenges_max_attempts_positive', 'challenges', 'max_attempts IS NULL OR max_attempts >= 1')


def downgrade():
    op.drop_constraint('ck_challenges_max_attempts_positive', 'challenges', type_='check')
    op.drop_column('challenges', 'max_attempts')
