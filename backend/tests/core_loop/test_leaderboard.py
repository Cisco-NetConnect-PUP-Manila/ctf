"""Participant leaderboard ranking and visibility rules (#18)."""

from datetime import UTC, datetime, timedelta

from app.models.intel import Hint, IntelRequest
from app.models.platform_setting import PlatformSetting
from app.models.submission import Solve, Submission
from app.models.team import TeamStatus
from app.services import scoring
from app.services.platform_settings import KEY_LEADERBOARD_VISIBLE

from .factories import PASSWORD, get_act, make_challenge, make_team


def _record_solve(db, team_id, challenge_id, points, solved_at):
    submission = Submission(
        team_id=team_id,
        challenge_id=challenge_id,
        submitted_value_hash="a" * 64,
        is_correct=True,
        submitted_at=solved_at,
    )
    db.add(submission)
    db.flush()
    db.add(
        Solve(
            team_id=team_id,
            challenge_id=challenge_id,
            submission_id=submission.id,
            points_awarded=points,
            solved_at=solved_at,
        )
    )


def _login(client, email):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert response.status_code == 200


def test_leaderboard_is_hidden_by_default(db, client, seed_reference_data):
    team = make_team(db)
    _login(client, team.email)

    response = client.get("/leaderboard")

    assert response.status_code == 403
    assert response.json()["code"] == "LEADERBOARD_HIDDEN"


def test_leaderboard_requires_an_approved_participant(
    db, client, seed_reference_data
):
    assert client.get("/leaderboard").status_code == 401

    pending = make_team(db, status=TeamStatus.PENDING)
    db.add(PlatformSetting(key=KEY_LEADERBOARD_VISIBLE, value_json=True))
    db.commit()
    _login(client, pending.email)

    response = client.get("/leaderboard")
    assert response.status_code == 403
    assert response.json()["code"] == "TEAM_NOT_APPROVED"


def test_leaderboard_ranks_score_then_timing_and_exposes_safe_fields(
    db, client, seed_reference_data
):
    act = get_act(db, 1)
    challenge = make_challenge(db, act, points=100)
    alpha = make_team(db, group_name="Alpha Analysts")
    bravo = make_team(db, group_name="Bravo Bureau")
    charlie = make_team(db, group_name="Charlie Crew")
    pending = make_team(db, group_name="Pending Power", status=TeamStatus.PENDING)

    now = datetime.now(UTC)
    _record_solve(db, alpha.team.id, challenge.id, 100, now)
    _record_solve(db, bravo.team.id, challenge.id, 100, now - timedelta(minutes=5))
    _record_solve(db, charlie.team.id, challenge.id, 50, now - timedelta(minutes=10))
    _record_solve(db, pending.team.id, challenge.id, 500, now - timedelta(hours=1))

    hint = Hint(challenge_id=challenge.id, content="Paid Intel", penalty_points=10)
    db.add(hint)
    db.flush()
    for team in (alpha.team, bravo.team):
        db.add(
            IntelRequest(
                team_id=team.id,
                challenge_id=challenge.id,
                hint_id=hint.id,
                penalty_points=10,
            )
        )
        scoring.ensure_initial_act_unlock(db, team.id)
    scoring.ensure_initial_act_unlock(db, charlie.team.id)
    db.add(PlatformSetting(key=KEY_LEADERBOARD_VISIBLE, value_json=True))
    db.commit()

    _login(client, alpha.email)
    response = client.get("/leaderboard")

    assert response.status_code == 200
    body = response.json()
    assert body["generated_at"] is not None
    assert body["current_team_rank"] == 2
    assert [row["team_name"] for row in body["rows"]] == [
        "Bravo Bureau",
        "Alpha Analysts",
        "Charlie Crew",
    ]
    assert body["rows"][0] == {
        "rank": 1,
        "team_id": str(bravo.team.id),
        "team_name": "Bravo Bureau",
        "investigation_score": 90,
        "solved_count": 1,
        "current_act": 1,
        "intel_penalty": 10,
        "last_solve_at": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
    }
    assert body["rows"][2]["investigation_score"] == 50
    assert body["rows"][2]["intel_penalty"] == 0
    assert all(row["team_name"] != "Pending Power" for row in body["rows"])
