from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class TeamMemberCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def clean_full_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class RegisterRequest(BaseModel):
    group_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    members: list[TeamMemberCreate] = Field(min_length=4, max_length=5)

    @field_validator("group_name")
    @classmethod
    def clean_group_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


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
    group_name: str
    status: str
    members: list[TeamMemberResponse]


class MeResponse(BaseModel):
    account: AccountResponse
    team: TeamResponse | None
