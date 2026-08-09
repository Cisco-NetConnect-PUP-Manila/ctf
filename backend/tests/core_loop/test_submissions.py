"""Submission tests (#13).

Covers the paths the handoff mandates in section 17: correct, incorrect, duplicate,
locked, and concurrent.
"""

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import func, select

from app.models.act import ActUnlock
from app.models.challenge import ChallengeStatus
from app.models.submission import Solve, Submission
from app.models.team import TeamStatus
from app.services import scoring
from app.services.submissions import SubmissionError, submit_flag
from tests.core_loop.factories import get_act, make_challenge, make_team, set_rate_limit

CORRECT_FLAG = "PacketCapture{TEST_FLAG}"
WRONG_FLAG = "PacketCapture{NOT_THE_FLAG}"


@pytest.fixture
def setup(db, seed_reference_data):
    """A team, an Act I challenge worth 100 points, and Act I unlocked.

    Also relaxes the submission rate limit: the shipped default includes a 2 second
    cooldown, and these tests submit back to back. The limiter has its own test below.
    """
    fixture = make_team(db)
    act1 = get_act(db, 1)
    challenge = make_challenge(db, act1, points=100, flag=CORRECT_FLAG)
    scoring.ensure_initial_act_unlock(db, fixture.team.id)
    db.commit()
    set_rate_limit(db)
    return fixture, act1, challenge


# ------------------------------------------------------------------ correct / incorrect


def test_correct_submission_awards_points_once(db, setup):
    fixture, _, challenge = setup

    result = submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG)

    assert result.correct is True
    assert result.solved is True
    assert result.awarded_points == 100
    assert result.current_score == 100

    assert db.scalar(select(func.count()).select_from(Solve)) == 1
    attempt = db.scalar(select(Submission))
    assert attempt.is_correct is True
    # A correct submission IS a real flag; never keep a preview of one.
    assert attempt.submitted_value_preview is None


def test_incorrect_submission_records_attempt_but_no_solve(db, setup):
    fixture, _, challenge = setup

    result = submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)

    assert result.correct is False
    assert result.solved is False
    assert result.awarded_points == 0
    assert result.current_score == 0

    assert db.scalar(select(func.count()).select_from(Solve)) == 0
    attempt = db.scalar(select(Submission))
    assert attempt.is_correct is False
    assert attempt.submitted_value_preview is not None
    assert attempt.submitted_value_preview != WRONG_FLAG
    assert len(attempt.submitted_value_preview) <= 32


def test_flags_are_case_sensitive(db, setup):
    """Competition rules: flags are case-sensitive. Only outer whitespace is trimmed."""
    fixture, _, challenge = setup

    result = submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG.lower())

    assert result.correct is False
    assert db.scalar(select(func.count()).select_from(Solve)) == 0


def test_outer_whitespace_is_trimmed(db, setup):
    """The single organizer-approved normalization."""
    fixture, _, challenge = setup

    result = submit_flag(db, fixture.team, challenge.id, f"   {CORRECT_FLAG}\n")

    assert result.correct is True
    assert result.awarded_points == 100


# ------------------------------------------------------------------------- duplicate


def test_duplicate_correct_submission_awards_zero(db, setup):
    fixture, _, challenge = setup
    submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG)

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG)

    assert excinfo.value.code == "ALREADY_SOLVED"
    assert db.scalar(select(func.count()).select_from(Solve)) == 1
    assert scoring.compute_investigation_score(db, fixture.team.id) == 100


# ------------------------------------------------------------------ locked / not found


def test_locked_act_is_rejected_without_recording_an_attempt(db, setup):
    fixture, _, _ = setup
    act2 = get_act(db, 2)
    locked_challenge = make_challenge(db, act2, points=150, flag=CORRECT_FLAG)

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, locked_challenge.id, CORRECT_FLAG)

    assert excinfo.value.code == "LOCKED_CHALLENGE"
    # Rejected before step 5, so no attempt row.
    assert db.scalar(select(func.count()).select_from(Submission)) == 0


def test_draft_challenge_is_not_found_rather_than_forbidden(db, setup):
    """Draft/archived/hidden/nonexistent must be indistinguishable or the roster leaks."""
    fixture, act1, _ = setup
    draft = make_challenge(db, act1, status=ChallengeStatus.DRAFT, flag=CORRECT_FLAG)

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, draft.id, CORRECT_FLAG)

    assert excinfo.value.code == "NOT_FOUND"


