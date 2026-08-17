from datetime import UTC, datetime

from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.errors import (
    ACCOUNT_DISABLED,
    APIError,
    AUTH_REQUIRED,
    FORBIDDEN,
    SESSION_EXPIRED,
    TEAM_NOT_APPROVED,
    TEAM_REQUIRED,
)
from app.core.security import hash_session_token
from app.db.session import get_db
from app.models.account import Account, AccountRole, AccountSession, AccountStatus
from app.models.audit_log import AuditLog
from app.models.team import Team, TeamStatus


def get_current_account(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    db: Session = Depends(get_db),
) -> Account:
    if not session_token:
        raise APIError(401, AUTH_REQUIRED, "Authentication required.")

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
    if account_session is None or account_session.revoked_at is not None:
        raise APIError(401, AUTH_REQUIRED, "Authentication required.")

    if account_session.expires_at <= now:
        account_session.revoked_at = now
        db.commit()
        raise APIError(401, SESSION_EXPIRED, "Your session has expired. Please log in again.")

    account = account_session.account
    if account.status != AccountStatus.ACTIVE.value:
        raise APIError(403, ACCOUNT_DISABLED, "Account is disabled.")

    account_session.last_seen_at = now
    db.commit()

    return account


def get_current_admin(
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Account:
    """Organizer/admin guard.

    Issue #9 (admin RBAC) owns hardening this -- admin session policy, scopes, step-up
    auth. The contract callers depend on is the NAME and this signature:
    ``Depends(get_current_admin) -> Account``, raising 403 FORBIDDEN. Internals are
    free to change.
    """
    if account.role != AccountRole.ADMIN.value:
        db.add(
            AuditLog(
                actor_account_id=account.id,
                action="admin.access_denied",
                target_type="admin_route",
                metadata_json={"reason": "wrong_role", "role": account.role},
            )
        )
        db.commit()
        raise APIError(403, FORBIDDEN, "Administrator access is required.")
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
        raise APIError(403, TEAM_REQUIRED, "This account is not linked to a team.")

    # Participant data is always approval-gated server-side. A frontend pending-page
    # redirect is not a security boundary, and a missing settings row must never turn
    # registration into immediate challenge/file/Intel access.
    if team.status != TeamStatus.APPROVED.value:
        raise APIError(
            403, TEAM_NOT_APPROVED, "Your team is not approved for the competition yet."
        )

    return team
