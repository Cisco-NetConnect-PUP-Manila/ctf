from tests.conftest import TEST_PASSWORD, create_test_account, create_test_team

from app.models.account import AccountRole
from app.models.audit_log import AuditLog
from app.models.team import TeamStatus


def _login_admin(client, db_session):
    create_test_account(db_session, email="team-admin@test.com", role=AccountRole.ADMIN.value)
    response = client.post(
        "/auth/login",
        json={"email": "team-admin@test.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    return response.cookies


def test_admin_lists_registered_teams(client, db_session):
    account = create_test_account(db_session, email="pending-team@test.com")
    create_test_team(
        db_session,
        account,
        group_name="Pending Team",
        team_status=TeamStatus.PENDING.value,
    )
    cookies = _login_admin(client, db_session)

    response = client.get("/admin/teams", cookies=cookies)

    assert response.status_code == 200
    body = response.json()
    assert body[0]["group_name"] == "Pending Team"
    assert body[0]["status"] == "pending"
    assert body[0]["email"] == "pending-team@test.com"
    assert body[0]["member_count"] == 1


def test_admin_approves_pending_team(client, db_session):
    account = create_test_account(db_session, email="approve-team@test.com")
    team = create_test_team(
        db_session,
        account,
        group_name="Approve Team",
        team_status=TeamStatus.PENDING.value,
    )
    cookies = _login_admin(client, db_session)

    response = client.patch(f"/admin/teams/{team.id}/approve", cookies=cookies)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["approved_at"] is not None
    assert db_session.query(AuditLog).filter_by(action="team.approved").count() == 1


def test_admin_rejects_pending_team_with_reason(client, db_session):
    account = create_test_account(db_session, email="reject-team@test.com")
    team = create_test_team(
        db_session,
        account,
        group_name="Reject Team",
        team_status=TeamStatus.PENDING.value,
    )
    cookies = _login_admin(client, db_session)

    response = client.patch(
        f"/admin/teams/{team.id}/reject",
        json={"reason": "Incomplete member details."},
        cookies=cookies,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["rejection_reason"] == "Incomplete member details."


def test_participant_cannot_access_team_management(client, db_session):
    create_test_account(db_session, email="not-admin@test.com")
    login = client.post(
        "/auth/login",
        json={"email": "not-admin@test.com", "password": TEST_PASSWORD},
    )

    response = client.get("/admin/teams", cookies=login.cookies)

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