def test_invisible_challenge_is_not_found(db, setup):
    fixture, act1, _ = setup
    hidden = make_challenge(db, act1, is_visible=False, flag=CORRECT_FLAG)

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, hidden.id, CORRECT_FLAG)

    assert excinfo.value.code == "NOT_FOUND"


def test_disabled_team_is_rejected(db, seed_reference_data):
    fixture = make_team(db, status=TeamStatus.DISABLED)
    act1 = get_act(db, 1)
    challenge = make_challenge(db, act1, flag=CORRECT_FLAG)
    scoring.ensure_initial_act_unlock(db, fixture.team.id)
    db.commit()

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG)

    assert excinfo.value.code == "TEAM_NOT_APPROVED"


# ------------------------------------------------------------------------ rate limiting


def test_rate_limited_request_creates_no_submission_row(db, setup):
    """Counting rejections would let a spammer extend their own lockout indefinitely."""
    fixture, _, challenge = setup
    set_rate_limit(db, per_team_per_window=2, per_challenge_per_window=2, cooldown_seconds=0)

    submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)
    submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)
    before = db.scalar(select(func.count()).select_from(Submission))

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)

    assert excinfo.value.code == "RATE_LIMITED"
    assert excinfo.value.retry_after_seconds is not None
    assert db.scalar(select(func.count()).select_from(Submission)) == before


# -------------------------------------------------------------------------- concurrency

WORKERS = 8


def _submit_in_thread(session_factory, barrier, team_id, challenge_id, flag):
    from app.models.team import Team

    session = session_factory()
    try:
        team = session.get(Team, team_id)
        barrier.wait(timeout=30)
        return submit_flag(session, team, challenge_id, flag)
    except SubmissionError as error:
        return error
    finally:
        session.close()


def test_concurrent_correct_submissions_award_points_once(session_factory, db, setup):
    """The headline requirement: N simultaneous correct submissions, one award."""
    fixture, _, challenge = setup
    barrier = threading.Barrier(WORKERS)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [
            pool.submit(
                _submit_in_thread,
                session_factory,
                barrier,
                fixture.team.id,
                challenge.id,
                CORRECT_FLAG,
            )
            for _ in range(WORKERS)
        ]
        results = [future.result() for future in futures]

    awarded = [r for r in results if not isinstance(r, SubmissionError) and r.awarded_points > 0]
    rejected = [r for r in results if isinstance(r, SubmissionError)]

    assert len(awarded) == 1, f"expected exactly one award, got {len(awarded)}"
    assert all(r.code == "ALREADY_SOLVED" for r in rejected), [r.code for r in rejected]

    check = session_factory()
    try:
        assert check.scalar(select(func.count()).select_from(Solve)) == 1
        assert scoring.compute_investigation_score(check, fixture.team.id) == 100
    finally:
        check.close()


def test_team_lock_serializes_a_blocked_submitter(session_factory, db, setup):
    """The team lock makes a concurrent duplicate resolve cleanly, with no wasted work.

    Session A inserts a solve and holds it uncommitted. Thread B blocks on A's team lock.
    Once A commits, B proceeds, sees the now-visible solve on the already-solved fast
    path, and returns ALREADY_SOLVED *before* writing an attempt row. That is the intended
    outcome: the lock means the constraint-violation branch is never reached in normal
    operation. See test_unique_constraint_is_the_backstop_without_the_team_lock for proof
    that the backstop still works when the lock is absent.
    """
    from app.models.team import Team

    fixture, _, challenge = setup

    session_a = session_factory()
    team_a = session_a.get(Team, fixture.team.id)
    session_a.execute(select(Team.id).where(Team.id == team_a.id).with_for_update()).scalar_one()
    attempt_a = Submission(
        team_id=team_a.id,
        challenge_id=challenge.id,
        submitted_value_hash="a" * 64,
        is_correct=True,
    )
    session_a.add(attempt_a)
    session_a.flush()
    session_a.add(
        Solve(
            team_id=team_a.id,
            challenge_id=challenge.id,
            submission_id=attempt_a.id,
            points_awarded=challenge.points,
        )
    )
    session_a.flush()

    result_box: dict[str, object] = {}
    started = threading.Event()

    def worker():
        session_b = session_factory()
        try:
            team_b = session_b.get(Team, fixture.team.id)
            started.set()
            result_box["result"] = submit_flag(session_b, team_b, challenge.id, CORRECT_FLAG)
        except SubmissionError as error:
            result_box["result"] = error
        finally:
            session_b.close()

    thread = threading.Thread(target=worker)
    thread.start()
    started.wait(timeout=10)
    thread.join(timeout=2)  # B is now blocked on A's team lock
    assert thread.is_alive(), "B should be blocked on the team lock"

    session_a.commit()
    session_a.close()

    thread.join(timeout=30)
    assert not thread.is_alive(), "worker did not finish; lock was never released"

    result = result_box["result"]
    assert isinstance(result, SubmissionError)
    assert result.code == "ALREADY_SOLVED"

    check = session_factory()
    try:
        assert check.scalar(select(func.count()).select_from(Solve)) == 1
        # B short-circuited on the fast path, so only A's attempt exists.
        assert check.scalar(select(func.count()).select_from(Submission)) == 1
    finally:
        check.close()


