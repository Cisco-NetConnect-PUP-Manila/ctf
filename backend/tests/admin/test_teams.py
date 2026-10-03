import io

from tests.conftest import TEST_PASSWORD, create_test_account, create_test_team

from app.models.account import Account, AccountRole
from app.models.audit_log import AuditLog
from app.models.team import Team, TeamStatus


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


def test_admin_can_create_pending_solo_participant_while_public_intake_is_closed(
    client, db_session, monkeypatch
):
    sent_messages = []
    monkeypatch.setattr("app.api.routes.admin_teams.send_email_best_effort", sent_messages.append)
    cookies = _login_admin(client, db_session)

    response = client.post(
        "/admin/teams",
        json={
            "participant_type": "solo",
            "group_name": "Solo Analyst",
            "email": "solo-admin@test.com",
            "password": TEST_PASSWORD,
            "members": [{"full_name": "Solo Analyst", "email": "solo-admin@test.com"}],
        },
        cookies=cookies,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["participant_type"] == "solo"
    assert body["status"] == "pending"
    assert body["member_count"] == 1
    assert db_session.query(AuditLog).filter_by(action="participant.created").count() == 1
    assert len(sent_messages) == 1


def test_admin_csv_import_is_atomic_and_supports_solo_and_team(client, db_session, monkeypatch):
    sent_messages = []
    monkeypatch.setattr("app.api.routes.admin_teams.send_email_best_effort", sent_messages.append)
    cookies = _login_admin(client, db_session)
    csv_content = """participant_type,group_name,email,password,member_1_name,member_1_email,member_2_name,member_2_email,member_3_name,member_3_email,member_4_name,member_4_email,member_5_name,member_5_email
team,Imported Team,imported-team@test.com,test-password-1234,Leader,imported-team@test.com,Two,two-import@test.com,Three,three-import@test.com,Four,four-import@test.com,,
solo,Imported Solo,imported-solo@test.com,test-password-1234,Imported Solo,imported-solo@test.com,,,,,,,,
"""

    response = client.post(
        "/admin/teams/import",
        files={"file": ("participants.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        cookies=cookies,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created_count"] == 2
    assert {item["participant_type"] for item in body["participants"]} == {"solo", "team"}
    assert db_session.query(Team).count() == 2
    assert db_session.query(Account).count() == 3
    assert len(sent_messages) == 2


def test_admin_csv_import_rejects_invalid_rows_without_partial_records(client, db_session):
    cookies = _login_admin(client, db_session)
    csv_content = """participant_type,group_name,email,password,member_1_name,member_1_email
team,Broken Team,broken@test.com,short,Leader,broken@test.com
"""

    response = client.post(
        "/admin/teams/import",
        files={"file": ("participants.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        cookies=cookies,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert db_session.query(Team).count() == 0


def test_admin_approves_pending_team(client, db_session, monkeypatch):
    sent_messages = []
    monkeypatch.setattr("app.api.routes.admin_teams.send_email_best_effort", sent_messages.append)

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
    assert len(sent_messages) == 1
    assert sent_messages[0].to == "approve-team@test.com"
    assert "approved" in sent_messages[0].subject.lower()


def test_admin_rejects_pending_team_with_reason(client, db_session, monkeypatch):
    sent_messages = []
    monkeypatch.setattr("app.api.routes.admin_teams.send_email_best_effort", sent_messages.append)

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
    assert len(sent_messages) == 1
    assert sent_messages[0].to == "reject-team@test.com"
    assert "update" in sent_messages[0].subject.lower()


def test_participant_cannot_access_team_management(client, db_session):
    create_test_account(db_session, email="not-admin@test.com")
    login = client.post(
        "/auth/login",
        json={"email": "not-admin@test.com", "password": TEST_PASSWORD},
    )

    response = client.get("/admin/teams", cookies=login.cookies)

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_admin_deletes_pending_registration_and_account(client, db_session):
    from app.models.account import Account
    from app.models.team import Team

    account = create_test_account(db_session, email="delete-registration@test.com")
    team = create_test_team(
        db_session,
        account,
        group_name="Delete Registration",
        team_status=TeamStatus.PENDING.value,
    )
    cookies = _login_admin(client, db_session)

    response = client.delete(f"/admin/teams/{team.id}", cookies=cookies)

    assert response.status_code == 204
    assert db_session.get(Team, team.id) is None
    assert db_session.get(Account, account.id) is None


def test_admin_cannot_delete_approved_registration(client, db_session):
    account = create_test_account(db_session, email="keep-approved@test.com")
    team = create_test_team(
        db_session,
        account,
        group_name="Keep Approved",
        team_status=TeamStatus.APPROVED.value,
    )
    cookies = _login_admin(client, db_session)

    response = client.delete(f"/admin/teams/{team.id}", cookies=cookies)

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
