"""Typed accessors over the platform_settings key/value table.

Organizer-controlled switches live here so they can be changed mid-event without a deploy.
Every getter is defensive about a missing row -- nothing seeds these eagerly.

None of these functions commit. Callers own the transaction.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.platform_setting import PlatformSetting

KEY_SUBMISSIONS_OPEN = "submissions_open"
KEY_REQUIRE_TEAM_APPROVAL = "require_team_approval"
KEY_SUBMISSION_RATE_LIMIT = "submission_rate_limit"

# Organizer-facing competition controls (Issue #21). These are the keys and defaults from
# docs/database-normalization.md section 14 and the frozen contract's PATCH body
# {registration_open, competition_status, leaderboard_visible}.
KEY_REGISTRATION_OPEN = "registration_open"
KEY_COMPETITION_STATUS = "competition_status"
KEY_LEADERBOARD_VISIBLE = "leaderboard_visible"


class CompetitionStatus(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    PAUSED = "paused"
    ENDED = "ended"


DEFAULT_COMPETITION_STATUS = CompetitionStatus.UPCOMING.value
DEFAULT_LEADERBOARD_VISIBLE = False


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
    """Return the organizer preference, failing closed when the row is missing."""
    value = get_setting(db, KEY_REQUIRE_TEAM_APPROVAL)
    if value is None:
        return True
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


# --- Competition control settings (Issue #21) -----------------------------------------
#
# Reconciliation note (raise with the lead before freezing): flag submission gates on the
# separate ``submissions_open`` boolean above. ``competition_status`` here is the
# organizer-facing lifecycle; whether ``live`` implies ``submissions_open`` must be decided
# with the submissions owner. This module intentionally does not couple the two.


def registration_is_open(db: Session) -> bool:
    value = get_setting(db, KEY_REGISTRATION_OPEN)
    if value is None:
        return bool(settings.registration_open_by_default)
    return bool(value)


def competition_status(db: Session) -> str:
    value = get_setting(db, KEY_COMPETITION_STATUS)
    if not isinstance(value, str) or value not in CompetitionStatus._value2member_map_:
        return DEFAULT_COMPETITION_STATUS
    return value


def leaderboard_is_visible(db: Session) -> bool:
    value = get_setting(db, KEY_LEADERBOARD_VISIBLE)
    if value is None:
        return DEFAULT_LEADERBOARD_VISIBLE
    return bool(value)


def get_all_settings(db: Session) -> dict[str, Any]:
    """Return every competition-control setting, falling back to defaults."""
    return {
        KEY_REGISTRATION_OPEN: registration_is_open(db),
        KEY_SUBMISSIONS_OPEN: submissions_are_open(db),
        KEY_COMPETITION_STATUS: competition_status(db),
        KEY_LEADERBOARD_VISIBLE: leaderboard_is_visible(db),
    }


def _upsert(db: Session, key: str, value: Any, actor_account_id: Any) -> None:
    setting = db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))
    if setting is None:
        db.add(
            PlatformSetting(key=key, value_json=value, updated_by_account_id=actor_account_id)
        )
    else:
        setting.value_json = value
        setting.updated_by_account_id = actor_account_id
        setting.updated_at = datetime.now(UTC)


def update_settings(db: Session, changes: dict[str, Any], actor_account_id: Any) -> dict[str, Any]:
    """Apply a subset of settings, writing one audit log per changed key.

    ``changes`` must contain only known keys with already-validated values (the schema
    layer enforces types and the competition-status enum). Does not commit.
    """
    before = get_all_settings(db)

    for key, value in changes.items():
        _upsert(db, key, value, actor_account_id)
        db.add(
            AuditLog(
                actor_account_id=actor_account_id,
                action="platform_setting.changed",
                target_type="platform_setting",
                target_id=None,
                metadata_json={"key": key, "old_value": before.get(key), "new_value": value},
            )
        )

    db.flush()
    return get_all_settings(db)
