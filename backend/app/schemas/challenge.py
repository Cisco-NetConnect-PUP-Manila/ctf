"""Challenge and Act schemas.

Response models never carry a flag, a flag hash, or a validator -- not even on admin
responses. The mapper functions in the route modules are the single chokepoint that
guarantees it, and a test sweeps every participant response for leakage.
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.flags import MAX_FLAG_LENGTH
from app.models.challenge import ChallengeStatus


class StrictRequest(BaseModel):
    """Request base that rejects unknown fields.

    Pydantic's default is to silently ignore them, which is a real footgun on an admin
    API that challenge authors drive by hand: posting ``category`` instead of
    ``category_id`` used to return 201 with the category silently unset, so a challenge
    could go live miscategorised with no error anywhere. Failing the request is far
    cheaper than discovering it mid-event.
    """

    model_config = ConfigDict(extra="forbid")


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


# --------------------------------------------------------------------------- acts


class ActResponse(BaseModel):
    id: UUID
    act_number: int
    slug: str
    title: str
    description: str | None
    unlock_threshold_points: int | None
    unlock_threshold_percent: int
    sort_order: int
    is_active: bool


class ActUpdateRequest(StrictRequest):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    unlock_threshold_points: int | None = Field(default=None, ge=0)
    unlock_threshold_percent: int | None = Field(default=None, ge=0, le=100)
    is_active: bool | None = None
    # Explicit opt-in to clear the absolute threshold and fall back to the percentage,
    # because a plain None is indistinguishable from "field omitted".
    clear_unlock_threshold_points: bool = False


class ActProgressResponse(BaseModel):
    """Participant-facing Act state."""

    id: UUID
    act_number: int
    slug: str
    title: str
    description: str | None
    unlocked: bool
    total_points: int
    earned_points: int
    required_points: int


# --------------------------------------------------------------------- lookup tables


class LookupResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    sort_order: int
    is_active: bool


# ---------------------------------------------------------------------- challenges


class ChallengeCreateRequest(StrictRequest):
    act_id: UUID
    title: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=160)
    mission_brief: str = Field(min_length=1)
    story_context: str | None = None
    objectives: list[str] = Field(default_factory=list)
    points: int = Field(ge=0)
    category_id: UUID | None = None
    difficulty_id: UUID | None = None
    story_fragment: str | None = Field(default=None, max_length=64)
    sort_order: int = 0
    is_visible: bool = True

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return _clean(value)

    @field_validator("slug")
    @classmethod
    def clean_slug(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("objectives")
    @classmethod
    def clean_objectives(cls, value: list[str]) -> list[str]:
        return [_clean(item) for item in value if item and item.strip()]


class ChallengeUpdateRequest(StrictRequest):
    act_id: UUID | None = None
    title: str | None = Field(default=None, min_length=2, max_length=200)
    slug: str | None = Field(default=None, min_length=2, max_length=160)
    mission_brief: str | None = Field(default=None, min_length=1)
    story_context: str | None = None
    objectives: list[str] | None = None
    points: int | None = Field(default=None, ge=0)
    category_id: UUID | None = None
    difficulty_id: UUID | None = None
    story_fragment: str | None = Field(default=None, max_length=64)
    sort_order: int | None = None
    is_visible: bool | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        return None if value is None else _clean(value)

    @field_validator("slug")
    @classmethod
    def clean_slug(cls, value: str | None) -> str | None:
        return None if value is None else value.strip().lower()

    @field_validator("objectives")
    @classmethod
    def clean_objectives(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return [_clean(item) for item in value if item and item.strip()]


class ChallengeAdminResponse(BaseModel):
    id: UUID
    act_id: UUID
    act_number: int
    title: str
    slug: str
    mission_brief: str
    story_context: str | None
    objectives: list[str]
    points: int
    status: str
    is_visible: bool
    story_fragment: str | None
    sort_order: int
    category: LookupResponse | None
    difficulty: LookupResponse | None
    # Count only. The hashes themselves never leave the database.
    active_flag_count: int


class ChallengeParticipantResponse(BaseModel):
    id: UUID
    act_id: UUID
    act_number: int
    title: str
    slug: str
    category: str | None
    difficulty: str | None
    points: int
    mission_brief: str
    story_context: str | None
    objectives: list[str]
    locked: bool
    solved: bool
    awarded_points: int | None


class ActChallengeGroupResponse(BaseModel):
    act: ActProgressResponse
    challenges: list[ChallengeParticipantResponse]


class ChallengeListResponse(BaseModel):
    acts: list[ActChallengeGroupResponse]
    current_act: int
    current_score: int


# --------------------------------------------------------------------------- flags


class ChallengeFlagCreateRequest(StrictRequest):
    value: str = Field(min_length=1, max_length=MAX_FLAG_LENGTH)
    label: str | None = Field(default=None, max_length=80)


class ChallengeFlagResponse(BaseModel):
    """Metadata only -- deliberately no hash and no value."""

    id: UUID
    challenge_id: UUID
    label: str | None
    validator_type: str
    is_active: bool


class ChallengePublishRequest(StrictRequest):
    status: ChallengeStatus
