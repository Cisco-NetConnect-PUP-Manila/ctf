"""End-to-end milestone from handoff section 17, driven through HTTP.

register -> log in -> admin creates and publishes a challenge -> participant sees it ->
wrong flag -> right flag -> score awarded once -> duplicate awards zero -> threshold
reached -> Act II unlocks -> leaderboard-facing score updates.

Also the security sweep: no participant-facing response may contain flag material.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.account import AccountRole
from app.services import scoring
from tests.factories import PASSWORD, get_act, make_account, make_team, set_rate_limit

ACT1_FLAG = "PacketCapture{PHANTOM_TRACE}"
ACT1_FLAG_2 = "PacketCapture{LEAKED_REPOSITORY}"
ACT2_FLAG = "PacketCapture{AUTH_BYPASS}"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_client(db, seed_reference_data, client):
    admin = make_account(db, role=AccountRole.ADMIN)
    db.commit()
    response = client.post("/auth/login", json={"email": admin.email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return client


def _create_published_challenge(client, act_id, title, slug, points, flag):
    response = client.post(
        "/admin/challenges",
        json={
            "act_id": str(act_id),
            "title": title,
            "slug": slug,
            "mission_brief": "Recover the artifact.",
            "objectives": ["Find it"],
            "points": points,
            "story_fragment": "THE",
        },
    )
    assert response.status_code == 201, response.text
    challenge_id = response.json()["id"]

    response = client.post(f"/admin/challenges/{challenge_id}/flags", json={"value": flag})
    assert response.status_code == 201, response.text

    response = client.patch(
        f"/admin/challenges/{challenge_id}/publish", json={"status": "published"}
    )
    assert response.status_code == 200, response.text
    return challenge_id


def test_full_core_loop(db, admin_client, seed_reference_data):
    client = admin_client
    act1 = get_act(db, 1)
    act2 = get_act(db, 2)

    # Threshold small enough for a two-challenge test, but still exercising the rule.
    act1.unlock_threshold_points = 150
    db.commit()

    first = _create_published_challenge(client, act1.id, "Hidden Profile", "hidden-profile", 100, ACT1_FLAG)
    second = _create_published_challenge(
        client, act1.id, "Forgotten Repository", "forgotten-repository", 50, ACT1_FLAG_2
    )
    locked = _create_published_challenge(client, act2.id, "Login Failure", "login-failure", 200, ACT2_FLAG)

    client.post("/auth/logout")
    client.cookies.clear()

    # --- participant ---
    team_fixture = make_team(db)
    set_rate_limit(db)
    response = client.post(
        "/auth/login", json={"email": team_fixture.email, "password": PASSWORD}
    )
    assert response.status_code == 200, response.text

    # Sees Act I unlocked, Act II locked.
    response = client.get("/challenges")
    assert response.status_code == 200, response.text
    listing = response.json()
    assert listing["current_act"] == 1
    assert listing["current_score"] == 0

    acts_by_number = {group["act"]["act_number"]: group for group in listing["acts"]}
    assert acts_by_number[1]["act"]["unlocked"] is True
    assert acts_by_number[1]["act"]["required_points"] == 150
    assert acts_by_number[1]["act"]["total_points"] == 150
    assert acts_by_number[2]["act"]["unlocked"] is False

    # A locked challenge is listed but its brief and objectives are withheld.
    locked_entry = next(c for c in acts_by_number[2]["challenges"] if c["id"] == locked)
    assert locked_entry["locked"] is True
    assert locked_entry["mission_brief"] == ""
    assert locked_entry["objectives"] == []
    assert locked_entry["points"] == 200

    # Wrong flag -> clear response, no points.
    response = client.post(f"/challenges/{first}/submissions", json={"flag": "PacketCapture{NOPE}"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["correct"] is False
    assert body["awarded_points"] == 0
    assert body["current_score"] == 0

    # Locked Act -> CHALLENGE_LOCKED envelope.
    response = client.post(f"/challenges/{locked}/submissions", json={"flag": ACT2_FLAG})
    assert response.status_code == 403, response.text
    assert response.json()["code"] == "CHALLENGE_LOCKED"

    # Correct flag -> points awarded, no unlock yet (100 < 150).
    response = client.post(f"/challenges/{first}/submissions", json={"flag": ACT1_FLAG})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["correct"] is True
    assert body["solved"] is True
    assert body["awarded_points"] == 100
    assert body["current_score"] == 100
    assert body["next_act_unlocked"] is None

    # Duplicate -> zero additional points.
    response = client.post(f"/challenges/{first}/submissions", json={"flag": ACT1_FLAG})
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "ALREADY_SOLVED"
    assert scoring.compute_investigation_score(db, team_fixture.team.id) == 100

    # Second solve crosses the threshold -> Act II unlocks in the same response.
    response = client.post(f"/challenges/{second}/submissions", json={"flag": ACT1_FLAG_2})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["current_score"] == 150
    assert body["next_act_unlocked"] is not None
    assert body["next_act_unlocked"]["act_number"] == 2

    # Act II is now genuinely submittable.
    response = client.post(f"/challenges/{locked}/submissions", json={"flag": ACT2_FLAG})
    assert response.status_code == 200, response.text
    assert response.json()["current_score"] == 350

    response = client.get("/challenges")
    listing = response.json()
    assert listing["current_act"] == 2
    assert listing["current_score"] == 350


def test_no_participant_response_leaks_flag_material(db, admin_client, seed_reference_data):
    client = admin_client
    act1 = get_act(db, 1)
    challenge_id = _create_published_challenge(
        client, act1.id, "Hidden Profile", "hidden-profile", 100, ACT1_FLAG
    )

    client.post("/auth/logout")
    client.cookies.clear()

    team_fixture = make_team(db)
    set_rate_limit(db)
    client.post("/auth/login", json={"email": team_fixture.email, "password": PASSWORD})

    bodies = [
        client.get("/challenges").text,
        client.get(f"/challenges/{challenge_id}").text,
        client.post(f"/challenges/{challenge_id}/submissions", json={"flag": ACT1_FLAG}).text,
        client.get("/challenges").text,
    ]

    for body in bodies:
        assert "PacketCapture{" not in body
        assert "flag_hash" not in body
        assert "hmac-sha256" not in body
        # story_fragment belongs to the Final Investigation (#22) and must not be
        # readable from the participant API.
        assert "story_fragment" not in body


def test_participant_cannot_reach_admin_routes(db, seed_reference_data, client):
    team_fixture = make_team(db)
    client.post("/auth/login", json={"email": team_fixture.email, "password": PASSWORD})

    checks = (
        client.get("/admin/challenges"),
        client.get("/admin/acts"),
        client.get("/admin/challenge-categories"),
        client.post("/admin/challenges", json={}),
        client.patch("/admin/acts/00000000-0000-0000-0000-000000000000", json={}),
    )
    for response in checks:
        assert response.status_code == 403, response.text
        assert response.json()["code"] == "ADMIN_REQUIRED"


def test_admin_recompute_progression_unlocks_after_threshold_edit(
    db, admin_client, seed_reference_data, client
):
    """An organizer lowering a threshold must not leave qualified teams stranded."""
    act1 = get_act(db, 1)
    act1.unlock_threshold_points = 500
    db.commit()

    challenge_id = _create_published_challenge(
        client, act1.id, "Hidden Profile", "hidden-profile", 100, ACT1_FLAG
    )
    admin_cookies = dict(client.cookies)

    client.cookies.clear()
    team_fixture = make_team(db)
    set_rate_limit(db)
    client.post("/auth/login", json={"email": team_fixture.email, "password": PASSWORD})
    response = client.post(f"/challenges/{challenge_id}/submissions", json={"flag": ACT1_FLAG})
    assert response.json()["next_act_unlocked"] is None

    client.cookies.clear()
    for name, value in admin_cookies.items():
        client.cookies.set(name, value)

    response = client.patch(f"/admin/acts/{act1.id}", json={"unlock_threshold_points": 100})
    assert response.status_code == 200, response.text

    response = client.post(f"/admin/teams/{team_fixture.team.id}/recompute-progression")
    assert response.status_code == 200, response.text
    unlocked = response.json()
    assert [act["act_number"] for act in unlocked] == [2]
