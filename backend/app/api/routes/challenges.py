"""Participant challenge reads (#14).

Provides the backend side of the participant challenge list; issue #12 owns the frontend
that consumes it.

``_challenge_to_participant_response`` is the single chokepoint through which challenge
data reaches a participant, so "no flag material ever leaves the database" is enforced in
exactly one place and asserted by a test that sweeps every response body.

These are GET endpoints and therefore must not write. They call
``ensure_initial_act_unlock`` -- the one exception, which is idempotent and needed because
team registration belongs to another developer's route.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_team
from app.core.errors import APIError
from app.db.session import get_db
from app.models.act import Act
from app.models.challenge import Challenge, ChallengeStatus
from app.models.submission import Solve
from app.models.team import Team
from app.schemas.challenge import (
    ActChallengeGroupResponse,
    ActProgressResponse,
    ChallengeListResponse,
    ChallengeParticipantResponse,
)
from app.services import scoring

router = APIRouter()


def _act_progress_to_response(
    act: Act,
    unlocked: bool,
    total: int,
    earned: int,
    required: int,
) -> ActProgressResponse:
    return ActProgressResponse(
        id=act.id,
        act_number=act.act_number,
        slug=act.slug,
        title=act.title,
        description=act.description,
        unlocked=unlocked,
        total_points=total,
        earned_points=earned,
        required_points=required,
    )


def _challenge_to_participant_response(
    challenge: Challenge,
    locked: bool,
    solved: bool,
    awarded_points: int | None,
) -> ChallengeParticipantResponse:
    return ChallengeParticipantResponse(
        id=challenge.id,
        act_id=challenge.act_id,
        act_number=challenge.act.act_number,
        title=challenge.title,
        slug=challenge.slug,
        category=challenge.category.name if challenge.category else None,
        difficulty=challenge.difficulty.name if challenge.difficulty else None,
        points=challenge.points,
        # Locked challenges expose their existence and point value (so a team can see what
        # they are working toward) but never their brief, context, or objectives.
        mission_brief="" if locked else challenge.mission_brief,
        story_context=None if locked else challenge.story_context,
        objectives=[] if locked else list(challenge.objectives_json or []),
        locked=locked,
        solved=solved,
        awarded_points=awarded_points,
    )


@router.get("", response_model=ChallengeListResponse)
def list_challenges(
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> ChallengeListResponse:
    scoring.ensure_initial_act_unlock(db, team.id)
    db.commit()

    acts = db.scalars(select(Act).where(Act.is_active.is_(True)).order_by(Act.act_number)).all()
    unlocked_ids = scoring.unlocked_act_ids(db, team.id)

    solves = {
        row.challenge_id: row.points_awarded
        for row in db.scalars(select(Solve).where(Solve.team_id == team.id)).all()
    }

    challenges = db.scalars(
        select(Challenge)
        .options(
            joinedload(Challenge.act),
            joinedload(Challenge.category),
            joinedload(Challenge.difficulty),
        )
        .where(
            Challenge.status == ChallengeStatus.PUBLISHED.value,
            Challenge.is_visible.is_(True),
        )
        .order_by(Challenge.sort_order, Challenge.title)
    ).all()

    by_act: dict[UUID, list[Challenge]] = {}
    for challenge in challenges:
        by_act.setdefault(challenge.act_id, []).append(challenge)

    groups: list[ActChallengeGroupResponse] = []
    for act in acts:
        unlocked = act.id in unlocked_ids
        total, earned, required = scoring.act_progress(db, team.id, act)
        groups.append(
            ActChallengeGroupResponse(
                act=_act_progress_to_response(act, unlocked, total, earned, required),
                challenges=[
                    _challenge_to_participant_response(
                        challenge,
                        locked=not unlocked,
                        solved=challenge.id in solves,
                        awarded_points=solves.get(challenge.id),
                    )
                    for challenge in by_act.get(act.id, [])
                ],
            )
        )

    return ChallengeListResponse(
        acts=groups,
        current_act=scoring.current_act_number(db, team.id),
        current_score=scoring.compute_investigation_score(db, team.id),
    )


@router.get("/{challenge_id}", response_model=ChallengeParticipantResponse)
def get_challenge(
    challenge_id: UUID,
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> ChallengeParticipantResponse:
    challenge = db.scalar(
        select(Challenge)
        .options(
            joinedload(Challenge.act),
            joinedload(Challenge.category),
            joinedload(Challenge.difficulty),
        )
        .where(Challenge.id == challenge_id)
    )
    if (
        challenge is None
        or challenge.status != ChallengeStatus.PUBLISHED.value
        or not challenge.is_visible
    ):
        # Same indistinguishability rule as the submission path: never reveal that a
        # draft or archived challenge exists.
        raise APIError(status.HTTP_404_NOT_FOUND, "CHALLENGE_NOT_FOUND", "Challenge not found.")

    scoring.ensure_initial_act_unlock(db, team.id)
    db.commit()

    locked = not scoring.team_can_access_act(db, team.id, challenge.act)
    solve = db.scalar(
        select(Solve).where(Solve.team_id == team.id, Solve.challenge_id == challenge.id)
    )

    return _challenge_to_participant_response(
        challenge,
        locked=locked,
        solved=solve is not None,
        awarded_points=solve.points_awarded if solve else None,
    )
