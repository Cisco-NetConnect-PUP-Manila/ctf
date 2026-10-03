"""Persistent, serialized login limits. Never trust client-supplied forwarded IPs."""
import hashlib
import ipaddress
from datetime import UTC, datetime, timedelta
from math import ceil

from fastapi import Request
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import APIError
from app.models.auth_throttle import AuthThrottle


def client_address(request: Request) -> str:
    peer = request.client.host if request.client else "unknown"
    try:
        trusted = any(
            ipaddress.ip_address(peer) in ipaddress.ip_network(network.strip())
            for network in settings.trusted_proxy_cidrs.split(",") if network.strip()
        )
        if trusted:
            forwarded = request.headers.get("x-forwarded-for", "").split(",")[-1].strip()
            if forwarded:
                return str(ipaddress.ip_address(forwarded))
    except ValueError:
        pass
    return peer


def login_buckets(db: Session, email: str, request: Request) -> tuple[AuthThrottle, AuthThrottle]:
    now = datetime.now(UTC)
    keys = ["account:" + hashlib.sha256(email.encode()).hexdigest(),
            "ip:" + hashlib.sha256(client_address(request).encode()).hexdigest()]
    # Sorted advisory locks serialize concurrent first attempts too (before rows exist).
    for key in sorted(keys):
        lock = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big", signed=True)
        db.execute(text("select pg_advisory_xact_lock(:key)"), {"key": lock})
    db.execute(delete(AuthThrottle).where(AuthThrottle.window_started_at < now - timedelta(days=1)))
    rows = []
    for key in keys:
        row = db.get(AuthThrottle, key)
        if row is None:
            row = AuthThrottle(key=key, count=0, window_started_at=now)
            db.add(row)
        elif (now - row.window_started_at).total_seconds() >= 900:
            row.count = 0
            row.blocked_until = None
            row.window_started_at = now
        rows.append(row)
    waits = [ceil((row.blocked_until - now).total_seconds())
             for row in rows if row.blocked_until and row.blocked_until > now]
    if waits:
        db.commit()  # release locks; denied traffic never extends the cooldown
        raise APIError(429, "RATE_LIMITED", "Too many sign-in attempts. Please wait.",
                       field_errors={"retry_after_seconds": str(max(waits))},
                       headers={"Retry-After": str(max(waits))})
    # Count all work against the IP budget, including successful password checks.
    rows[1].count += 1
    if rows[1].count > settings.login_ip_limit:
        rows[1].blocked_until = now + timedelta(minutes=5)
        db.commit()
        raise APIError(429, "RATE_LIMITED", "Too many sign-in attempts. Please wait.",
                       field_errors={"retry_after_seconds": "300"}, headers={"Retry-After": "300"})
    return rows[0], rows[1]


def failed_login(bucket: AuthThrottle) -> bool:
    bucket.count += 1
    if bucket.count >= 5:
        seconds = min(900, 30 * 2 ** min(bucket.count - 5, 5))
        bucket.blocked_until = datetime.now(UTC) + timedelta(seconds=seconds)
        return True
    return False
