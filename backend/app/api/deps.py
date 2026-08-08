from datetime import UTC, datetime

from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import settings
from app.core.errors import ACCOUNT_DISABLED, APIError, AUTH_REQUIRED, SESSION_EXPIRED
from app.core.security import hash_session_token
from app.db.session import get_db
from app.models.account import Account, AccountSession, AccountStatus
from app.models.team import Team


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
