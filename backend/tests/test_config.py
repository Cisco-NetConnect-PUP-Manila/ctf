import pytest
from cryptography.fernet import Fernet

from app.core.config import Settings


def _production_settings(**overrides):
    values = {
        "BACKEND_ENV": "production",
        "DATABASE_URL": "postgresql+psycopg://user:pass@db.internal:5432/packet_capture_ctf",
        "FRONTEND_ORIGIN": "https://packetcapture.xyz",
        "SESSION_COOKIE_SECURE": True,
        "FLAG_HASH_SECRET": "prod-flag-secret-with-enough-entropy",
        "TEAM_FRAGMENT_SECRET": "prod-team-fragment-secret-with-enough-entropy",
        "CHALLENGE_FILE_STORAGE_PROVIDER": "local",
        "EMAIL_PROVIDER": "none",
        "ADMIN_MFA_REQUIRED": True,
        "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.fixture(autouse=True)
def no_development_credentials(monkeypatch):
    monkeypatch.delenv("DEV_ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("DEV_ADMIN_PASSWORD", raising=False)


def test_production_requires_valid_key_when_mfa_is_enabled():
    for overrides in ({"MFA_ENCRYPTION_KEY": ""}, {"MFA_ENCRYPTION_KEY": "invalid"}):
        with pytest.raises(RuntimeError, match="MFA"):
            _production_settings(**overrides).assert_production_ready()


def test_production_allows_mfa_to_be_deferred():
    _production_settings(ADMIN_MFA_REQUIRED=False, MFA_ENCRYPTION_KEY="").assert_production_ready()


def test_production_rejects_shipped_credentials(monkeypatch):
    monkeypatch.setenv("DEV_ADMIN_PASSWORD", "AdminPassword123!")
    with pytest.raises(RuntimeError, match="DEV_ADMIN"):
        _production_settings().assert_production_ready()


def test_production_settings_accept_secure_baseline():
    _production_settings().assert_production_ready()


def test_production_settings_reject_local_database():
    settings = _production_settings(
        DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/packet_capture_ctf"
    )

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        settings.assert_production_ready()


def test_production_settings_reject_insecure_cookie():
    settings = _production_settings(SESSION_COOKIE_SECURE=False)

    with pytest.raises(RuntimeError, match="SESSION_COOKIE_SECURE"):
        settings.assert_production_ready()


def test_production_settings_require_s3_bucket_when_s3_enabled():
    settings = _production_settings(CHALLENGE_FILE_STORAGE_PROVIDER="s3")

    with pytest.raises(RuntimeError, match="CHALLENGE_FILE_S3_BUCKET"):
        settings.assert_production_ready()


def test_production_settings_require_email_sender_and_provider_key():
    missing_sender = _production_settings(EMAIL_PROVIDER="resend", RESEND_API_KEY="resend-key")
    with pytest.raises(RuntimeError, match="EMAIL_FROM"):
        missing_sender.assert_production_ready()

    missing_key = _production_settings(EMAIL_PROVIDER="sendgrid", EMAIL_FROM="Packet Capture <noreply@example.com>")
    with pytest.raises(RuntimeError, match="SENDGRID_API_KEY"):
        missing_key.assert_production_ready()
