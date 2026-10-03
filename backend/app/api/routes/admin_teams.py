"""Admin participant intake, approval, and roster management."""

import csv
import io
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.deps import get_current_admin
from app.core.errors import (
    APIError,
    EMAIL_TAKEN,
    GROUP_NAME_TAKEN,
    INTERNAL_ERROR,
    NOT_FOUND,
    VALIDATION_ERROR,
)
from app.core.security import hash_password, normalize_email
from app.db.session import get_db
from app.models.account import Account
from app.models.audit_log import AuditLog
from app.models.team import Team, TeamMember, TeamStatus
from app.schemas.admin_team import (
    AdminParticipantCreateRequest,
    AdminParticipantImportError,
    AdminParticipantImportResponse,
    AdminTeamMemberResponse,
    AdminTeamResponse,
    TeamRejectRequest,
)
from app.services.email_notifications import (
    send_email_best_effort,
    team_approved_email,
    team_rejected_email,
)

router = APIRouter()

MAX_IMPORT_BYTES = 2 * 1024 * 1024
MAX_IMPORT_ROWS = 500
CSV_REQUIRED_HEADERS = {
    "participant_type",
    "group_name",
    "email",
    "password",
    "member_1_name",
    "member_1_email",
}
CSV_MEMBER_HEADERS = [
    (f"member_{index}_name", f"member_{index}_email")
    for index in range(1, 6)
]


def _team_to_response(team: Team) -> AdminTeamResponse:
    members = sorted(team.members, key=lambda item: (not item.is_leader, item.full_name))
    return AdminTeamResponse(
        id=team.id,
        participant_type=team.participant_type,
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


def _validate_payload_invariants(payload: AdminParticipantCreateRequest) -> None:
    member_emails = [normalize_email(str(member.email)) for member in payload.members]
    if len(set(member_emails)) != len(member_emails):
        raise APIError(
            400,
            VALIDATION_ERROR,
            "Participant member emails must be unique within the record.",
            field_errors={"members": ["Participant member emails must be unique within the record."]},
        )
    if normalize_email(str(payload.email)) not in member_emails:
        raise APIError(
            400,
            VALIDATION_ERROR,
            "The login email must belong to one of the listed participants.",
            field_errors={"email": ["The login email must belong to one of the listed participants."]},
        )


def _check_duplicates(
    db: Session,
    payloads: list[AdminParticipantCreateRequest],
) -> None:
    emails = [normalize_email(str(payload.email)) for payload in payloads]
    group_names = [payload.group_name for payload in payloads]
    existing_emails = set(db.scalars(select(Account.email).where(Account.email.in_(emails))).all())
    existing_group_names = set(
        db.scalars(select(Team.group_name).where(Team.group_name.in_(group_names))).all()
    )

    seen_emails: set[str] = set()
    seen_group_names: set[str] = set()
    for payload in payloads:
        email = normalize_email(str(payload.email))
        if email in existing_emails or email in seen_emails:
            raise APIError(409, EMAIL_TAKEN, f"An account with email {email} already exists.")
        if payload.group_name in existing_group_names or payload.group_name in seen_group_names:
            raise APIError(
                409,
                GROUP_NAME_TAKEN,
                f'A participant record named "{payload.group_name}" already exists.',
            )
        seen_emails.add(email)
        seen_group_names.add(payload.group_name)


def _create_pending_participant(
    db: Session,
    admin: Account,
    payload: AdminParticipantCreateRequest,
    *,
    source: str,
) -> Team:
    account = Account(
        email=normalize_email(str(payload.email)),
        password_hash=hash_password(payload.password),
    )
    db.add(account)
    db.flush()

    team = Team(
        account_id=account.id,
        group_name=payload.group_name,
        participant_type=payload.participant_type,
        status=TeamStatus.PENDING.value,
    )
    db.add(team)
    db.flush()

    leader_member: TeamMember | None = None
    login_email = normalize_email(str(payload.email))
    for member_payload in payload.members:
        member_email = normalize_email(str(member_payload.email))
        member = TeamMember(
            team_id=team.id,
            full_name=member_payload.full_name,
            email=member_email,
            is_leader=member_email == login_email,
        )
        db.add(member)
        if member.is_leader:
            leader_member = member

    db.flush()
    team.leader_member_id = leader_member.id if leader_member else None
    _audit(
        db,
        admin,
        team,
        "participant.created",
        {
            "source": source,
            "group_name": team.group_name,
            "participant_type": team.participant_type,
            "member_count": len(payload.members),
        },
    )
    return team


def _validation_message(exc: ValidationError) -> str:
    return "; ".join(
        str(error.get("msg", "Invalid value.")).replace("Value error, ", "")
        for error in exc.errors()
    )


def _csv_payloads(raw: bytes) -> tuple[list[AdminParticipantCreateRequest], list[AdminParticipantImportError]]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], [AdminParticipantImportError(row=1, message="CSV must be UTF-8 encoded.")]

    reader = csv.DictReader(io.StringIO(text))
    headers = {header.strip().lower() for header in (reader.fieldnames or []) if header}
    missing_headers = sorted(CSV_REQUIRED_HEADERS - headers)
    if missing_headers:
        return [], [
            AdminParticipantImportError(
                row=1,
                message=f"Missing required column(s): {', '.join(missing_headers)}.",
            )
        ]

    payloads: list[AdminParticipantCreateRequest] = []
    errors: list[AdminParticipantImportError] = []
    rows = list(reader)
    if len(rows) > MAX_IMPORT_ROWS:
        return [], [
            AdminParticipantImportError(
                row=1,
                message=f"CSV cannot contain more than {MAX_IMPORT_ROWS} participant records.",
            )
        ]

    for row_number, raw_row in enumerate(rows, start=2):
        row = {
            str(key).strip().lower(): (value or "").strip()
            for key, value in raw_row.items()
            if key is not None
        }
        members = []
        for name_header, email_header in CSV_MEMBER_HEADERS:
            name = row.get(name_header, "")
            email = row.get(email_header, "")
            if not name and not email:
                continue
            if not name or not email:
                errors.append(
                    AdminParticipantImportError(
                        row=row_number,
                        message=f"{name_header} and {email_header} must be provided together.",
                    )
                )
                continue
            members.append({"full_name": name, "email": email})

        try:
            payload = AdminParticipantCreateRequest.model_validate(
                {
                    "participant_type": row.get("participant_type", "").lower(),
                    "group_name": row.get("group_name", ""),
                    "email": row.get("email", ""),
                    "password": row.get("password", ""),
                    "members": members,
                }
            )
            _validate_payload_invariants(payload)
            payloads.append(payload)
        except ValidationError as exc:
            errors.append(
                AdminParticipantImportError(row=row_number, message=_validation_message(exc))
            )
        except APIError as exc:
            errors.append(AdminParticipantImportError(row=row_number, message=exc.message))

    return payloads, errors


