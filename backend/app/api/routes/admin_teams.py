"""Admin team approval and roster management."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import get_current_admin
from app.core.errors import APIError, NOT_FOUND, VALIDATION_ERROR
from app.db.session import get_db
from app.models.account import Account
from app.models.audit_log import AuditLog
from app.models.team import Team, TeamMember, TeamStatus
from app.schemas.admin_team import (
    AdminTeamMemberResponse,
    AdminTeamResponse,
    TeamRejectRequest,
)

router = APIRouter()


def _team_to_response(team: Team) -> AdminTeamResponse:
    members = sorted(team.members, key=lambda item: (not item.is_leader, item.full_name))
    return AdminTeamResponse(
        id=team.id,
        group_name=team.group_name,
        status=team.status,
        email=team.account.email,
        member_count=len(members),
        members=[
            AdminTeamMemberResponse(
                id=member.id,
                full_name=member.full_name,
                email=member.email,
                is_leader=member.is_leader,
            )
            for member in members
        ],
        approved_at=team.approved_at,
        rejected_at=team.rejected_at,
        rejection_reason=team.rejection_reason,
        created_at=team.created_at,
    )


def _load_team(db: Session, team_id: UUID) -> Team:
    team = db.scalar(
        select(Team)
        .options(joinedload(Team.account), selectinload(Team.members))
        .where(Team.id == team_id)
    )
    if team is None:
        raise APIError(404, NOT_FOUND, "Team not found.")
    return team


def _audit(db: Session, admin: Account, team: Team, action: str, metadata: dict) -> None:
    db.add(
        AuditLog(
            actor_account_id=admin.id,
            action=action,
            target_type="team",
            target_id=team.id,
            metadata_json=metadata,
        )
    )


@router.get("/teams", response_model=list[AdminTeamResponse])
def list_teams(db: Session = Depends(get_db)) -> list[AdminTeamResponse]:
    teams = db.scalars(
        select(Team)
        .options(joinedload(Team.account), selectinload(Team.members))
        .order_by(Team.created_at.desc(), Team.group_name)
    ).unique().all()
    return [_team_to_response(team) for team in teams]


@router.patch("/teams/{team_id}/approve", response_model=AdminTeamResponse)
def approve_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> AdminTeamResponse:
    team = _load_team(db, team_id)
    team.status = TeamStatus.APPROVED.value
    team.approved_by_account_id = admin.id
    team.approved_at = datetime.now(UTC)
    team.rejected_by_account_id = None
    team.rejected_at = None
    team.rejection_reason = None
    _audit(db, admin, team, "team.approved", {"group_name": team.group_name})
    db.commit()
    db.refresh(team)
    return _team_to_response(_load_team(db, team.id))


@router.patch("/teams/{team_id}/reject", response_model=AdminTeamResponse)
def reject_team(
    team_id: UUID,
    payload: TeamRejectRequest,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> AdminTeamResponse:
    team = _load_team(db, team_id)
    if team.status == TeamStatus.APPROVED.value:
        raise APIError(
            400,
            VALIDATION_ERROR,
            "Approved teams must be disabled instead of rejected.",
        )
    team.status = TeamStatus.REJECTED.value
    team.rejected_by_account_id = admin.id
    team.rejected_at = datetime.now(UTC)
    team.rejection_reason = payload.reason.strip()
    team.approved_by_account_id = None
    team.approved_at = None
    _audit(
        db,
        admin,
        team,
        "team.rejected",
        {"group_name": team.group_name, "reason": team.rejection_reason},
    )
    db.commit()
    return _team_to_response(_load_team(db, team.id))


@router.patch("/teams/{team_id}/disable", response_model=AdminTeamResponse)
def disable_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> AdminTeamResponse:
    team = _load_team(db, team_id)
    team.status = TeamStatus.DISABLED.value
    _audit(db, admin, team, "team.disabled", {"group_name": team.group_name})
    db.commit()
    return _team_to_response(_load_team(db, team.id))


@router.patch("/teams/{team_id}/reactivate", response_model=AdminTeamResponse)
def reactivate_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> AdminTeamResponse:
    team = _load_team(db, team_id)
    team.status = TeamStatus.PENDING.value
    team.rejection_reason = None
    team.rejected_by_account_id = None
    team.rejected_at = None
    _audit(db, admin, team, "team.reactivated", {"group_name": team.group_name})
    db.commit()
    return _team_to_response(_load_team(db, team.id))


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_registration(
    team_id: UUID,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> Response:
    team = _load_team(db, team_id)
    if team.status not in {TeamStatus.PENDING.value, TeamStatus.REJECTED.value}:
        raise APIError(
            400,
            VALIDATION_ERROR,
            "Only pending or rejected registrations can be deleted. Disable approved teams instead.",
        )

    account = team.account
    _audit(
        db,
        admin,
        team,
        "team.registration_deleted",
        {"group_name": team.group_name, "email": account.email, "status": team.status},
    )
    db.delete(team)
    try:
        # The team references its account, so flush the team deletion before removing
        # the now-orphaned login account and its sessions.
        db.flush()
        db.delete(account)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise APIError(
            409,
            VALIDATION_ERROR,
            "This registration has protected competition activity and cannot be deleted.",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
