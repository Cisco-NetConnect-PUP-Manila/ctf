"""Authenticator verification; caller must hold the account row lock."""
import base64
import hashlib
from datetime import UTC, datetime

import pyotp
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def cipher() -> Fernet:
    key = settings.mfa_encryption_key
    if not key:
        if settings.backend_env != "local":
            raise RuntimeError("MFA encryption key is missing.")
        # Local-only fallback; production always requires a separate random key.
        key = base64.urlsafe_b64encode(hashlib.sha256(("local-mfa:" + settings.flag_hash_secret).encode()).digest()).decode()
    return Fernet(key.encode())


def encrypt_secret(secret: str) -> str:
    return cipher().encrypt(secret.encode()).decode()


def verified_step(encrypted: str, code: str, last_step: int) -> int | None:
    try:
        totp = pyotp.TOTP(cipher().decrypt(encrypted.encode()).decode())
    except InvalidToken:
        return None  # Fail closed if the key changed; operator must recover enrollment.
    now = datetime.now(UTC)
    current = totp.timecode(now)
    for step in (current, current - 1, current + 1):
        if step > last_step and pyotp.utils.strings_equal(totp.at(step * totp.interval), code):
            return step
    return None
