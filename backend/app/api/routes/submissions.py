"""Participant flag submission (#13).

The handler is deliberately thin: it translates HTTP to a service call and the service's
domain error back to the documented error envelope. All logic lives in
app/services/submissions.py so the concurrency tests can drive it directly.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_team
from app.core.errors import APIError
from app.db.session import get_db
from app.models.team import Team
from app.schemas.submission import (
    FlagSubmissionRequest,
    FlagSubmissionResponse,
    UnlockedActResponse,
)
from app.services.submissions import SubmissionError, SubmissionResult, submit_flag

router = APIRouter()

# Maps a domain error code to its HTTP status. Codes are frozen in the #10 API contract.
_ERROR_STATUS: dict[str, int] = {
    "CHALLENGE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
    "CHALLENGE_LOCKED": status.HTTP_403_FORBIDDEN,
    "ALREADY_SOLVED": status.HTTP_409_CONFLICT,
    "RATE_LIMITED": status.HTTP_429_TOO_MANY_REQUESTS,
    "COMPETITION_CLOSED": status.HTTP_403_FORBIDDEN,
    "TEAM_NOT_APPROVED": status.HTTP_403_FORBIDDEN,
}


def _client_ip(request: Request) -> str | None:
    # Behind a proxy the immediate peer is the proxy, so prefer the first forwarded hop.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _to_api_error(error: SubmissionError) -> APIError:
    headers = None
    if error.retry_after_seconds is not None:
        headers = {"Retry-After": str(error.retry_after_seconds)}
    return APIError(
        _ERROR_STATUS.get(error.code, status.HTTP_400_BAD_REQUEST),
        error.code,
        error.message,
        headers=headers,
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
