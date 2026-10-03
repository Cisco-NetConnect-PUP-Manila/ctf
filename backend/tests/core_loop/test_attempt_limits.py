from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import func, select

from app.models.submission import Submission
from app.schemas.challenge import ChallengeUpdateRequest
from app.services import scoring
from app.services.submissions import SubmissionError, submit_flag
from tests.core_loop.factories import get_act, make_challenge, make_team, set_rate_limit


@pytest.fixture
def budget(db, seed_reference_data):
    team = make_team(db).team
    challenge = make_challenge(db, get_act(db, 1))
    challenge.max_attempts = 2
    scoring.ensure_initial_act_unlock(db, team.id)
    db.commit()
    set_rate_limit(db)
    return team, challenge


def test_budget_is_per_team_and_can_be_raised_or_removed(db, budget):
    team, challenge = budget
    for _ in range(2):
        assert not submit_flag(db, team, challenge.id, 'wrong').correct
    with pytest.raises(SubmissionError) as denied:
        submit_flag(db, team, challenge.id, 'PacketCapture{TEST_FLAG}')
    assert denied.value.code == 'ATTEMPTS_EXHAUSTED'
    assert db.scalar(select(func.count()).select_from(Submission)) == 2
    other = make_team(db).team
    assert not submit_flag(db, other, challenge.id, 'wrong').correct
    challenge.max_attempts = 3
    db.commit()
    assert not submit_flag(db, team, challenge.id, 'wrong').correct
    challenge.max_attempts = None
    db.commit()
    assert submit_flag(db, team, challenge.id, 'PacketCapture{TEST_FLAG}').correct


def test_concurrent_wrong_flags_cannot_exceed_budget(db, budget, session_factory):
    team, challenge = budget
    barrier = Barrier(4)
    team_id, challenge_id = team.id, challenge.id
    db.rollback()  # Release the main session connection before concurrent callers.
    def attempt(_):
        with session_factory() as session:
            from app.models.team import Team
            own_team = session.get(Team, team_id)
            barrier.wait(timeout=10)
            try:
                submit_flag(session, own_team, challenge_id, 'wrong')
                return 'recorded'
            except SubmissionError as error:
                return error.code
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(attempt, range(4)))
    assert results.count('recorded') == 2
    assert results.count('ATTEMPTS_EXHAUSTED') == 2
    assert db.scalar(select(func.count()).select_from(Submission)) == 2


def test_attempt_limit_validation_and_explicit_unlimited():
    from pydantic import ValidationError
    for invalid in (0, -1, 1.5, True, 100001):
        with pytest.raises(ValidationError):
            ChallengeUpdateRequest(max_attempts=invalid)
    assert 'max_attempts' not in ChallengeUpdateRequest().model_fields_set
    assert 'max_attempts' in ChallengeUpdateRequest(max_attempts=None).model_fields_set


def test_admin_api_can_set_edit_and_remove_limit(client, db, seed_reference_data):
    from tests.core_loop.factories import make_admin, PASSWORD
    admin = make_admin(db)
    assert client.post('/auth/login', json={'email': admin.email, 'password': PASSWORD}).status_code == 200
    created = client.post('/admin/challenges', json={
        'act_id': str(get_act(db, 1).id), 'title': 'Limited challenge',
        'slug': 'limited-challenge', 'mission_brief': 'Find a flag', 'points': 100,
        'max_attempts': 3,
    })
    assert created.status_code == 201, created.text
    challenge_id = created.json()['id']
    assert created.json()['max_attempts'] == 3
    assert client.patch(f'/admin/challenges/{challenge_id}', json={'title': 'Renamed challenge'}).json()['max_attempts'] == 3
    assert client.patch(f'/admin/challenges/{challenge_id}', json={'max_attempts': 5}).json()['max_attempts'] == 5
    assert client.patch(f'/admin/challenges/{challenge_id}', json={'max_attempts': None}).json()['max_attempts'] is None
    assert client.patch(f'/admin/challenges/{challenge_id}', json={'max_attempts': 0}).status_code == 400


def test_participant_sees_only_own_budget_and_cannot_bypass_it(client, db, budget):
    from tests.core_loop.factories import PASSWORD
    team, challenge = budget
    email, challenge_id = team.account.email, str(challenge.id)
    assert client.post('/auth/login', json={'email': email, 'password': PASSWORD}).status_code == 200
    url = f'/challenges/{challenge_id}'
    assert client.get(url).json()['max_attempts'] == 2
    for used in (1, 2):
        assert client.post(url + '/submissions', json={'flag': 'wrong'}).status_code == 200
        assert client.get(url).json()['attempts_used'] == used
    denied = client.post(url + '/submissions', json={'flag': 'PacketCapture{TEST_FLAG}'})
    assert denied.status_code == 403
    assert denied.json()['code'] == 'ATTEMPTS_EXHAUSTED'
    other = make_team(db)
    assert client.post('/auth/login', json={'email': other.email, 'password': PASSWORD}).status_code == 200
    assert client.get(url).json()['attempts_used'] == 0
