"""Operator-only enrollment/recovery; never expose this as a web endpoint."""
import argparse
from datetime import UTC, datetime
from getpass import getpass

import pyotp
from sqlalchemy import select, update

import app.models  # noqa: F401
from app.core.mfa import encrypt_secret, verified_step
from app.core.security import normalize_email
from app.db.session import SessionLocal
from app.models.account import Account, AccountSession
from app.models.audit_log import AuditLog


def main():
    parser = argparse.ArgumentParser(description="Enroll/recover an admin authenticator; revokes all existing sessions.")
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    with SessionLocal() as db:
        account = db.scalar(select(Account).where(Account.email == normalize_email(args.email), Account.role == "admin").with_for_update())
        if account is None:
            raise SystemExit("Admin account not found.")
        if account.mfa_secret_encrypted and input("Replace existing authenticator and revoke sessions? Type REPLACE: ") != "REPLACE":
            raise SystemExit("Canceled.")
        secret = pyotp.random_base32()
        encrypted = encrypt_secret(secret)
        print("Keep this enrollment secret private. Add it to your authenticator app:")
        print(pyotp.TOTP(secret).provisioning_uri(name=account.email, issuer_name="Packet Capture"))
        print("Manual setup key:", secret)
        step = verified_step(encrypted, getpass("Enter the six-digit code: ").strip(), -1)
        if step is None:
            raise SystemExit("Code was not verified; nothing changed.")
        account.mfa_secret_encrypted = encrypted
        account.mfa_last_step = step
        db.execute(update(AccountSession).where(AccountSession.account_id == account.id, AccountSession.revoked_at.is_(None)).values(revoked_at=datetime.now(UTC)))
        db.add(AuditLog(actor_account_id=account.id, action="account.mfa_enrolled", target_type="account", target_id=account.id))
        db.commit()
        print("Authenticator enrolled. Wait for the next code, then sign in at /login.")


if __name__ == "__main__":
    main()
