"""Intel Request persistence and score rules (#17)."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.intel import Hint, IntelRequest
from app.services import scoring

from .factories import get_act, make_challenge, make_team


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
