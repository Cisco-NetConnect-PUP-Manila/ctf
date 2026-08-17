from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_team
from app.core.errors import APIError, LEADERBOARD_HIDDEN
from app.db.session import get_db
from app.models.team import Team
from app.schemas.leaderboard import LeaderboardResponse, LeaderboardRowResponse
from app.services.leaderboard import calculate_leaderboard
from app.services.platform_settings import leaderboard_is_visible

router = APIRouter()


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    team: Team = Depends(get_current_team),
    db: Session = Depends(get_db),
) -> LeaderboardResponse:
    if not leaderboard_is_visible(db):
        raise APIError(403, LEADERBOARD_HIDDEN, "The leaderboard is currently hidden.")

    entries = calculate_leaderboard(db)
    current_team_rank = next(
        (entry.rank for entry in entries if entry.team_id == team.id),
        None,
    )
    return LeaderboardResponse(
        generated_at=datetime.now(UTC),
        current_team_rank=current_team_rank,
        rows=[LeaderboardRowResponse(**entry.__dict__) for entry in entries],
    )
