from datetime import UTC, datetime, timedelta

from tests.conftest import (
    TEST_PASSWORD,
    create_test_account,
    create_test_team,
    seed_registration_open,
)

from app.core.security import hash_session_token, new_session_token
from app.models.account import AccountSession, AccountStatus


class TestLogin:
    def test_invalid_credentials_email_not_found(self, client, db_session):
        seed_registration_open(db_session, True)
        resp = client.post("/auth/login", json={"email": "no@test.com", "password": "whatever1234"})
        assert resp.status_code == 401
        assert resp.json()["code"] == "INVALID_CREDENTIALS"

    def test_invalid_credentials_wrong_password(self, client, db_session):
        seed_registration_open(db_session, True)
        create_test_account(db_session, email="team@test.com", password=TEST_PASSWORD)
        resp = client.post("/auth/login", json={"email": "team@test.com", "password": "wrong-password-123"})
        assert resp.status_code == 401
        assert resp.json()["code"] == "INVALID_CREDENTIALS"

    def test_account_disabled(self, client, db_session):
        seed_registration_open(db_session, True)
        create_test_account(
            db_session,
            email="disabled@test.com",
            status=AccountStatus.DISABLED.value,
        )
        resp = client.post("/auth/login", json={"email": "disabled@test.com", "password": TEST_PASSWORD})
        assert resp.status_code == 403
        assert resp.json()["code"] == "ACCOUNT_DISABLED"

    def test_success_sets_cookie_and_returns_me(self, client, db_session):
        seed_registration_open(db_session, True)
        account = create_test_account(db_session, email="team@test.com")
        create_test_team(db_session, account, group_name="Test Team")
        resp = client.post("/auth/login", json={"email": "team@test.com", "password": TEST_PASSWORD})
        assert resp.status_code == 200
        data = resp.json()
        assert data["account"]["email"] == "team@test.com"
        assert data["account"]["role"] == "participant"
        assert data["team"]["group_name"] == "Test Team"
        assert "packet_capture_session" in resp.cookies


class TestSession:
    def test_me_returns_account_when_authenticated(self, client, db_session):
        seed_registration_open(db_session, True)
        account = create_test_account(db_session, email="team@test.com")
        create_test_team(db_session, account, group_name="Test Team")
        login_resp = client.post("/auth/login", json={"email": "team@test.com", "password": TEST_PASSWORD})
        cookies = login_resp.cookies

        resp = client.get("/auth/me", cookies=cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["account"]["email"] == "team@test.com"
        assert data["team"]["group_name"] == "Test Team"

    def test_me_returns_auth_required_without_cookie(self, client, db_session):
        resp = client.get("/auth/me")
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    def test_me_returns_session_expired(self, client, db_session):
        account = create_test_account(db_session, email="team@test.com")
        create_test_team(db_session, account)

        token = new_session_token()
        expired_session = AccountSession(
            account_id=account.id,
            token_hash=hash_session_token(token),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        db_session.add(expired_session)
        db_session.flush()

        resp = client.get("/auth/me", cookies={"packet_capture_session": token})
        assert resp.status_code == 401
        assert resp.json()["code"] == "SESSION_EXPIRED"

    def test_logout_then_me_returns_auth_required(self, client, db_session):
        seed_registration_open(db_session, True)
        account = create_test_account(db_session, email="team@test.com")
        create_test_team(db_session, account)
        login_resp = client.post("/auth/login", json={"email": "team@test.com", "password": TEST_PASSWORD})
        cookies = login_resp.cookies

        logout_resp = client.post("/auth/logout", cookies=cookies)
        assert logout_resp.status_code == 204

        me_resp = client.get("/auth/me", cookies=cookies)
        assert me_resp.status_code == 401
        assert me_resp.json()["code"] == "AUTH_REQUIRED"

    def test_logout_clears_cookie(self, client, db_session):
        seed_registration_open(db_session, True)
        account = create_test_account(db_session, email="team@test.com")
        create_test_team(db_session, account)
        login_resp = client.post("/auth/login", json={"email": "team@test.com", "password": TEST_PASSWORD})

        logout_resp = client.post("/auth/logout", cookies=login_resp.cookies)
        assert logout_resp.status_code == 204
        assert "packet_capture_session" in logout_resp.cookies
        assert logout_resp.cookies["packet_capture_session"] == '""'
