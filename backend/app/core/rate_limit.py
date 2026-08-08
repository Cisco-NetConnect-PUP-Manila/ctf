"""DB-backed rate limiting. No Redis in the stack.

Why a database counter is exact here, when normally it would only be approximate:
under READ COMMITTED a COUNT cannot see concurrent uncommitted inserts, so N simultaneous
requests can all read the same pre-burst count and all pass. But this limiter runs *after*
``SELECT ... FROM teams FOR UPDATE`` in the submission path, so every prior submission by
that team is already committed and visible. The limit is per-team and only that team can
race its own counter, so the window is exact for the dimension that matters.

Cross-team flooding is a reverse-proxy/WAF concern, not this limiter's job.
"""

from datetime import UTC, datetime, timedelta
from math import ceil
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.services.platform_settings import SubmissionRateLimitConfig, get_submission_rate_limit
from app.models.submission import Submission


class RateLimited(Exception):
    """Raised when a team exceeds its submission window."""

    def __init__(self, retry_after_seconds: int, reason: str) -> None:
        self.retry_after_seconds = max(1, retry_after_seconds)
        self.reason = reason
        super().__init__(f"Rate limited ({reason}); retry after {self.retry_after_seconds}s")


def count_in_window(
    db: Session,
    team_id: UUID,
    window_seconds: int,
    challenge_id: UUID | None = None,
) -> int:
    """Generic sliding-window counter.

    Exposed separately so #9 can reuse it for the login rate limit mandated by handoff
    section 15, rather than inventing a second mechanism.
    """
    since = datetime.now(UTC) - timedelta(seconds=window_seconds)
    stmt = select(func.count()).select_from(Submission).where(
        Submission.team_id == team_id,
        Submission.submitted_at > since,
    )
    if challenge_id is not None:
        stmt = stmt.where(Submission.challenge_id == challenge_id)
    return int(db.scalar(stmt) or 0)


def enforce_submission_rate_limit(
    db: Session,
    team_id: UUID,
    challenge_id: UUID,
    config: SubmissionRateLimitConfig | None = None,
) -> None:
    """Raise RateLimited if the team has exceeded any configured limit.

    Rejected requests deliberately create no ``submissions`` row: counting rejections
    would let a spammer extend their own lockout indefinitely and inflate the table
    without bound. Callers audit-log the rejection instead.
    """
    cfg = config if config is not None else get_submission_rate_limit(db)
    now = datetime.now(UTC)
    window_start = now - timedelta(seconds=cfg.window_seconds)

    # One indexed round trip for all three checks.
    team_count, challenge_count, last_at = db.execute(
        select(
            func.count().filter(Submission.submitted_at > window_start),
            func.count().filter(
                Submission.submitted_at > window_start,
                Submission.challenge_id == challenge_id,
            ),
            func.max(Submission.submitted_at),
        ).where(Submission.team_id == team_id)
    ).one()

    if cfg.cooldown_seconds and last_at is not None:
        elapsed = (now - last_at).total_seconds()
        if elapsed < cfg.cooldown_seconds:
            raise RateLimited(ceil(cfg.cooldown_seconds - elapsed), "cooldown")

    if cfg.per_challenge_per_window and challenge_count >= cfg.per_challenge_per_window:
        raise RateLimited(cfg.window_seconds, "per_challenge")

    if cfg.per_team_per_window and team_count >= cfg.per_team_per_window:
        raise RateLimited(cfg.window_seconds, "per_team")
