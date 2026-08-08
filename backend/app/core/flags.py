"""Flag validator hashing.

HMAC-SHA256 keyed with a server-side pepper (FLAG_HASH_SECRET), not Argon2 and not plain
SHA-256:

* Argon2 costs ~50-100ms per verify and the submission path verifies against every active
  validator for a challenge *while holding the team row lock*. That is a reachable CPU DoS
  and it makes the concurrency tests slow and flaky.
* Plain SHA-256 is near useless here. Flags are low-entropy, human-authored, and follow the
  published format PacketCapture{NAME}, so a database dump falls to a wordlist in seconds.

HMAC costs microseconds and makes a database dump alone worthless -- recovering flags needs
the dump *and* the application secret. That is the realistic leak (a pg_dump, a backup file,
a psql screenshot).

Never log a raw submitted value or its normalized form, at any level.
"""

import hashlib
import hmac

from app.core.config import settings

FLAG_HASH_PREFIX = "hmac-sha256$v1$"

# Reject oversized submissions before doing any hashing work.
MAX_FLAG_LENGTH = 512


def normalize_flag(raw: str) -> str:
    """Apply the only organizer-approved normalization.

    docs/database-normalization.md section 7: trim leading/trailing spaces before
    validation. Do NOT lowercase. Do NOT remove inner spaces. Do NOT change punctuation.
    Flags are case-sensitive per the competition rules.
    """
    return raw.strip()


def hash_flag(raw: str) -> str:
    digest = hmac.new(
        settings.flag_hash_secret.encode("utf-8"),
        normalize_flag(raw).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return FLAG_HASH_PREFIX + digest


def flags_match(candidate_hash: str, stored_hash: str) -> bool:
    return hmac.compare_digest(candidate_hash, stored_hash)


def hash_submitted_value(raw: str) -> str:
    """Traceability hash for the submissions log. Not a validator.

    Unkeyed on purpose: this only needs to group identical attempts for duplicate analysis,
    and it must stay comparable if FLAG_HASH_SECRET is ever rotated.
    """
    return hashlib.sha256(normalize_flag(raw).encode("utf-8")).hexdigest()


def incorrect_preview(raw: str) -> str | None:
    """Short preview of an INCORRECT submission for admin logs.

    Callers must pass None for correct submissions -- those are the only values guaranteed
    to be a real flag, and an admin log screenshot is the likeliest leak path.
    """
    trimmed = normalize_flag(raw)
    if not trimmed:
        return None
    if len(trimmed) <= 8:
        return trimmed
    return trimmed[:8] + "..."
