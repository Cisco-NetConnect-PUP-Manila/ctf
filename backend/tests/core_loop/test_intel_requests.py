"""Intel Request persistence and score rules (#17)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.intel import Hint, IntelRequest
from app.services import scoring

from app.models.account import AccountRole
from app.models.platform_setting import PlatformSetting
from app.services.platform_settings import KEY_SUBMISSIONS_OPEN

from .factories import PASSWORD, get_act, make_account, make_challenge, make_team


def test_intel_penalty_reduces_score_without_reducing_act_progress(db, seed_reference_data):
    team = make_team(db)
    act = get_act(db, 1)
    challenge = make_challenge(db, act, points=100)

    hint = Hint(challenge_id=challenge.id, content="Inspect the metadata.", penalty_points=25)
    db.add(hint)
    db.flush()
    db.add(
        IntelRequest(
            team_id=team.team.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            penalty_points=hint.penalty_points,
        )
    )
    db.commit()

    assert scoring.compute_investigation_score(db, team.team.id) == -25
    assert scoring.act_earned_points(db, team.team.id, act.id) == 0


def test_same_hint_cannot_charge_the_same_team_twice(db, seed_reference_data):
    team = make_team(db)
    challenge = make_challenge(db, get_act(db, 1))
    hint = Hint(challenge_id=challenge.id, content="Follow the stream.", penalty_points=10)
    db.add(hint)
    db.flush()
    db.add(
        IntelRequest(
            team_id=team.team.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            penalty_points=10,
        )
    )
    db.commit()

    db.add(
        IntelRequest(
            team_id=team.team.id,
            challenge_id=challenge.id,
            hint_id=hint.id,
            penalty_points=10,
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()


def test_admin_configures_hint_and_participant_is_charged_once(
    db, client, seed_reference_data
):
    admin = make_account(db, role=AccountRole.ADMIN)
    challenge = make_challenge(db, get_act(db, 1))
    db.commit()
    assert client.post(
        "/auth/login", json={"email": admin.email, "password": PASSWORD}
    ).status_code == 200

    response = client.post(
        f"/admin/challenges/{challenge.id}/hints",
        json={"content": "Inspect the packet timestamps.", "penalty_points": 20},
    )
    assert response.status_code == 201, response.text
    hint_id = response.json()["id"]

    client.post("/auth/logout")
    client.cookies.clear()
    team = make_team(db)
    assert client.post(
        "/auth/login", json={"email": team.email, "password": PASSWORD}
    ).status_code == 200

    available = client.get(f"/challenges/{challenge.id}/hints")
    assert available.status_code == 200, available.text
    assert available.json() == [
        {
            "id": hint_id,
            "penalty_points": 20,
            "sort_order": 0,
            "requested": False,
            "content": None,
        }
    ]

    first = client.post(
        f"/challenges/{challenge.id}/intel-requests", json={"hint_id": hint_id}
    )
    assert first.status_code == 200, first.text
    assert first.json() == {
        "hint": "Inspect the packet timestamps.",
        "penalty_points": 20,
        "total_penalty": 20,
        "already_requested": False,
    }

    repeat = client.post(
        f"/challenges/{challenge.id}/intel-requests", json={"hint_id": hint_id}
    )
    assert repeat.status_code == 200, repeat.text
    assert repeat.json()["already_requested"] is True
    assert repeat.json()["total_penalty"] == 20
    assert scoring.compute_investigation_score(db, team.team.id) == -20


def test_closed_submissions_block_intel_listing_and_requests(db, client, seed_reference_data):
    team = make_team(db)
    challenge = make_challenge(db, get_act(db, 1))
    hint = Hint(challenge_id=challenge.id, content="This must remain closed.", penalty_points=10)
    db.add(hint)
    db.add(PlatformSetting(key=KEY_SUBMISSIONS_OPEN, value_json=False))
    db.commit()
    assert client.post(
        "/auth/login", json={"email": team.email, "password": PASSWORD}
    ).status_code == 200

    listing = client.get(f"/challenges/{challenge.id}/hints")
    request = client.post(
        f"/challenges/{challenge.id}/intel-requests", json={"hint_id": str(hint.id)}
    )

    assert listing.status_code == 403
    assert listing.json()["code"] == "SUBMISSIONS_CLOSED"
    assert request.status_code == 403
    assert request.json()["code"] == "SUBMISSIONS_CLOSED"


def test_repeated_intel_requests_are_rate_limited_without_duplicate_penalty(
    db, client, seed_reference_data, monkeypatch
):
    from app.api.routes import intel as intel_routes

    monkeypatch.setattr(intel_routes, "INTEL_REQUEST_LIMIT", 2)
    team = make_team(db)
    challenge = make_challenge(db, get_act(db, 1))
    hint = Hint(challenge_id=challenge.id, content="Rate-limited Intel.", penalty_points=15)
    db.add(hint)
    db.commit()
    assert client.post(
        "/auth/login", json={"email": team.email, "password": PASSWORD}
    ).status_code == 200
    path = f"/challenges/{challenge.id}/intel-requests"
    payload = {"hint_id": str(hint.id)}

    assert client.post(path, json=payload).status_code == 200
    assert client.post(path, json=payload).status_code == 200
    blocked = client.post(path, json=payload)

    assert blocked.status_code == 429
    assert blocked.json()["code"] == "RATE_LIMITED"
    assert scoring.compute_investigation_score(db, team.team.id) == -15
