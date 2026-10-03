from sqlalchemy import select

from app.core.security import verify_password
from app.models.account import Account


def assert_admin_passwords_safe(db):
    for account in db.scalars(select(Account).where(Account.role == 'admin', Account.status == 'active')):
        if verify_password('AdminPassword123!', account.password_hash):
            raise RuntimeError('An active admin still uses the shipped development password. Rotate it before production startup.')
