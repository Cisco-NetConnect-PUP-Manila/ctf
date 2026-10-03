from datetime import datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class TeamMemberCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class RegisterRequest(BaseModel):
    participant_type: Literal["solo", "team"] = "team"
    group_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    members: list[TeamMemberCreate] = Field(min_length=1, max_length=5)

    @field_validator("group_name")
    @classmethod
    def clean_group_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @model_validator(mode="after")
    def validate_participant_roster(self):
        member_count = len(self.members)
        if self.participant_type == "solo" and member_count != 1:
            raise ValueError("Solo participants must have exactly one member.")
        if self.participant_type == "team" and not 4 <= member_count <= 5:
            raise ValueError("Teams must have four or five members.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    mfa_code: str | None = Field(default=None, pattern=r"^[0-9]{6}$")


class AccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    status: str


class TeamMemberResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    is_leader: bool


class TeamResponse(BaseModel):
    id: UUID
    participant_type: str
    group_name: str
    status: str
    rejected_at: datetime | None
    rejection_reason: str | None
    members: list[TeamMemberResponse]


class MeResponse(BaseModel):
    account: AccountResponse
    team: TeamResponse | None
