"""Investigation Score and Act access.

Score is DERIVED from source records, never a denormalized counter.
``docs/database-normalization.md`` section 10 mandates it, and the deciding argument is
ownership: the eventual formula is ``solves - intel penalties (#17) + adjustments``, and
two of those three terms belong to developers landing later. A cached counter would make
every future contributor a possible source of silent score corruption, which in a live CTF
is unrecoverable by inspection.

No function in this module commits. The caller owns the transaction.
"""

from math import ceil
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.act import Act, ActUnlock, ActUnlockReason
from app.models.challenge import Challenge, ChallengeStatus
from app.models.submission import Solve
from app.models.intel import IntelRequest

FIRST_ACT_NUMBER = 1


def compute_investigation_score(db: Session, team_id: UUID) -> int:
    """The team's Investigation Score.

    Intel Request penalties (#17) and admin score adjustments become additional terms
    here -- this is the single place that definition lives.
    """
    solve_total = db.scalar(
        select(func.coalesce(func.sum(Solve.points_awarded), 0)).where(Solve.team_id == team_id)
    )
    penalty_total = db.scalar(
        select(func.coalesce(func.sum(IntelRequest.penalty_points), 0)).where(
            IntelRequest.team_id == team_id
        )
    )
    return int(solve_total or 0) - int(penalty_total or 0)


def solved_challenge_ids(db: Session, team_id: UUID) -> set[UUID]:
    return set(db.scalars(select(Solve.challenge_id).where(Solve.team_id == team_id)).all())


def act_total_points(db: Session, act_id: UUID) -> int:
    """Reachable points in an Act.

    Counts published AND visible challenges only. Including drafts would mean a challenge
    author leaving something unpublished silently raises the bar, and can make an Act
    mathematically impossible to escape.
    """
    total = db.scalar(
        select(func.coalesce(func.sum(Challenge.points), 0)).where(
            Challenge.act_id == act_id,
            Challenge.status == ChallengeStatus.PUBLISHED.value,
            Challenge.is_visible.is_(True),
        )
    )
    return int(total or 0)


def act_earned_points(db: Session, team_id: UUID, act_id: UUID) -> int:
    """Raw solve points a team has earned inside one Act.

    Deliberately NOT penalty-adjusted: hint penalties (#17) must not be able to push a
    team backwards out of an Act they already entered, which would contradict
    "previously unlocked Acts remain accessible".
    """
    total = db.scalar(
        select(func.coalesce(func.sum(Solve.points_awarded), 0))
        .select_from(Solve)
        .join(Challenge, Challenge.id == Solve.challenge_id)
        .where(Solve.team_id == team_id, Challenge.act_id == act_id)
    )
    return int(total or 0)


def unlocked_act_ids(db: Session, team_id: UUID) -> set[UUID]:
    return set(
        db.scalars(
            select(ActUnlock.act_id).where(
                ActUnlock.team_id == team_id,
                ActUnlock.revoked_at.is_(None),
            )
        ).all()
    )


def ensure_initial_act_unlock(db: Session, team_id: UUID) -> None:
    """Grant Act I lazily, so team registration (another developer's route) is untouched.

    Idempotent via ``uq_act_unlocks_team_act``; the caller holds the team lock on the
    submission path, and the constraint covers every other path.
    """
    first_act = db.scalar(select(Act).where(Act.act_number == FIRST_ACT_NUMBER))
    if first_act is None:
        return

    already = db.scalar(
        select(ActUnlock.id).where(
            ActUnlock.team_id == team_id,
            ActUnlock.act_id == first_act.id,
        )
    )
    if already is not None:
        return

    db.add(
        ActUnlock(
            team_id=team_id,
            act_id=first_act.id,
            reason=ActUnlockReason.INITIAL.value,
        )
    )
    db.flush()


def team_can_access_act(db: Session, team_id: UUID, act: Act) -> bool:
    if not act.is_active:
        return False
    return (
        db.scalar(
            select(ActUnlock.id).where(
                ActUnlock.team_id == team_id,
                ActUnlock.act_id == act.id,
                ActUnlock.revoked_at.is_(None),
            )
        )
        is not None
    )


def current_act_number(db: Session, team_id: UUID) -> int:
    """Highest Act number currently accessible to the team."""
    value = db.scalar(
        select(func.coalesce(func.max(Act.act_number), 0))
        .select_from(ActUnlock)
        .join(Act, Act.id == ActUnlock.act_id)
        .where(
            ActUnlock.team_id == team_id,
            ActUnlock.revoked_at.is_(None),
            Act.is_active.is_(True),
        )
    )
    return int(value or 0)


# --------------------------------------------------------------- Act progression (#14)


def resolve_threshold(act: Act, act_total_points_value: int) -> int:
    """Points required inside ``act`` to unlock the next one.

    The handoff contradicts itself: its prose says "20 percent of the total points of the
    current challenge set", but its flags table gives explicit per-Act minimums of
    500/700/700/700, which are 62-70 percent and not even a consistent ratio. No formula
    recovers the table from the rule, so the threshold is stored as data on the Act and
    the absolute column wins when set.

    The seed ships the explicit table per the website lead's decision. Clearing
    ``unlock_threshold_points`` falls back to the percentage rule with no migration.
    """
    if act.unlock_threshold_points is not None:
        return act.unlock_threshold_points
    return ceil(act_total_points_value * act.unlock_threshold_percent / 100)


def act_progress(db: Session, team_id: UUID, act: Act) -> tuple[int, int, int]:
    """Return ``(total_points, earned_points, required_points)`` for one Act."""
    total = act_total_points(db, act.id)
    earned = act_earned_points(db, team_id, act.id)
    return total, earned, resolve_threshold(act, total)


def evaluate_act_unlocks(db: Session, team_id: UUID) -> list[Act]:
    """Create any act_unlock rows the team has now earned. Never commits.

    Callers on the submission path MUST hold the team ``FOR UPDATE`` lock; without it two
    concurrent solves can each compute progress without the other's points and neither
    creates the unlock.

    Evaluates ALL unlocked Acts rather than only the one just solved in, which makes the
    function self-healing: if an admin edits point values or a threshold, the team's next
    submission repairs their progression with no backfill job. It also lets a single call
    cascade several unlocks after a threshold is lowered. Four rows -- the cost is
    irrelevant.
    """
    acts = db.scalars(select(Act).where(Act.is_active.is_(True)).order_by(Act.act_number)).all()
    by_number = {act.act_number: act for act in acts}
    unlocked = unlocked_act_ids(db, team_id)

    newly: list[Act] = []
    for act in acts:
        if act.id not in unlocked:
            continue
        next_act = by_number.get(act.act_number + 1)
        if next_act is None or next_act.id in unlocked:
            continue

        total, earned, required = act_progress(db, team_id, act)
        if earned < required:
            continue

        try:
            with db.begin_nested():  # SAVEPOINT; uq_act_unlocks_team_act arbitrates
                db.add(
                    ActUnlock(
                        team_id=team_id,
                        act_id=next_act.id,
                        reason=ActUnlockReason.SCORE_THRESHOLD.value,
                        source_score=earned,
                        threshold_points=required,
                    )
                )
                db.flush()
        except IntegrityError:
            # Another transaction created it first. Idempotent, not an error.
            unlocked.add(next_act.id)
            continue

        unlocked.add(next_act.id)
        newly.append(next_act)

    return newly
