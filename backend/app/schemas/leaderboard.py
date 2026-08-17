from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LeaderboardRowResponse(BaseModel):
    rank: int
    team_id: UUID
    team_name: str
    investigation_score: int
    solved_count: int
    current_act: int
    intel_penalty: int
    last_solve_at: datetime | None


class LeaderboardResponse(BaseModel):
    generated_at: datetime
    current_team_rank: int | None
    rows: list[LeaderboardRowResponse]
