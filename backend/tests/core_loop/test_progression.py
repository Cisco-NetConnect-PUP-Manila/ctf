"""Scoring and Act progression tests (#14)."""

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import func, select

from app.models.act import ActUnlock
from app.models.challenge import ChallengeStatus
from app.services import scoring
from app.services.submissions import SubmissionError, submit_flag
from tests.core_loop.factories import get_act, make_challenge, make_team, set_rate_limit

FLAG = "PacketCapture{TEST_FLAG}"


@pytest.fixture
def team_fixture(db, seed_reference_data):
    fixture = make_team(db)
    scoring.ensure_initial_act_unlock(db, fixture.team.id)
    db.commit()
    set_rate_limit(db)
    return fixture


# ------------------------------------------------------------------ threshold resolution


def test_absolute_threshold_overrides_percentage(db, seed_reference_data):
    """Pins the documented contradiction.

    The handoff's prose rule says 20 percent of Act I's 800 points, i.e. 160. Its flags
    table says 500. The seed ships the table, so 500 must win.
    """
    act1 = get_act(db, 1)
    assert act1.unlock_threshold_points == 500
    assert act1.unlock_threshold_percent == 20

    assert scoring.resolve_threshold(act1, 800) == 500


def test_percentage_is_used_when_absolute_threshold_is_cleared(db, seed_reference_data):
    """Organizers can switch to the 20 percent rule without a migration."""
    act1 = get_act(db, 1)
    act1.unlock_threshold_points = None
    db.commit()

    assert scoring.resolve_threshold(act1, 800) == 160
    assert scoring.resolve_threshold(act1, 1125) == 225  # ceil(225.0)
    assert scoring.resolve_threshold(act1, 801) == 161  # rounds up, never down


def test_act_total_counts_only_published_and_visible_challenges(db, seed_reference_data):
    """Drafts must not raise the bar, or an Act can become impossible to escape."""
    act1 = get_act(db, 1)
    make_challenge(db, act1, points=100)
    make_challenge(db, act1, points=200, status=ChallengeStatus.DRAFT)
    make_challenge(db, act1, points=400, is_visible=False)
    make_challenge(db, act1, points=800, status=ChallengeStatus.ARCHIVED)

    assert scoring.act_total_points(db, act1.id) == 100


# ------------------------------------------------------------------------ unlock rules


def test_unlock_happens_exactly_at_the_threshold(db, team_fixture):
    act1 = get_act(db, 1)
    act1.unlock_threshold_points = 100
    db.commit()

    below = make_challenge(db, act1, points=99, flag=FLAG)
    result = submit_flag(db, team_fixture.team, below.id, FLAG)
    assert result.next_act_unlocked is None
    assert scoring.current_act_number(db, team_fixture.team.id) == 1

    exact = make_challenge(db, act1, points=1, flag=FLAG)
    result = submit_flag(db, team_fixture.team, exact.id, FLAG)

    assert result.next_act_unlocked is not None
    assert result.next_act_unlocked.act_number == 2
    assert scoring.current_act_number(db, team_fixture.team.id) == 2


def test_unlocking_act_two_makes_its_challenges_submittable(db, team_fixture):
    act1 = get_act(db, 1)
    act2 = get_act(db, 2)
    act1.unlock_threshold_points = 100
    db.commit()

    gate = make_challenge(db, act1, points=100, flag=FLAG)
    act2_challenge = make_challenge(db, act2, points=150, flag=FLAG)

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, team_fixture.team, act2_challenge.id, FLAG)
    assert excinfo.value.code == "LOCKED_CHALLENGE"

    submit_flag(db, team_fixture.team, gate.id, FLAG)

    result = submit_flag(db, team_fixture.team, act2_challenge.id, FLAG)
    assert result.correct is True
    assert result.current_score == 250


def test_unlock_is_idempotent_across_further_solves(db, team_fixture):
    act1 = get_act(db, 1)
    act1.unlock_threshold_points = 50
    db.commit()

    for _ in range(3):
        challenge = make_challenge(db, act1, points=50, flag=FLAG)
        submit_flag(db, team_fixture.team, challenge.id, FLAG)

    unlocks = db.scalar(
        select(func.count())
        .select_from(ActUnlock)
        .where(ActUnlock.team_id == team_fixture.team.id)
    )
    assert unlocks == 2  # Act I initial + Act II threshold


