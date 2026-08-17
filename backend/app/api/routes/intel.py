from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_team
from app.core.errors import APIError, NOT_FOUND
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.intel import Hint, IntelRequest
from app.models.team import Team
from app.schemas.intel import HintParticipantResponse, IntelRequestCreate, IntelRequestResponse
from app.api.routes.challenges import _load_accessible_challenge

router = APIRouter()


def _hint(db: Session, challenge_id: UUID, hint_id: UUID) -> Hint:
    row = db.scalar(select(Hint).where(Hint.id == hint_id, Hint.challenge_id == challenge_id, Hint.is_active.is_(True)))
    if row is None:
        raise APIError(404, NOT_FOUND, "Intel is not available for this challenge.")
    return row


def _total(db: Session, team_id: UUID) -> int:
    value = db.scalar(select(func.coalesce(func.sum(IntelRequest.penalty_points), 0)).where(IntelRequest.team_id == team_id))
    return int(value or 0)


@router.get("/{challenge_id}/hints", response_model=list[HintParticipantResponse])
def list_hints(challenge_id: UUID, team: Team = Depends(get_current_team), db: Session = Depends(get_db)) -> list[HintParticipantResponse]:
    _load_accessible_challenge(db, team, challenge_id)
    rows = db.scalars(select(Hint).where(Hint.challenge_id == challenge_id, Hint.is_active.is_(True)).order_by(Hint.sort_order, Hint.created_at)).all()
    requests = {row.hint_id: row for row in db.scalars(select(IntelRequest).where(IntelRequest.team_id == team.id, IntelRequest.challenge_id == challenge_id)).all()}
    return [HintParticipantResponse(id=row.id, penalty_points=row.penalty_points, sort_order=row.sort_order, requested=row.id in requests, content=row.content if row.id in requests else None) for row in rows]


@router.post("/{challenge_id}/intel-requests", response_model=IntelRequestResponse)
def request_intel(challenge_id: UUID, payload: IntelRequestCreate, team: Team = Depends(get_current_team), db: Session = Depends(get_db)) -> IntelRequestResponse:
    _load_accessible_challenge(db, team, challenge_id)
    hint = _hint(db, challenge_id, payload.hint_id)
    db.execute(select(Team.id).where(Team.id == team.id).with_for_update()).scalar_one()
    existing = db.scalar(select(IntelRequest).where(IntelRequest.team_id == team.id, IntelRequest.hint_id == hint.id))
    if existing is not None:
        return IntelRequestResponse(hint=hint.content, penalty_points=existing.penalty_points, total_penalty=_total(db, team.id), already_requested=True)
    request = IntelRequest(team_id=team.id, challenge_id=challenge_id, hint_id=hint.id, penalty_points=hint.penalty_points)
    db.add(request)
    db.add(AuditLog(actor_account_id=team.account_id, action="intel.requested", target_type="hint", target_id=hint.id, metadata_json={"challenge_id": str(challenge_id), "penalty_points": hint.penalty_points}))
    db.commit()
    return IntelRequestResponse(hint=hint.content, penalty_points=hint.penalty_points, total_penalty=_total(db, team.id), already_requested=False)
