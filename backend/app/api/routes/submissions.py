"""Participant flag submission (#13).

The handler is deliberately thin: it translates HTTP to a service call and the service's
domain error back to the documented error envelope. All logic lives in
app/services/submissions.py so the concurrency tests can drive it directly.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_team
from app.core.errors import (
    ALREADY_SOLVED,
    APIError,
    LOCKED_CHALLENGE,
    NOT_FOUND,
    RATE_LIMITED,
    SUBMISSIONS_CLOSED,
    TEAM_NOT_APPROVED,
)
from app.db.session import get_db
from app.models.team import Team
from app.schemas.submission import (
    FlagSubmissionRequest,
    FlagSubmissionResponse,
    UnlockedActResponse,
)
from app.services.submissions import SubmissionError, SubmissionResult, submit_flag

router = APIRouter()

# Statuses come from docs/api-contract.md section 3.
_ERROR_STATUS: dict[str, int] = {
    NOT_FOUND: status.HTTP_404_NOT_FOUND,
    # 422 for both of these is what the contract specifies. Written numerically because
    # the Starlette constant for 422 is deprecated.
    LOCKED_CHALLENGE: 422,
    ALREADY_SOLVED: 422,
    RATE_LIMITED: status.HTTP_429_TOO_MANY_REQUESTS,
    SUBMISSIONS_CLOSED: status.HTTP_403_FORBIDDEN,
    TEAM_NOT_APPROVED: status.HTTP_403_FORBIDDEN,
}


def _client_ip(request: Request) -> str | None:
    # Behind a proxy the immediate peer is the proxy, so prefer the first forwarded hop.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _to_api_error(error: SubmissionError) -> APIError:
    # APIError carries no headers, so the retry hint goes in field_errors rather than a
    # Retry-After header. Clients should read retry_after_seconds from the body.
    field_errors = None
    if error.retry_after_seconds is not None:
        field_errors = {"retry_after_seconds": str(error.retry_after_seconds)}
    return APIError(
        _ERROR_STATUS.get(error.code, status.HTTP_400_BAD_REQUEST),
        error.code,
        error.message,
        field_errors=field_errors,
    )


def _to_response(result: SubmissionResult) -> FlagSubmissionResponse:
    unlocked = None
    if result.next_act_unlocked is not None:
        act = result.next_act_unlocked
        unlocked = UnlockedActResponse(
            id=act.id,
            act_number=act.act_number,
            slug=act.slug,
            title=act.title,
        )
    return FlagSubmissionResponse(
        correct=result.correct,
        awarded_points=result.awarded_points,
        current_score=result.current_score,
        solved=result.solved,
        message=result.message,
        next_act_unlocked=unlocked,
    )


@router.post("/{challenge_id}/submissions", response_model=FlagSubmissionResponse)
def create_submission(
    challenge_id: UUID,
    payload: FlagSubmissionRequest,
    request: Request,
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> FlagSubmissionResponse:
    try:
        result = submit_flag(
            db,
            team,
            challenge_id,
            payload.flag,
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
    except SubmissionError as error:
        raise _to_api_error(error) from None

    return _to_response(result)
