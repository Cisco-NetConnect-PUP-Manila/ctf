"""Announcement schemas (#19).

Two response shapes on purpose:
- ``AnnouncementResponse`` is participant-facing and matches the frozen contract's
  Announcement model exactly (id, title, body, published_at) -- no status, no author,
  no draft/archive timestamps leak to participants.
- ``AnnouncementAdminResponse`` is the full organizer view used by /admin endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.announcement import AnnouncementStatus


class StrictRequest(BaseModel):
    """Reject unknown fields so a typo in an admin payload fails loudly."""

    model_config = ConfigDict(extra="forbid")


def _clean(value: str) -> str:
    return value.strip()


class AnnouncementCreateRequest(StrictRequest):
    title: str = Field(min_length=2, max_length=200)
    body: str = Field(min_length=1)

    @field_validator("title", "body")
    @classmethod
    def clean(cls, value: str) -> str:
        cleaned = _clean(value)
        if not cleaned:
            raise ValueError("This field cannot be blank.")
        return cleaned


class AnnouncementUpdateRequest(StrictRequest):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    body: str | None = Field(default=None, min_length=1)

    @field_validator("title", "body")
    @classmethod
    def clean(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = _clean(value)
        if not cleaned:
            raise ValueError("This field cannot be blank.")
        return cleaned


class AnnouncementStatusRequest(StrictRequest):
    status: AnnouncementStatus


class AnnouncementResponse(BaseModel):
    """Participant-facing shape -- matches api-contract.md Announcement exactly."""

    id: UUID
    title: str
    body: str
    published_at: datetime | None


class AnnouncementAdminResponse(BaseModel):
    id: UUID
    title: str
    body: str
    status: str
    created_by_account_id: UUID | None
    published_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
