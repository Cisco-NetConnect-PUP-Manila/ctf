import hashlib
import hmac
from uuid import UUID

from app.core.config import settings

TEAM_FRAGMENT_PREFIX = "PCFRAG"
TEAM_FRAGMENT_HASH_PREFIX = "team-fragment-hmac-sha256$v1$"


def derive_team_fragment(team_id: UUID, challenge_id: UUID) -> str:
    """Stable per-team proof token for one solved challenge.

    This is an anti-sharing layer, not a challenge validator. The same solved challenge
    maps to different visible proof tokens for different teams.
    """

    message = f"{team_id}:{challenge_id}".encode("utf-8")
    digest = hmac.new(
        settings.team_fragment_secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()
    return f"{TEAM_FRAGMENT_PREFIX}-{digest[:6].upper()}-{digest[6:12].upper()}"


def hash_team_fragment(fragment: str) -> str:
    digest = hmac.new(
        settings.team_fragment_secret.encode("utf-8"),
        fragment.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return TEAM_FRAGMENT_HASH_PREFIX + digest


def preview_team_fragment(fragment: str) -> str:
    return f"{fragment[:12]}..."
