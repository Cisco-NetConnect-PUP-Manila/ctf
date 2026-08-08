from datetime import UTC, datetime, timedelta

from tests.conftest import TEST_PASSWORD, create_test_account

from app.core.security import hash_session_token, new_session_token
from app.models.account import AccountRole, AccountSession, AccountStatus


class TestAdminRBAC:
    def test_admin_can_access_acts(self, client, db_session):
        account = create_test_account(
            db_session, email="admin@test.com", role=AccountRole.ADMIN.value
        )
        login_resp = client.post(
            "/auth/login", json={"email": "admin@test.com", "password": TEST_PASSWORD}
        )
        resp = client.get("/admin/acts", cookies=login_resp.cookies)
        assert resp.status_code == 200

    def test_admin_can_access_challenge_categories(self, client, db_session):
        account = create_test_account(
            db_session, email="admin@test.com", role=AccountRole.ADMIN.value
        )
        login_resp = client.post(
            "/auth/login", json={"email": "admin@test.com", "password": TEST_PASSWORD}
        )
        resp = client.get("/admin/challenge-categories", cookies=login_resp.cookies)
        assert resp.status_code == 200

    def test_participant_denied_acts(self, client, db_session):
        account = create_test_account(db_session, email="user@test.com")
        login_resp = client.post(
            "/auth/login", json={"email": "user@test.com", "password": TEST_PASSWORD}
        )
        resp = client.get("/admin/acts", cookies=login_resp.cookies)
        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"

    def test_participant_denied_challenge_categories(self, client, db_session):
        account = create_test_account(db_session, email="user@test.com")
        login_resp = client.post(
            "/auth/login", json={"email": "user@test.com", "password": TEST_PASSWORD}
        )
        resp = client.get("/admin/challenge-categories", cookies=login_resp.cookies)
        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"

    def test_unauthenticated_denied_acts(self, client, db_session):
        resp = client.get("/admin/acts")
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    def test_unauthenticated_denied_challenge_categories(self, client, db_session):
        resp = client.get("/admin/challenge-categories")
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    def test_disabled_admin_denied(self, client, db_session):
        account = create_test_account(
            db_session,
            email="disabled@test.com",
            role=AccountRole.ADMIN.value,
            status=AccountStatus.DISABLED.value,
        )
        token = new_session_token()
        session = AccountSession(
            account_id=account.id,
            token_hash=hash_session_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        db_session.add(session)
        db_session.flush()

        resp = client.get("/admin/acts", cookies={"packet_capture_session": token})
        assert resp.status_code == 403
        assert resp.json()["code"] == "ACCOUNT_DISABLED"
