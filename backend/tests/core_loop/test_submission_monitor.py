from app.models.account import AccountRole
from tests.core_loop.factories import (
    PASSWORD,
    get_act,
    make_account,
    make_challenge,
    make_team,
    set_rate_limit,
)

FLAG = "PacketCapture{MONITOR_SECRET}"
WRONG = "PacketCapture{WRONG_SECRET}"


def _login_admin(client, db):
    admin = make_account(db, role=AccountRole.ADMIN)
    db.commit()
    response = client.post("/auth/login", json={"email": admin.email, "password": PASSWORD})
    assert response.status_code == 200, response.text


def _login_team(client, team):
    client.post("/auth/logout")
    client.cookies.clear()
    response = client.post("/auth/login", json={"email": team.email, "password": PASSWORD})
    assert response.status_code == 200, response.text


def test_admin_submission_monitor_flags_rapid_first_attempt_solve(
    db, client, seed_reference_data
):
    act = get_act(db, 1)
    challenge = make_challenge(db, act, flag=FLAG, title="Hidden Web")
    team = make_team(db, group_name="Rapid Team")
    set_rate_limit(db)

    _login_team(client, team)
    response = client.post(
        f"/challenges/{challenge.id}/submissions",
        json={"flag": FLAG},
        headers={"user-agent": "shared-browser"},
    )
    assert response.status_code == 200, response.text

    _login_admin(client, db)
    response = client.get("/admin/submission-monitor")

    assert response.status_code == 200, response.text
    row = response.json()["rows"][0]
    assert row["team_name"] == "Rapid Team"
    assert row["challenge_title"] == "Hidden Web"
    assert row["correct_attempts"] == 1
    assert row["incorrect_attempts"] == 0
    assert row["rapid_solve"] is True
    assert row["suspicious_notes"]
    assert FLAG not in response.text


def test_submission_monitor_counts_wrong_attempts_without_leaking_flags(
    db, client, seed_reference_data
):
    act = get_act(db, 1)
    challenge = make_challenge(db, act, flag=FLAG)
    team = make_team(db, group_name="Attempt Team")
    set_rate_limit(db)

    _login_team(client, team)
    assert client.post(f"/challenges/{challenge.id}/submissions", json={"flag": WRONG}).status_code == 200
    assert client.post(f"/challenges/{challenge.id}/submissions", json={"flag": FLAG}).status_code == 200

    _login_admin(client, db)
    response = client.get("/admin/submission-monitor")

    assert response.status_code == 200, response.text
    row = response.json()["rows"][0]
    assert row["correct_attempts"] == 1
    assert row["incorrect_attempts"] == 1
    assert row["rapid_solve"] is False
    assert FLAG not in response.text
    assert WRONG not in response.text


def test_participant_cannot_access_submission_monitor(db, client, seed_reference_data):
    team = make_team(db)
    _login_team(client, team)

    response = client.get("/admin/submission-monitor")

    assert response.status_code == 403
