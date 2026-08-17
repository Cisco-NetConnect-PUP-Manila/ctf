from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.api.deps import get_current_team
from app.core.errors import APIError, NOT_FOUND, RATE_LIMITED, SUBMISSIONS_CLOSED
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.intel import Hint, IntelRequest
from app.models.team import Team
from app.schemas.intel import HintParticipantResponse, IntelRequestCreate, IntelRequestResponse
from app.api.routes.challenges import _load_accessible_challenge
from app.services.platform_settings import submissions_are_open

router = APIRouter()

INTEL_REQUEST_LIMIT = 20
INTEL_REQUEST_WINDOW_SECONDS = 60
INTEL_LOCK_TIMEOUT = "5s"


def _hint(db: Session, challenge_id: UUID, hint_id: UUID) -> Hint:
    row = db.scalar(select(Hint).where(Hint.id == hint_id, Hint.challenge_id == challenge_id, Hint.is_active.is_(True)))
    if row is None:
        raise APIError(404, NOT_FOUND, "Intel is not available for this challenge.")
    return row


def _total(db: Session, team_id: UUID) -> int:
    value = db.scalar(select(func.coalesce(func.sum(IntelRequest.penalty_points), 0)).where(IntelRequest.team_id == team_id))
    return int(value or 0)


def _ensure_intel_access_open(db: Session) -> None:
    if not submissions_are_open(db):
        raise APIError(403, SUBMISSIONS_CLOSED, "Intel Requests are closed.")


def _enforce_intel_rate_limit(db: Session, account_id: UUID) -> None:
    since = datetime.now(UTC) - timedelta(seconds=INTEL_REQUEST_WINDOW_SECONDS)
    count = db.scalar(
        select(func.count())
        .select_from(AuditLog)
        .where(
            AuditLog.actor_account_id == account_id,
            AuditLog.action == "intel.requested",
            AuditLog.created_at > since,
        )
    )
    if int(count or 0) >= INTEL_REQUEST_LIMIT:
        raise APIError(
            429,
            RATE_LIMITED,
            "Too many Intel Requests. Please wait before trying again.",
            field_errors={"retry_after_seconds": str(INTEL_REQUEST_WINDOW_SECONDS)},
        )


def _audit_request(db: Session, team: Team, hint: Hint, *, repeated: bool) -> None:
    db.add(
        AuditLog(
            actor_account_id=team.account_id,
            action="intel.requested",
            target_type="hint",
            target_id=hint.id,
            metadata_json={
                "challenge_id": str(hint.challenge_id),
                "penalty_points": hint.penalty_points,
                "already_requested": repeated,
            },
        )
    )


@router.get("/{challenge_id}/hints", response_model=list[HintParticipantResponse])
def list_hints(challenge_id: UUID, team: Team = Depends(get_current_team), db: Session = Depends(get_db)) -> list[HintParticipantResponse]:
    _load_accessible_challenge(db, team, challenge_id)
    _ensure_intel_access_open(db)
    requests = {row.hint_id: row for row in db.scalars(select(IntelRequest).where(IntelRequest.team_id == team.id, IntelRequest.challenge_id == challenge_id)).all()}
    rows = db.scalars(
        select(Hint)
        .where(
            Hint.challenge_id == challenge_id,
            or_(Hint.is_active.is_(True), Hint.id.in_(requests)),
        )
        .order_by(Hint.sort_order, Hint.created_at)
    ).all()
    return [
        HintParticipantResponse(
            id=row.id,
            penalty_points=(requests[row.id].penalty_points if row.id in requests else row.penalty_points),
            sort_order=row.sort_order,
            requested=row.id in requests,
            content=row.content if row.id in requests else None,
        )
        for row in rows
    ]


@router.post("/{challenge_id}/intel-requests", response_model=IntelRequestResponse)
def request_intel(challenge_id: UUID, payload: IntelRequestCreate, team: Team = Depends(get_current_team), db: Session = Depends(get_db)) -> IntelRequestResponse:
    _load_accessible_challenge(db, team, challenge_id)
    _ensure_intel_access_open(db)
    hint = _hint(db, challenge_id, payload.hint_id)
    db.execute(text(f"set local lock_timeout = '{INTEL_LOCK_TIMEOUT}'"))
    db.execute(select(Team.id).where(Team.id == team.id).with_for_update()).scalar_one()
    _enforce_intel_rate_limit(db, team.account_id)
    existing = db.scalar(select(IntelRequest).where(IntelRequest.team_id == team.id, IntelRequest.hint_id == hint.id))
    if existing is not None:
        _audit_request(db, team, hint, repeated=True)
        db.commit()
        return IntelRequestResponse(hint=hint.content, penalty_points=existing.penalty_points, total_penalty=_total(db, team.id), already_requested=True)
    request = IntelRequest(team_id=team.id, challenge_id=challenge_id, hint_id=hint.id, penalty_points=hint.penalty_points)
    db.add(request)
    _audit_request(db, team, hint, repeated=False)
    db.commit()
    return IntelRequestResponse(hint=hint.content, penalty_points=hint.penalty_points, total_penalty=_total(db, team.id), already_requested=False)
