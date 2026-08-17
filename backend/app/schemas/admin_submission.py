from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminSubmissionMonitorRow(BaseModel):
    challenge_id: UUID
    challenge_title: str
    team_id: UUID
    team_name: str
    solved_at: datetime | None
    correct_attempts: int
    incorrect_attempts: int
    first_attempt_at: datetime | None
    last_attempt_at: datetime | None
    first_correct_at: datetime | None
    seconds_to_solve: int | None
    shared_ip_hash_team_count: int
    shared_user_agent_hash_team_count: int
    rapid_solve: bool
    suspicious_notes: list[str]


class AdminSubmissionMonitorResponse(BaseModel):
    rows: list[AdminSubmissionMonitorRow]


class AdminLeaderboardRow(BaseModel):
    rank: int
    team_id: UUID
    team_name: str
    team_status: str
    member_count: int
    score: int
    current_act: int
    solves: int
    attempts: int
    incorrect_attempts: int
    last_solve_at: datetime | None


class AdminLeaderboardResponse(BaseModel):
    rows: list[AdminLeaderboardRow]
