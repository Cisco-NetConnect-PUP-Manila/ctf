"""Flag submission (#13).

Lives in the service layer rather than the route handler so the concurrency tests can
drive it from N threads with N sessions on N connections. TestClient is synchronous and
cannot produce genuinely simultaneous in-flight transactions.

Transaction contract
--------------------
Isolation assumption is PostgreSQL's default READ COMMITTED. Correctness rests on two
mechanisms, both required:

1. ``SELECT ... FROM teams WHERE id = :id FOR UPDATE`` -- a per-team mutex held to commit.
   This is NOT redundant with the unique constraint. It fixes a race the constraint cannot
   see: a team submitting correct flags for two different challenges concurrently, where
   neither transaction sees the other's uncommitted solve, so each computes Act progress
   too low. If either alone is below the threshold but the sum crosses it, no act_unlock
   is created and the team is stuck on a locked Act with a passing score. That is a lost
   read, not a duplicate write.

2. ``UNIQUE (team_id, challenge_id)`` on solves, entered through ``begin_nested()``.
   In PostgreSQL a constraint violation aborts the whole transaction and poisons the
   SQLAlchemy session, so a plain ``except IntegrityError: db.rollback()`` would discard
   the submission attempt row we are required to record. The SAVEPOINT unwinds only the
   failed insert.

There is exactly ONE commit on every path. Any exception propagates and ``get_db()``'s
``finally: db.close()`` rolls back and releases the lock, so a write failure mid-scoring
cannot leave partial score state.

    Review rule: no helper called by submit_flag may ever call commit().

SessionLocal is built with ``autoflush=False``, so every read-after-write here needs an
explicit ``db.flush()`` or it returns a stale score.
"""

import hashlib
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.errors import (
    ALREADY_SOLVED,
    LOCKED_CHALLENGE,
    NOT_FOUND,
    RATE_LIMITED,
    SUBMISSIONS_CLOSED,
    TEAM_NOT_APPROVED,
)
from app.core.flags import (
    MAX_FLAG_LENGTH,
    flags_match,
    hash_flag,
    hash_submitted_value,
    incorrect_preview,
)
from app.core.rate_limit import RateLimited, enforce_submission_rate_limit
from app.models.act import Act
from app.models.audit_log import AuditLog
from app.models.challenge import Challenge, ChallengeFlag, ChallengeStatus
from app.models.submission import Solve, Submission
from app.models.team import Team, TeamStatus
from app.services import scoring
from app.services.platform_settings import submissions_are_open

logger = logging.getLogger(__name__)

# Guards against a stuck lock surfacing as a hung request.
LOCK_TIMEOUT = "5s"


class SubmissionError(Exception):
    """Domain error carrying an API contract code.

    Raised by the service so it stays framework-agnostic and directly testable; the route
    translates it into an APIError.
    """

    def __init__(self, code: str, message: str, retry_after_seconds: int | None = None) -> None:
        self.code = code
        self.message = message
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"{code}: {message}")


@dataclass
class SubmissionResult:
    correct: bool
    awarded_points: int
    current_score: int
    solved: bool
    message: str
    next_act_unlocked: Act | None = None


def hash_client_value(value: str | None) -> str | None:
    """Hash client metadata rather than storing it raw."""
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _acquire_team_lock(db: Session, team_id: UUID) -> None:
    """Take the per-team mutex, held until commit.

    Factored out so tests can disable it and prove the unique-constraint + SAVEPOINT
    backstop still awards points exactly once. With the lock in place the IntegrityError
    branch is unreachable in normal operation, which is precisely why it needs a test that
    removes the lock -- otherwise it is dead code nobody notices breaking.
    """
    db.execute(text(f"set local lock_timeout = '{LOCK_TIMEOUT}'"))
    db.execute(select(Team.id).where(Team.id == team_id).with_for_update()).scalar_one()


def verify_flag(db: Session, challenge_id: UUID, raw_value: str) -> bool:
    if len(raw_value) > MAX_FLAG_LENGTH:
        return False
    candidate = hash_flag(raw_value)
    stored = db.scalars(
        select(ChallengeFlag.flag_hash).where(
            ChallengeFlag.challenge_id == challenge_id,
            ChallengeFlag.is_active.is_(True),
        )
    ).all()
    # Constant-time compare against every active validator; a challenge may legitimately
    # have more than one (accepted aliases).
    return any(flags_match(candidate, item) for item in stored)


