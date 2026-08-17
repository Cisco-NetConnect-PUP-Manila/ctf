"""Participant-safe challenge reads for Issue #12."""

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_team
from app.core.errors import APIError, LOCKED_CHALLENGE, NOT_FOUND, SUBMISSIONS_CLOSED
from app.core.team_fragments import derive_team_fragment
from app.db.session import get_db
from app.models.act import Act
from app.models.challenge import Challenge, ChallengeFile, ChallengeStatus
from app.models.submission import Solve
from app.models.team import Team
from app.schemas.challenge import (
    ActChallengeGroupResponse,
    ActProgressResponse,
    ChallengeFileResponse,
    ChallengeListResponse,
    ChallengeParticipantResponse,
)
from app.services import scoring
from app.services.challenge_files import get_challenge_file_storage
from app.services.platform_settings import submissions_are_open

router = APIRouter()


def _file_response(file: ChallengeFile) -> ChallengeFileResponse:
    return ChallengeFileResponse(
        id=file.id,
        challenge_id=file.challenge_id,
        display_name=file.display_name,
        original_filename=file.original_filename,
        extension=file.extension,
        content_type=file.content_type,
        size_bytes=file.size_bytes,
        is_active=file.is_active,
    )


def _challenge_response(
    challenge: Challenge,
    *,
    locked: bool,
    solved_ids: set[UUID],
    awarded_points: dict[UUID, int],
    team_fragments: dict[UUID, str],
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
        mission_brief="" if locked else challenge.mission_brief,
        story_context=None if locked else challenge.story_context,
        objectives=[] if locked else list(challenge.objectives_json or []),
        locked=locked,
        solved=challenge.id in solved_ids,
        awarded_points=awarded_points.get(challenge.id),
        team_fragment=None if locked else team_fragments.get(challenge.id),
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


def _load_accessible_challenge(db: Session, team: Team, challenge_id: UUID) -> Challenge:
    scoring.ensure_initial_act_unlock(db, team.id)
    db.commit()

    challenge = db.scalar(_published_challenges_query().where(Challenge.id == challenge_id))
    if challenge is None:
        raise APIError(404, NOT_FOUND, "Challenge not found.")
    if not scoring.team_can_access_act(db, team.id, challenge.act):
        raise APIError(422, LOCKED_CHALLENGE, "This challenge is not available yet.")
    return challenge


def _ensure_artifact_access_open(db: Session) -> None:
    if not submissions_are_open(db):
        raise APIError(403, SUBMISSIONS_CLOSED, "Challenge files are closed.")


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
    team_fragments = {
        challenge_id: derive_team_fragment(team.id, challenge_id)
        for challenge_id in solved_ids
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
                        team_fragments=team_fragments,
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
    challenge = _load_accessible_challenge(db, team, challenge_id)

    solved_ids = scoring.solved_challenge_ids(db, team.id)
    solve_row = db.execute(
        select(Solve.points_awarded).where(
            Solve.team_id == team.id,
            Solve.challenge_id == challenge.id,
        )
    ).first()
    return _challenge_response(
        challenge,
        locked=False,
        solved_ids=solved_ids,
        awarded_points={challenge.id: solve_row[0]} if solve_row is not None else {},
        team_fragments={
            challenge.id: derive_team_fragment(team.id, challenge.id)
        }
        if solve_row is not None
        else {},
    )


@router.get("/{challenge_id}/files", response_model=list[ChallengeFileResponse])
def list_challenge_files(
    challenge_id: UUID,
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> list[ChallengeFileResponse]:
    _load_accessible_challenge(db, team, challenge_id)
    _ensure_artifact_access_open(db)
    rows = db.scalars(
        select(ChallengeFile)
        .where(
            ChallengeFile.challenge_id == challenge_id,
            ChallengeFile.is_active.is_(True),
        )
        .order_by(ChallengeFile.created_at)
    ).all()
    return [_file_response(row) for row in rows]


@router.get("/{challenge_id}/files/{file_id}/download", response_class=FileResponse)
def download_challenge_file(
    challenge_id: UUID,
    file_id: UUID,
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> FileResponse:
    _load_accessible_challenge(db, team, challenge_id)
    _ensure_artifact_access_open(db)
    row = db.scalar(
        select(ChallengeFile).where(
            ChallengeFile.id == file_id,
            ChallengeFile.challenge_id == challenge_id,
            ChallengeFile.is_active.is_(True),
        )
    )
    if row is None:
        raise APIError(404, NOT_FOUND, "Challenge file not found.")

    try:
        path = get_challenge_file_storage().path_for_download(row.storage_key)
    except FileNotFoundError as exc:
        raise APIError(404, NOT_FOUND, "Challenge file not found.") from exc

    return FileResponse(
        path=path,
        media_type=row.content_type or "application/octet-stream",
        filename=row.original_filename,
    )
