from pydantic import BaseModel, model_validator

from app.services.platform_settings import CompetitionStatus


class PlatformSettingsResponse(BaseModel):
    registration_open: bool
    competition_status: CompetitionStatus
    leaderboard_visible: bool


class PlatformSettingsUpdate(BaseModel):
    """All fields optional so admins can PATCH any subset. At least one required."""

    registration_open: bool | None = None
    competition_status: CompetitionStatus | None = None
    leaderboard_visible: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PlatformSettingsUpdate":
        if self.registration_open is None and self.competition_status is None and self.leaderboard_visible is None:
            raise ValueError("Provide at least one setting to update.")
        return self

    def to_changes(self) -> dict:
        """Only the fields the caller actually set, as plain JSON-storable values."""
        changes: dict = {}
        if self.registration_open is not None:
            changes["registration_open"] = self.registration_open
        if self.competition_status is not None:
            changes["competition_status"] = self.competition_status.value
        if self.leaderboard_visible is not None:
            changes["leaderboard_visible"] = self.leaderboard_visible
        return changes
