"""Create (or promote) an admin account for local development.

Usage (from ``backend/`` with the venv active):

    python -m app.scripts.create_admin --email admin@example.com --password "a-strong-pass"

If an account with the email already exists it is promoted to ``admin`` and reactivated,
and its password is reset to the supplied value. Intended for local/dev use only.

``app.db.seed`` seeds platform settings and reference data but does not create an admin;
this script fills that gap so admin-only endpoints can be exercised locally.
"""

import argparse
import sys

from sqlalchemy import select

# Import the models package so SQLAlchemy resolves cross-model relationships (e.g.
# Account.team -> Team) before any query runs.
import app.models  # noqa: F401
from app.core.security import hash_password, normalize_email
from app.db.session import SessionLocal
from app.models.account import Account, AccountRole, AccountStatus


def create_admin(email: str, password: str) -> None:
    if len(password) < 12:
        sys.exit("Password must be at least 12 characters.")

    normalized = normalize_email(email)
    with SessionLocal() as db:
        account = db.scalar(select(Account).where(Account.email == normalized))
        if account is None:
            account = Account(
                email=normalized,
                password_hash=hash_password(password),
                role=AccountRole.ADMIN.value,
                status=AccountStatus.ACTIVE.value,
            )
            db.add(account)
            action = "Created"
        else:
            account.password_hash = hash_password(password)
            account.role = AccountRole.ADMIN.value
            account.status = AccountStatus.ACTIVE.value
            action = "Updated"
        db.commit()
        print(f"{action} admin account: {normalized}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote a local admin account.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    create_admin(args.email, args.password)


if __name__ == "__main__":
    main()