@router.get("/teams", response_model=list[AdminTeamResponse])
def list_teams(db: Session = Depends(get_db)) -> list[AdminTeamResponse]:
    teams = db.scalars(
        select(Team)
        .options(joinedload(Team.account), selectinload(Team.members))
        .order_by(Team.created_at.desc(), Team.group_name)
    ).unique().all()
    return [_team_to_response(team) for team in teams]


@router.post("/teams", response_model=AdminTeamResponse, status_code=status.HTTP_201_CREATED)
def create_participant(
    payload: AdminParticipantCreateRequest,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> AdminTeamResponse:
    """Create a pending participant without opening public registration intake."""
    _validate_payload_invariants(payload)
    _check_duplicates(db, [payload])

    try:
        team = _create_pending_participant(db, admin, payload, source="admin_manual")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise APIError(
            409,
            INTERNAL_ERROR,
            "The participant could not be created because the record changed. Please retry.",
        ) from exc

    team = _load_team(db, team.id)
    send_email_best_effort(registration_received_email(team))
    return _team_to_response(team)


@router.post("/teams/import", response_model=AdminParticipantImportResponse)
async def import_participants(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> AdminParticipantImportResponse:
    """Atomically create pending participants from the admin CSV template."""
    raw = await file.read(MAX_IMPORT_BYTES + 1)
    if len(raw) > MAX_IMPORT_BYTES:
        raise APIError(
            413,
            VALIDATION_ERROR,
            f"CSV files must be smaller than {MAX_IMPORT_BYTES // (1024 * 1024)} MB.",
        )

    payloads, errors = _csv_payloads(raw)
    if errors:
        raise APIError(
            400,
            VALIDATION_ERROR,
            "CSV validation failed. No participants were imported.",
            field_errors={f"row_{error.row}": [error.message] for error in errors},
        )

    if not payloads:
        raise APIError(
            400,
            VALIDATION_ERROR,
            "The CSV does not contain any participant records.",
        )

    _check_duplicates(db, payloads)
    created: list[Team] = []
    try:
        for payload in payloads:
            created.append(
                _create_pending_participant(db, admin, payload, source="admin_csv")
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise APIError(
            409,
            INTERNAL_ERROR,
            "The CSV could not be imported because a record changed. No participants were imported.",
        ) from exc

    participants = [_load_team(db, team.id) for team in created]
    for team in participants:
        send_email_best_effort(registration_received_email(team))

    return AdminParticipantImportResponse(
        created_count=len(participants),
        participants=[_team_to_response(team) for team in participants],
    )


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
    team = _load_team(db, team.id)
    send_email_best_effort(team_approved_email(team))
    return _team_to_response(team)


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
    team = _load_team(db, team.id)
    send_email_best_effort(team_rejected_email(team))
    return _team_to_response(team)


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