def test_lowering_a_threshold_cascades_multiple_unlocks(db, team_fixture):
    """Self-healing: one call can unlock several Acts after an organizer edit."""
    for number in (1, 2, 3):
        act = get_act(db, number)
        act.unlock_threshold_points = 10_000  # unreachable for now
    db.commit()

    act1 = get_act(db, 1)
    challenge = make_challenge(db, act1, points=100, flag=FLAG)
    result = submit_flag(db, team_fixture.team, challenge.id, FLAG)
    assert result.next_act_unlocked is None

    for number in (1, 2, 3):
        get_act(db, number).unlock_threshold_points = 0
    db.commit()

    newly = scoring.evaluate_act_unlocks(db, team_fixture.team.id)
    db.commit()

    assert [act.act_number for act in newly] == [2, 3, 4]
    assert scoring.current_act_number(db, team_fixture.team.id) == 4


def test_unlocks_are_never_revoked_when_points_would_no_longer_qualify(db, team_fixture):
    """Previously unlocked Acts stay accessible; nothing in scoring sets revoked_at."""
    act1 = get_act(db, 1)
    act1.unlock_threshold_points = 100
    db.commit()

    challenge = make_challenge(db, act1, points=100, flag=FLAG)
    submit_flag(db, team_fixture.team, challenge.id, FLAG)
    assert scoring.current_act_number(db, team_fixture.team.id) == 2

    act1.unlock_threshold_points = 5000
    db.commit()
    scoring.evaluate_act_unlocks(db, team_fixture.team.id)
    db.commit()

    assert scoring.current_act_number(db, team_fixture.team.id) == 2
    revoked = db.scalar(
        select(func.count())
        .select_from(ActUnlock)
        .where(ActUnlock.revoked_at.is_not(None))
    )
    assert revoked == 0


def test_inactive_act_is_inaccessible_even_when_unlocked(db, team_fixture):
    """Act-wide organizer locking, without destroying per-team unlock history."""
    act1 = get_act(db, 1)
    challenge = make_challenge(db, act1, points=100, flag=FLAG)

    act1.is_active = False
    db.commit()

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, team_fixture.team, challenge.id, FLAG)
    assert excinfo.value.code == "LOCKED_CHALLENGE"


# --------------------------------------------------------------------------- score


def test_score_is_derived_and_survives_challenge_archival(db, team_fixture):
    """points_awarded snapshots the value at solve time."""
    act1 = get_act(db, 1)
    challenge = make_challenge(db, act1, points=100, flag=FLAG)
    submit_flag(db, team_fixture.team, challenge.id, FLAG)
    assert scoring.compute_investigation_score(db, team_fixture.team.id) == 100

    challenge.points = 999
    challenge.status = ChallengeStatus.ARCHIVED.value
    db.commit()

    assert scoring.compute_investigation_score(db, team_fixture.team.id) == 100


# ---------------------------------------------------------------------- concurrency


def test_concurrent_solves_of_different_challenges_still_unlock(session_factory, db, team_fixture):
    """The race the unique constraint cannot catch.

    Two correct submissions for DIFFERENT challenges land simultaneously. Neither alone
    reaches the threshold, but together they cross it. Without the per-team FOR UPDATE
    lock each transaction computes Act progress without the other's uncommitted solve,
    no act_unlock is created, and the team is stranded on a locked Act with a passing
    score. This test is the reason that lock exists.
    """
    from app.models.team import Team

    act1 = get_act(db, 1)
    act1.unlock_threshold_points = 200
    db.commit()

    first = make_challenge(db, act1, points=100, flag=FLAG)
    second = make_challenge(db, act1, points=100, flag=FLAG)

    barrier = threading.Barrier(2)

    def worker(challenge_id):
        session = session_factory()
        try:
            team = session.get(Team, team_fixture.team.id)
            barrier.wait(timeout=30)
            return submit_flag(session, team, challenge_id, FLAG)
        except SubmissionError as error:
            return error
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [f.result() for f in [pool.submit(worker, first.id), pool.submit(worker, second.id)]]

    assert all(not isinstance(r, SubmissionError) for r in results), [
        r.code for r in results if isinstance(r, SubmissionError)
    ]

    check = session_factory()
    try:
        assert scoring.compute_investigation_score(check, team_fixture.team.id) == 200
        assert scoring.current_act_number(check, team_fixture.team.id) == 2, (
            "Act II should be unlocked; the team lock is what guarantees this"
        )
    finally:
        check.close()
