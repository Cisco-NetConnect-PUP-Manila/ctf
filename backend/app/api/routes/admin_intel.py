from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.errors import APIError, NOT_FOUND
from app.db.session import get_db
from app.models.account import Account
from app.models.audit_log import AuditLog
from app.models.challenge import Challenge
from app.models.intel import Hint
from app.schemas.intel import HintAdminResponse, HintCreateRequest, HintUpdateRequest

router = APIRouter()


def _response(hint: Hint) -> HintAdminResponse:
    return HintAdminResponse(
        id=hint.id,
        challenge_id=hint.challenge_id,
        content=hint.content,
        penalty_points=hint.penalty_points,
        sort_order=hint.sort_order,
        is_active=hint.is_active,
    )


def _challenge(db: Session, challenge_id: UUID) -> Challenge:
    row = db.get(Challenge, challenge_id)
    if row is None:
        raise APIError(404, NOT_FOUND, "Challenge not found.")
    return row


@router.get("/challenges/{challenge_id}/hints", response_model=list[HintAdminResponse])
def list_hints(challenge_id: UUID, db: Session = Depends(get_db)) -> list[HintAdminResponse]:
    _challenge(db, challenge_id)
    rows = db.scalars(
        select(Hint).where(Hint.challenge_id == challenge_id).order_by(Hint.sort_order, Hint.created_at)
    ).all()
    return [_response(row) for row in rows]


@router.post(
    "/challenges/{challenge_id}/hints",
    response_model=HintAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hint(
    challenge_id: UUID,
    payload: HintCreateRequest,
    admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> HintAdminResponse:
    _challenge(db, challenge_id)
    hint = Hint(challenge_id=challenge_id, **payload.model_dump())
    db.add(hint)
    db.flush()
    db.add(AuditLog(actor_account_id=admin.id, action="hint.created", target_type="hint", target_id=hint.id, metadata_json={"challenge_id": str(challenge_id), "penalty_points": hint.penalty_points}))
    db.commit()
    db.refresh(hint)
    return _response(hint)


@router.patch("/challenges/{challenge_id}/hints/{hint_id}", response_model=HintAdminResponse)
def update_hint(
    challenge_id: UUID,
    hint_id: UUID,
    payload: HintUpdateRequest,
    admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> HintAdminResponse:
    hint = db.scalar(select(Hint).where(Hint.id == hint_id, Hint.challenge_id == challenge_id))
    if hint is None:
        raise APIError(404, NOT_FOUND, "Hint not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(hint, field, value)
    db.add(AuditLog(actor_account_id=admin.id, action="hint.updated", target_type="hint", target_id=hint.id, metadata_json={"fields": sorted(payload.model_dump(exclude_unset=True))}))
    db.commit()
    db.refresh(hint)
    return _response(hint)
