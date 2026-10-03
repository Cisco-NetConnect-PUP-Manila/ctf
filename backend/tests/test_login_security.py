from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from starlette.requests import Request

from app.core.config import settings
from app.models.auth_throttle import AuthThrottle
from app.models.audit_log import AuditLog
from app.services.login_security import client_address
from tests.conftest import create_test_account, TEST_PASSWORD


def test_account_cooldown_and_success_reset(client, db_session):
    create_test_account(db_session)
    for _ in range(5):
        assert client.post('/auth/login', json={'email': 'team@example.com', 'password': 'wrong'}).status_code == 401
    denied = client.post('/auth/login', json={'email': 'team@example.com', 'password': TEST_PASSWORD})
    assert denied.status_code == 429
    assert 0 < int(denied.headers['Retry-After']) <= 30
    bucket = db_session.scalar(select(AuthThrottle).where(AuthThrottle.key.like('account:%')))
    blocked_until = bucket.blocked_until
    client.post('/auth/login', json={'email': 'team@example.com', 'password': 'wrong'})
    db_session.refresh(bucket)
    assert bucket.blocked_until == blocked_until
    bucket.blocked_until = datetime.now(UTC) - timedelta(seconds=1)
    db_session.commit()
    assert client.post('/auth/login', json={'email': 'team@example.com', 'password': TEST_PASSWORD}).status_code == 200
    assert bucket.count == 0
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == 'account.login_throttled'))


def test_unknown_accounts_are_limited_too(client):
    for _ in range(5):
        assert client.post('/auth/login', json={'email': 'missing@example.com', 'password': 'wrong'}).status_code == 401
    assert client.post('/auth/login', json={'email': 'missing@example.com', 'password': 'wrong'}).status_code == 429


def test_ip_budget_spans_accounts(client, monkeypatch):
    monkeypatch.setattr(settings, 'login_ip_limit', 10)
    for index in range(10):
        assert client.post('/auth/login', json={'email': f'unknown{index}@example.com', 'password': 'wrong'}).status_code == 401
    assert client.post('/auth/login', json={'email': 'other@example.com', 'password': 'wrong'}).status_code == 429


def test_forwarded_ip_requires_trusted_peer(monkeypatch):
    request = Request({'type': 'http', 'client': ('10.0.0.2', 123), 'headers': [(b'x-forwarded-for', b'1.2.3.4, 5.6.7.8')]})
    monkeypatch.setattr(settings, 'trusted_proxy_cidrs', '')
    assert client_address(request) == '10.0.0.2'
    monkeypatch.setattr(settings, 'trusted_proxy_cidrs', '10.0.0.2/32')
    assert client_address(request) == '5.6.7.8'
