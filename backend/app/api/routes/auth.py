from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_account
from app.core.config import settings
from app.core.errors import (
    ACCOUNT_DISABLED,
    APIError,
    EMAIL_TAKEN,
    GROUP_NAME_TAKEN,
    INTERNAL_ERROR,
    INVALID_CREDENTIALS,
    REGISTRATION_CLOSED,
    VALIDATION_ERROR,
)
from app.core.security import (
    hash_password,
    hash_session_token,
    new_session_token,
    normalize_email,
    verify_password,
)
from app.db.session import get_db
from app.models.account import Account, AccountRole, AccountSession, AccountStatus
from app.models.audit_log import AuditLog
from app.models.platform_setting import PlatformSetting
from app.models.team import Team, TeamMember, TeamStatus
from app.schemas.auth import (
    AccountResponse,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TeamMemberResponse,
    TeamResponse,
)

router = APIRouter()


def _registration_is_open(db: Session) -> bool:
    setting = db.scalar(
        select(PlatformSetting).where(PlatformSetting.key == "registration_open")
    )
    if setting is None:
        return settings.registration_open_by_default
    return bool(setting.value_json)


def _account_to_response(account: Account) -> AccountResponse:
    return AccountResponse(
        id=account.id,
        email=account.email,
        role=account.role,
        status=account.status,
    )


def _team_to_response(team: Team | None) -> TeamResponse | None:
    if team is None:
        return None
    return TeamResponse(
        id=team.id,
        group_name=team.group_name,
        status=team.status,
        rejected_at=team.rejected_at,
        rejection_reason=team.rejection_reason,
        members=[
            TeamMemberResponse(
                id=member.id,
                full_name=member.full_name,
                email=member.email,
                is_leader=member.is_leader,
            )
            for member in sorted(team.members, key=lambda item: (not item.is_leader, item.full_name))
        ],
    )


def _raise_for_integrity(exc: IntegrityError) -> None:
    orig = exc.orig
    constraint = ""
    if orig is not None and hasattr(orig, "diag") and orig.diag is not None:
        constraint = getattr(orig.diag, "constraint_name", "") or ""
    detail = str(orig or "").lower()
    if "email" in constraint.lower() or "accounts_email" in constraint or "email" in detail:
        raise APIError(409, EMAIL_TAKEN, "An account with this email already exists.")
    if "group_name" in constraint.lower() or "teams_group_name" in constraint or "group_name" in detail:
        raise APIError(409, GROUP_NAME_TAKEN, "A team with this group name already exists.")
    raise APIError(500, INTERNAL_ERROR, "A registration conflict occurred. Please try again.")


@router.post("/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
def register_team(payload: RegisterRequest, db: Session = Depends(get_db)) -> MeResponse:
    if not _registration_is_open(db):
        raise APIError(403, REGISTRATION_CLOSED, "Registration is currently closed.")

    team_email = normalize_email(payload.email)
    group_name = payload.group_name.strip()

    member_emails = [normalize_email(member.email) for member in payload.members]
    if len(set(member_emails)) != len(member_emails):
        raise APIError(
            400,
            VALIDATION_ERROR,
            "Team member emails must be unique within the team.",
            field_errors={"members": ["Team member emails must be unique within the team."]},
        )

    if team_email not in member_emails:
        raise APIError(
            400,
            VALIDATION_ERROR,
            "The team login email must belong to one of the listed team members.",
            field_errors={"email": ["The team login email must belong to one of the listed team members."]},
        )

    existing_account = db.scalar(select(Account).where(Account.email == team_email))
    if existing_account is not None:
        raise APIError(409, EMAIL_TAKEN, "An account with this email already exists.")

    existing_team = db.scalar(select(Team).where(Team.group_name == group_name))
    if existing_team is not None:
        raise APIError(409, GROUP_NAME_TAKEN, "A team with this group name already exists.")

    try:
        account = Account(
            email=team_email,
            password_hash=hash_password(payload.password),
            role=AccountRole.PARTICIPANT.value,
            status=AccountStatus.ACTIVE.value,
        )
        db.add(account)
        db.flush()

        team = Team(
            account_id=account.id,
            group_name=group_name,
            status=TeamStatus.PENDING.value,
        )
        db.add(team)
        db.flush()

        leader_member: TeamMember | None = None
        for member_payload in payload.members:
            member_email = normalize_email(member_payload.email)
            member = TeamMember(
                team_id=team.id,
                full_name=member_payload.full_name.strip(),
                email=member_email,
                is_leader=member_email == team_email,
            )
            db.add(member)
            if member.is_leader:
                leader_member = member

        db.flush()
        team.leader_member_id = leader_member.id if leader_member else None

        db.add(
            AuditLog(
                actor_account_id=account.id,
                action="team.registered",
                target_type="team",
                target_id=team.id,
                metadata_json={"group_name": team.group_name, "member_count": len(payload.members)},
            )
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        _raise_for_integrity(exc)

    db.refresh(account)
    account = db.scalar(
        select(Account)
        .options(selectinload(Account.team).selectinload(Team.members))
        .where(Account.id == account.id)
    )
    return MeResponse(account=_account_to_response(account), team=_team_to_response(account.team))


@router.post("/login", response_model=MeResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> MeResponse:
    email = normalize_email(payload.email)
    account = db.scalar(
        select(Account)
        .options(selectinload(Account.team).selectinload(Team.members))
        .where(Account.email == email)
    )

    if account is None or not verify_password(payload.password, account.password_hash):
        raise APIError(401, INVALID_CREDENTIALS, "Invalid email or password.")

    if account.status != AccountStatus.ACTIVE.value:
        raise APIError(403, ACCOUNT_DISABLED, "Account is disabled.")

    now = datetime.now(UTC)
    token = new_session_token()
    account_session = AccountSession(
        account_id=account.id,
        token_hash=hash_session_token(token),
        expires_at=now + timedelta(hours=settings.session_expire_hours),
    )
    account.last_login_at = now
    db.add(account_session)
    db.add(
        AuditLog(
            actor_account_id=account.id,
            action="account.logged_in",
            target_type="account",
            target_id=account.id,
            metadata_json={"role": account.role},
        )
    )
    db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_expire_hours * 60 * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
    )

    return MeResponse(account=_account_to_response(account), team=_team_to_response(account.team))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Response:
    now = datetime.now(UTC)
    sessions = db.scalars(
        select(AccountSession).where(
            AccountSession.account_id == current_account.id,
            AccountSession.revoked_at.is_(None),
        )
    ).all()
    for session in sessions:
        session.revoked_at = now

    db.add(
        AuditLog(
            actor_account_id=current_account.id,
            action="account.logged_out",
            target_type="account",
            target_id=current_account.id,
            metadata_json={},
        )
    )
    db.commit()
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(
        key=settings.session_cookie_name,
        samesite="lax",
        secure=settings.session_cookie_secure,
    )
    return response


@router.get("/me", response_model=MeResponse)
def me(current_account: Account = Depends(get_current_account)) -> MeResponse:
    return MeResponse(
        account=_account_to_response(current_account),
        team=_team_to_response(current_account.team),
    )
