from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IntelRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HintCreateRequest(IntelRequestBase):
    content: str = Field(min_length=1, max_length=4000)
    penalty_points: int = Field(ge=0)
    sort_order: int = Field(default=0, ge=0)


class HintUpdateRequest(IntelRequestBase):
    content: str | None = Field(default=None, min_length=1, max_length=4000)
    penalty_points: int | None = Field(default=None, ge=0)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class HintAdminResponse(BaseModel):
    id: UUID
    challenge_id: UUID
    content: str
    penalty_points: int
    sort_order: int
    is_active: bool


class HintParticipantResponse(BaseModel):
    id: UUID
    penalty_points: int
    sort_order: int
    requested: bool
    content: str | None


class IntelRequestCreate(IntelRequestBase):
    hint_id: UUID


class IntelRequestResponse(BaseModel):
    hint: str
    penalty_points: int
    total_penalty: int
    already_requested: bool