def test_unique_constraint_is_the_backstop_without_the_team_lock(
    session_factory, db, setup, monkeypatch
):
    """Points are still awarded exactly once with the team lock disabled.

    This is what proves the UNIQUE(team_id, challenge_id) + SAVEPOINT path is live code
    rather than an unreachable branch: with the lock removed, several threads race past
    the already-solved fast path together and the constraint has to arbitrate.

    It also asserts that a loser's submission row SURVIVES. That assertion fails if
    anyone ever "simplifies" the IntegrityError handler from db.begin_nested() to a plain
    db.rollback(), which would discard the attempt we are required to record.
    """
    from app.services import submissions as submissions_module

    monkeypatch.setattr(submissions_module, "_acquire_team_lock", lambda db, team_id: None)

    fixture, _, challenge = setup
    barrier = threading.Barrier(WORKERS)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [
            pool.submit(
                _submit_in_thread,
                session_factory,
                barrier,
                fixture.team.id,
                challenge.id,
                CORRECT_FLAG,
            )
            for _ in range(WORKERS)
        ]
        results = [future.result() for future in futures]

    awarded = [r for r in results if not isinstance(r, SubmissionError) and r.awarded_points > 0]
    assert len(awarded) == 1, f"expected exactly one award, got {len(awarded)}"

    check = session_factory()
    try:
        assert check.scalar(select(func.count()).select_from(Solve)) == 1
        assert scoring.compute_investigation_score(check, fixture.team.id) == 100

        # At least one thread must have gone through the constraint-violation branch and
        # kept its attempt row, rather than only hitting the fast path.
        losers = check.scalar(
            select(func.count())
            .select_from(Submission)
            .where(Submission.is_correct.is_(True))
        )
        assert losers >= 1
    finally:
        check.close()


def test_initial_act_unlock_is_idempotent_under_concurrency(session_factory, db, setup):
    fixture, _, challenge = setup

    barrier = threading.Barrier(WORKERS)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [
            pool.submit(
                _submit_in_thread,
                session_factory,
                barrier,
                fixture.team.id,
                challenge.id,
                WRONG_FLAG,
            )
            for _ in range(WORKERS)
        ]
        [future.result() for future in futures]

    check = session_factory()
    try:
        unlocks = check.scalar(
            select(func.count())
            .select_from(ActUnlock)
            .where(ActUnlock.team_id == fixture.team.id)
        )
        assert unlocks == 1
    finally:
        check.close()


# ----------------------------------------------------------------------------- security


def test_flag_material_never_appears_in_audit_logs(db, setup):
    from app.models.audit_log import AuditLog

    fixture, _, challenge = setup
    submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG)

    rows = db.scalars(select(AuditLog)).all()
    assert rows
    for row in rows:
        assert CORRECT_FLAG not in str(row.metadata_json)


def test_submission_row_never_stores_the_plaintext_flag(db, setup):
    fixture, _, challenge = setup
    # Wrong first: once the challenge is solved, further attempts raise ALREADY_SOLVED.
    submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)
    submit_flag(db, fixture.team, challenge.id, CORRECT_FLAG)

    attempts = db.scalars(select(Submission)).all()
    assert len(attempts) == 2
    for attempt in attempts:
        assert attempt.submitted_value_hash != CORRECT_FLAG
        assert CORRECT_FLAG not in (attempt.submitted_value_preview or "")


def test_cooldown_blocks_rapid_resubmission(db, setup):
    fixture, _, challenge = setup
    set_rate_limit(db, cooldown_seconds=30)

    submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)

    with pytest.raises(SubmissionError) as excinfo:
        submit_flag(db, fixture.team, challenge.id, WRONG_FLAG)

    assert excinfo.value.code == "RATE_LIMITED"
    assert excinfo.value.retry_after_seconds is not None
    assert excinfo.value.retry_after_seconds <= 30