def submit_flag(
    db: Session,
    team: Team,
    challenge_id: UUID,
    raw_value: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> SubmissionResult:
    """Validate a flag and record the attempt. Commits exactly once.

    Never logs ``raw_value`` or its normalized form at any level.
    """
    # 1. Team gating. get_current_team already applied the approval policy; this is the
    #    service-level backstop for direct (test / future internal) callers.
    if team.status == TeamStatus.DISABLED.value:
        raise SubmissionError(TEAM_NOT_APPROVED, "This team has been disabled.")

    # 2. Competition open for submissions.
    if not submissions_are_open(db):
        raise SubmissionError(SUBMISSIONS_CLOSED, "Submissions are currently closed.")

    # 3. Load the challenge and verify published + visible.
    challenge = db.scalar(
        select(Challenge)
        .options(joinedload(Challenge.act))
        .where(Challenge.id == challenge_id)
    )
    if (
        challenge is None
        or challenge.status != ChallengeStatus.PUBLISHED.value
        or not challenge.is_visible
    ):
        # Draft, archived, hidden and nonexistent are deliberately indistinguishable --
        # distinguishing them leaks the challenge roster before release.
        raise SubmissionError(NOT_FOUND, "Challenge not found.")

    # ---- serialization point: per-team mutex, held until commit ----
    _acquire_team_lock(db, team.id)

    scoring.ensure_initial_act_unlock(db, team.id)

    # 3b. ...unlocked and accessible.
    if not scoring.team_can_access_act(db, team.id, challenge.act):
        raise SubmissionError(LOCKED_CHALLENGE, "This challenge is not available yet.")

    # 4. Rate limit BEFORE any validator work, per handoff section 10 step 4.
    #    Placed after the access check so a team hammering a locked challenge gets
    #    CHALLENGE_LOCKED rather than a confusing 429.
    try:
        enforce_submission_rate_limit(db, team.id, challenge.id)
    except RateLimited as limited:
        db.add(
            AuditLog(
                actor_account_id=team.account_id,
                action="submission.rate_limited",
                target_type="challenge",
                target_id=challenge.id,
                metadata_json={"team_id": str(team.id), "reason": limited.reason},
            )
        )
        db.commit()
        raise SubmissionError(
            "RATE_LIMITED",
            "Too many submissions. Please wait before trying again.",
            retry_after_seconds=limited.retry_after_seconds,
        ) from limited

    # Already-solved fast path. A friendly error, NOT the safety mechanism -- the unique
    # constraint below is what actually guarantees single award.
    existing_solve = db.scalar(
        select(Solve.id).where(Solve.team_id == team.id, Solve.challenge_id == challenge.id)
    )
    if existing_solve is not None:
        db.commit()  # nothing written; releases the lock cleanly
        raise SubmissionError(ALREADY_SOLVED, "Your team has already solved this challenge.")

    # 5. Record the attempt.
    attempt = Submission(
        team_id=team.id,
        challenge_id=challenge.id,
        submitted_value_hash=hash_submitted_value(raw_value),
        submitted_value_preview=incorrect_preview(raw_value),
        is_correct=False,
        ip_address_hash=hash_client_value(ip_address),
        user_agent_hash=hash_client_value(user_agent),
    )
    db.add(attempt)
    db.flush()

    # 6. Validate server-side.
    is_correct = verify_flag(db, challenge.id, raw_value)

    # 7. Incorrect: the attempt is already persisted with is_correct=False.
    if not is_correct:
        db.commit()
        return SubmissionResult(
            correct=False,
            awarded_points=0,
            current_score=scoring.compute_investigation_score(db, team.id),
            solved=False,
            message="Incorrect flag.",
        )

    # 8. Correct. Finalize the attempt BEFORE opening the savepoint so a savepoint
    #    rollback can never ambiguously revert these attribute changes.
    attempt.is_correct = True
    attempt.submitted_value_preview = None  # never preview a real flag
    db.flush()

    # 9. Create the solve, arbitrated by uq_solves_team_challenge.
    solve = Solve(
        team_id=team.id,
        challenge_id=challenge.id,
        submission_id=attempt.id,
        points_awarded=challenge.points,
    )
    try:
        with db.begin_nested():  # SAVEPOINT
            db.add(solve)
            db.flush()
    except IntegrityError:
        # ROLLBACK TO SAVEPOINT has already run, so the outer transaction is alive and the
        # attempt row above survives. Without the savepoint the session would be poisoned
        # and the attempt lost.
        db.commit()
        raise SubmissionError(
            "ALREADY_SOLVED", "Your team has already solved this challenge."
        ) from None

    # 10. Act progression, still uncommitted and still under the team lock.
    newly_unlocked = scoring.evaluate_act_unlocks(db, team.id)

    db.add(
        AuditLog(
            actor_account_id=team.account_id,
            action="challenge.solved",
            target_type="challenge",
            target_id=challenge.id,
            metadata_json={
                "team_id": str(team.id),
                "points": challenge.points,
                "submission_id": str(attempt.id),
            },
        )
    )
    for act in newly_unlocked:
        db.add(
            AuditLog(
                actor_account_id=team.account_id,
                action="act.unlocked",
                target_type="act",
                target_id=act.id,
                metadata_json={"team_id": str(team.id), "reason": "score_threshold"},
            )
        )

    db.flush()  # required: SessionLocal has autoflush=False
    current_score = scoring.compute_investigation_score(db, team.id)

    db.commit()  # THE single commit: attempt + solve + unlocks + audit, atomically
    # ---------------------------------------------------------------

    return SubmissionResult(
        correct=True,
        awarded_points=challenge.points,
        current_score=current_score,
        solved=True,
        message="Flag accepted.",
        next_act_unlocked=newly_unlocked[0] if newly_unlocked else None,
    )
