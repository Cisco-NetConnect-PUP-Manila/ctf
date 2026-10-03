from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.auth import RegisterRequest
from app.schemas.challenge import StrictRequest


class AdminTeamMemberResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    is_leader: bool


class AdminTeamResponse(BaseModel):
    id: UUID
    participant_type: str
    group_name: str
    status: str
    email: str
    member_count: int
    members: list[AdminTeamMemberResponse]
    approved_at: datetime | None
    rejected_at: datetime | None
    rejection_reason: str | None
    created_at: datetime


class TeamRejectRequest(StrictRequest):
    reason: str = Field(min_length=2, max_length=500)


class AdminParticipantCreateRequest(RegisterRequest):
    """Admin-created participant records bypass public registration intake."""


class AdminParticipantImportError(BaseModel):
    row: int
    message: str


class AdminParticipantImportResponse(BaseModel):
    created_count: int
    participants: list[AdminTeamResponse]
    errors: list[AdminParticipantImportError] = Field(default_factory=list)
