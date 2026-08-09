"""Investigation Score and Act access.

Score is DERIVED from source records, never a denormalized counter.
``docs/database-normalization.md`` section 10 mandates it, and the deciding argument is
ownership: the eventual formula is ``solves - intel penalties (#17) + adjustments``, and
two of those three terms belong to developers landing later. A cached counter would make
every future contributor a possible source of silent score corruption, which in a live CTF
is unrecoverable by inspection.

No function in this module commits. The caller owns the transaction.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.act import Act, ActUnlock, ActUnlockReason
from app.models.challenge import Challenge, ChallengeStatus
from app.models.submission import Solve

FIRST_ACT_NUMBER = 1


def compute_investigation_score(db: Session, team_id: UUID) -> int:
    """The team's Investigation Score.

    Intel Request penalties (#17) and admin score adjustments become additional terms
    here -- this is the single place that definition lives.
    """
    total = db.scalar(
        select(func.coalesce(func.sum(Solve.points_awarded), 0)).where(Solve.team_id == team_id)
    )
    return int(total or 0)


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
