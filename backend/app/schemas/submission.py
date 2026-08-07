from uuid import UUID

from pydantic import BaseModel, Field

from app.core.flags import MAX_FLAG_LENGTH


class FlagSubmissionRequest(BaseModel):
    # No validator strips or rewrites the value here -- normalization is the validator's
    # job (trim only, per docs/database-normalization.md section 7) and doing it twice in
    # two places is how normalization rules silently diverge.
    flag: str = Field(min_length=1, max_length=MAX_FLAG_LENGTH)


class UnlockedActResponse(BaseModel):
    id: UUID
    act_number: int
    slug: str
    title: str


class FlagSubmissionResponse(BaseModel):
    """Frozen shape for the #10 API contract."""

    correct: bool
    awarded_points: int
    current_score: int
    solved: bool
    message: str
    next_act_unlocked: UnlockedActResponse | None = None
