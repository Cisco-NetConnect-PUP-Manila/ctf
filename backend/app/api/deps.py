from datetime import UTC, datetime

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.errors import APIError
from app.core.security import hash_session_token
from app.db.session import get_db
from app.models.account import Account, AccountRole, AccountSession, AccountStatus
from app.models.team import Team, TeamStatus
from app.services.platform_settings import team_approval_required


def get_current_account(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    db: Session = Depends(get_db),
) -> Account:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    token_hash = hash_session_token(session_token)
    stmt = (
        select(AccountSession)
        .options(
            joinedload(AccountSession.account)
            .selectinload(Account.team)
            .selectinload(Team.members)
        )
        .where(AccountSession.token_hash == token_hash)
    )
    account_session = db.scalar(stmt)

    now = datetime.now(UTC)
    if (
        account_session is None
        or account_session.revoked_at is not None
        or account_session.expires_at <= now
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")

    account = account_session.account
    if account.status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

    account_session.last_seen_at = now
    db.commit()

    return account


def get_current_admin(account: Account = Depends(get_current_account)) -> Account:
    """Organizer/admin guard.

    Issue #9 (admin RBAC) owns hardening this -- admin session policy, scopes, step-up
    auth. The contract callers depend on is the NAME and this signature:
    ``Depends(get_current_admin) -> Account``, raising 403 ADMIN_REQUIRED. Internals are
    free to change.
    """
    if account.role != AccountRole.ADMIN.value:
        raise APIError(
            status.HTTP_403_FORBIDDEN,
            "ADMIN_REQUIRED",
            "Administrator access is required.",
        )
    return account


def get_current_team(
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Team:
    """Participant guard covering handoff section 10 step 1.

    ``get_current_account`` already rejects disabled accounts. Whether organizer approval
    is required is an explicit Pending Organizer Decision in the handoff, so it is config
    (``require_team_approval``, default false) rather than a guess.
    """
    team = account.team
    if team is None:
        raise APIError(
            status.HTTP_403_FORBIDDEN,
            "TEAM_REQUIRED",
            "This account is not linked to a team.",
        )

    if team.status == TeamStatus.DISABLED.value:
        raise APIError(
            status.HTTP_403_FORBIDDEN,
            "TEAM_NOT_APPROVED",
            "This team has been disabled.",
        )

    if team_approval_required(db) and team.status != TeamStatus.APPROVED.value:
        raise APIError(
            status.HTTP_403_FORBIDDEN,
            "TEAM_NOT_APPROVED",
            "Your team is not approved for the competition yet.",
        )

    return team
