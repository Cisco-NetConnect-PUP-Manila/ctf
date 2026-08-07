"""Typed accessors over the platform_settings key/value table.

Organizer-controlled switches live here so they can be changed mid-event without a deploy.
Every getter is defensive about a missing row -- nothing seeds these eagerly.

None of these functions commit. Callers own the transaction.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.platform_setting import PlatformSetting

KEY_SUBMISSIONS_OPEN = "submissions_open"
KEY_REQUIRE_TEAM_APPROVAL = "require_team_approval"
KEY_SUBMISSION_RATE_LIMIT = "submission_rate_limit"


@dataclass(frozen=True)
class SubmissionRateLimitConfig:
    window_seconds: int = 60
    per_team_per_window: int = 20
    per_challenge_per_window: int = 5
    cooldown_seconds: int = 2


def get_setting(db: Session, key: str) -> Any | None:
    setting = db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))
    return None if setting is None else setting.value_json


def submissions_are_open(db: Session) -> bool:
    value = get_setting(db, KEY_SUBMISSIONS_OPEN)
    if value is None:
        return True
    return bool(value)


def team_approval_required(db: Session) -> bool:
    """Default false.

    The handoff lists "whether registration requires organizer approval" as a Pending
    Organizer Decision, so it must not be guessed. Encoding it as config keeps the
    end-to-end milestone testable before issue #9 ships an approval route.
    """
    value = get_setting(db, KEY_REQUIRE_TEAM_APPROVAL)
    if value is None:
        return False
    return bool(value)


def get_submission_rate_limit(db: Session) -> SubmissionRateLimitConfig:
    value = get_setting(db, KEY_SUBMISSION_RATE_LIMIT)
    defaults = SubmissionRateLimitConfig()
    if not isinstance(value, dict):
        return defaults

    def _positive_int(field: str, fallback: int) -> int:
        raw = value.get(field, fallback)
        if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
            return fallback
        return raw

    return SubmissionRateLimitConfig(
        window_seconds=_positive_int("window_seconds", defaults.window_seconds) or 1,
        per_team_per_window=_positive_int("per_team_per_window", defaults.per_team_per_window),
        per_challenge_per_window=_positive_int(
            "per_challenge_per_window", defaults.per_challenge_per_window
        ),
        cooldown_seconds=_positive_int("cooldown_seconds", defaults.cooldown_seconds),
    )
