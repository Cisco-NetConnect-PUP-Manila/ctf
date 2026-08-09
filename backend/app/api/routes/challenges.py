"""Participant-safe challenge reads for Issue #12."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_team
from app.core.errors import APIError, LOCKED_CHALLENGE, NOT_FOUND
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


def _challenge_response(
    challenge: Challenge,
    *,
    locked: bool,
    solved_ids: set[UUID],
    awarded_points: dict[UUID, int],
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
        mission_brief=challenge.mission_brief,
        story_context=challenge.story_context,
        objectives=list(challenge.objectives_json or []),
        locked=locked,
        solved=challenge.id in solved_ids,
        awarded_points=awarded_points.get(challenge.id),
    )


def _published_challenges_query():
    return (
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
    )


@router.get("", response_model=ChallengeListResponse)
def list_challenges(
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> ChallengeListResponse:
    scoring.ensure_initial_act_unlock(db, team.id)
    db.commit()

    acts = db.scalars(select(Act).order_by(Act.sort_order, Act.act_number)).all()
    challenges = db.scalars(
        _published_challenges_query().order_by(Challenge.act_id, Challenge.sort_order, Challenge.title)
    ).unique().all()
    challenges_by_act: dict[UUID, list[Challenge]] = {}
    for challenge in challenges:
        challenges_by_act.setdefault(challenge.act_id, []).append(challenge)

    solved_ids = scoring.solved_challenge_ids(db, team.id)
    awarded_points = {
        challenge_id: points
        for challenge_id, points in db.execute(
            select(Solve.challenge_id, Solve.points_awarded).where(Solve.team_id == team.id)
        ).all()
    }
    unlocked_ids = scoring.unlocked_act_ids(db, team.id)

    groups: list[ActChallengeGroupResponse] = []
    for act in acts:
        total_points = scoring.act_total_points(db, act.id)
        earned_points = scoring.act_earned_points(db, team.id, act.id)
        unlocked = act.is_active and act.id in unlocked_ids
        groups.append(
            ActChallengeGroupResponse(
                act=ActProgressResponse(
                    id=act.id,
                    act_number=act.act_number,
                    slug=act.slug,
                    title=act.title,
                    description=act.description,
                    unlocked=unlocked,
                    total_points=total_points,
                    earned_points=earned_points,
                    required_points=scoring.resolve_threshold(act, total_points),
                ),
                challenges=[
                    _challenge_response(
                        challenge,
                        locked=not unlocked,
                        solved_ids=solved_ids,
                        awarded_points=awarded_points,
                    )
                    for challenge in challenges_by_act.get(act.id, [])
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
    scoring.ensure_initial_act_unlock(db, team.id)
    db.commit()

    challenge = db.scalar(_published_challenges_query().where(Challenge.id == challenge_id))
    if challenge is None:
        raise APIError(404, NOT_FOUND, "Challenge not found.")
    if not scoring.team_can_access_act(db, team.id, challenge.act):
        raise APIError(422, LOCKED_CHALLENGE, "This challenge is not available yet.")

    solved_ids = scoring.solved_challenge_ids(db, team.id)
    points_awarded = db.scalar(
        select(Solve.points_awarded).where(
            Solve.team_id == team.id,
            Solve.challenge_id == challenge.id,
        )
    )
    return _challenge_response(
        challenge,
        locked=False,
        solved_ids=solved_ids,
        awarded_points={challenge.id: points_awarded} if points_awarded is not None else {},
    )
