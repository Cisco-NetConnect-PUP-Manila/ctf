from datetime import UTC, datetime, timedelta

import pyotp
from sqlalchemy import select

from app.core.config import settings
from app.core.mfa import encrypt_secret
from app.core.security import hash_session_token
from app.models.account import AccountSession
from tests.conftest import create_test_account, TEST_PASSWORD


def test_admin_requires_code_and_rejects_replay(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, 'admin_mfa_required', True)
    account = create_test_account(db_session, role='admin')
    credentials = {'email': account.email, 'password': TEST_PASSWORD}
    assert client.post('/auth/login', json=credentials).json()['code'] == 'MFA_SETUP_REQUIRED'
    secret = pyotp.random_base32()
    account.mfa_secret_encrypted = encrypt_secret(secret)
    db_session.commit()
    assert client.post('/auth/login', json=credentials).json()['code'] == 'MFA_REQUIRED'
    assert db_session.scalar(select(AccountSession)) is None
    code = pyotp.TOTP(secret).now()
    assert client.post('/auth/login', json={**credentials, 'mfa_code': code}).status_code == 200
    assert client.get('/auth/me').status_code == 200
    assert client.post('/auth/login', json={**credentials, 'mfa_code': code}).json()['code'] == 'MFA_INVALID'


def test_password_only_admin_session_is_revoked(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, 'admin_mfa_required', True)
    account = create_test_account(db_session, role='admin')
    session = AccountSession(account_id=account.id, token_hash=hash_session_token('old-token'), expires_at=datetime.now(UTC) + timedelta(hours=1))
    db_session.add(session)
    db_session.commit()
    client.cookies.set(settings.session_cookie_name, 'old-token')
    assert client.get('/auth/me').status_code == 401
    assert session.revoked_at is not None
