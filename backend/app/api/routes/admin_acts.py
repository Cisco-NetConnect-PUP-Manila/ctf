"""Admin Act management.

Mounted with ``dependencies=[Depends(get_current_admin)]`` at the router level in main.py,
so no individual endpoint can forget the guard.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.errors import APIError
from app.db.session import get_db
from app.models.account import Account
from app.models.act import Act
from app.models.audit_log import AuditLog
from app.models.team import Team
from app.schemas.challenge import ActResponse, ActUpdateRequest
from app.services import scoring

router = APIRouter()


def _act_to_response(act: Act) -> ActResponse:
    return ActResponse(
        id=act.id,
        act_number=act.act_number,
        slug=act.slug,
        title=act.title,
        description=act.description,
        unlock_threshold_points=act.unlock_threshold_points,
        unlock_threshold_percent=act.unlock_threshold_percent,
        sort_order=act.sort_order,
        is_active=act.is_active,
    )


def _get_act_or_404(db: Session, act_id: UUID) -> Act:
    act = db.get(Act, act_id)
    if act is None:
        raise APIError(status.HTTP_404_NOT_FOUND, "ACT_NOT_FOUND", "Act not found.")
    return act


@router.get("/acts", response_model=list[ActResponse])
def list_acts(db: Session = Depends(get_db)) -> list[ActResponse]:
    acts = db.scalars(select(Act).order_by(Act.act_number)).all()
    return [_act_to_response(act) for act in acts]


@router.patch("/acts/{act_id}", response_model=ActResponse)
def update_act(
    act_id: UUID,
    payload: ActUpdateRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ActResponse:
    act = _get_act_or_404(db, act_id)

    changes: dict[str, object] = {}

    if payload.title is not None:
        act.title = payload.title
        changes["title"] = payload.title
    if payload.description is not None:
        act.description = payload.description
        changes["description"] = "updated"
    if payload.is_active is not None:
        act.is_active = payload.is_active
        changes["is_active"] = payload.is_active
    if payload.unlock_threshold_percent is not None:
        act.unlock_threshold_percent = payload.unlock_threshold_percent
        changes["unlock_threshold_percent"] = payload.unlock_threshold_percent

    # Clearing and setting the absolute threshold are separate operations: a plain None
    # is indistinguishable from an omitted field, and this column silently overrides the
    # percentage rule when set.
    if payload.clear_unlock_threshold_points:
        act.unlock_threshold_points = None
        changes["unlock_threshold_points"] = None
    elif payload.unlock_threshold_points is not None:
        act.unlock_threshold_points = payload.unlock_threshold_points
        changes["unlock_threshold_points"] = payload.unlock_threshold_points

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="act.updated",
            target_type="act",
            target_id=act.id,
            metadata_json={"act_number": act.act_number, "changes": changes},
        )
    )
    db.commit()
    db.refresh(act)
    return _act_to_response(act)


@router.post("/teams/{team_id}/recompute-progression", response_model=list[ActResponse])
def recompute_team_progression(
    team_id: UUID,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ActResponse]:
    """Re-evaluate a team's Act unlocks after editing points or thresholds.

    Exists because unlock evaluation otherwise only runs inside the submission
    transaction, and a GET must never write. Without this, an organizer lowering a
    threshold mid-event would leave already-qualified teams locked until they happen to
    submit again.

    Takes the same team lock as the submission path so it cannot race a live submission.
    """
    team = db.get(Team, team_id)
    if team is None:
        raise APIError(status.HTTP_404_NOT_FOUND, "TEAM_NOT_FOUND", "Team not found.")

    db.execute(select(Team.id).where(Team.id == team.id).with_for_update()).scalar_one()
    scoring.ensure_initial_act_unlock(db, team.id)
    newly_unlocked = scoring.evaluate_act_unlocks(db, team.id)

    for act in newly_unlocked:
        db.add(
            AuditLog(
                actor_account_id=current_admin.id,
                action="act.unlocked",
                target_type="act",
                target_id=act.id,
                metadata_json={"team_id": str(team.id), "reason": "admin_recompute"},
            )
        )
    db.commit()

    return [_act_to_response(act) for act in newly_unlocked]
