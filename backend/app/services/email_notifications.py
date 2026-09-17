"""Transactional email notifications.

Email delivery is best-effort: registration and admin review actions must not fail
because a provider is temporarily unavailable. Providers are selected by EMAIL_PROVIDER.
"""

from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import dataclass
from email.utils import parseaddr

from app.core.config import settings
from app.models.team import Team

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    text: str


def _post_json(url: str, api_key: str, payload: dict, auth_scheme: str = "Bearer") -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"{auth_scheme} {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status >= 400:
            raise RuntimeError(f"Email provider returned HTTP {response.status}.")


def _plain_email(value: str) -> str:
    parsed = parseaddr(value)[1]
    return parsed or value


def send_email(message: EmailMessage) -> None:
    provider = settings.email_provider.lower()
    if provider == "none":
        return
    if provider == "console":
        logger.info("Email notification to %s: %s\n%s", message.to, message.subject, message.text)
        return
    if not settings.email_from:
        raise RuntimeError("EMAIL_FROM is required for email delivery.")

    if provider == "resend":
        if not settings.resend_api_key:
            raise RuntimeError("RESEND_API_KEY is required for Resend delivery.")
        _post_json(
            "https://api.resend.com/emails",
            settings.resend_api_key,
            {
                "from": settings.email_from,
                "to": [message.to],
                "subject": message.subject,
                "text": message.text,
            },
        )
        return

    if provider == "sendgrid":
        if not settings.sendgrid_api_key:
            raise RuntimeError("SENDGRID_API_KEY is required for SendGrid delivery.")
        _post_json(
            "https://api.sendgrid.com/v3/mail/send",
            settings.sendgrid_api_key,
            {
                "personalizations": [{"to": [{"email": message.to}]}],
                "from": {"email": _plain_email(settings.email_from)},
                "subject": message.subject,
                "content": [{"type": "text/plain", "value": message.text}],
            },
        )
        return

    raise RuntimeError(f"Unsupported EMAIL_PROVIDER: {settings.email_provider}")


def send_email_best_effort(message: EmailMessage) -> None:
    try:
        send_email(message)
    except Exception:
        logger.exception("Email notification failed for %s", message.to)


def registration_received_email(team: Team) -> EmailMessage:
    return EmailMessage(
        to=team.account.email,
        subject="Packet Capture registration received",
        text=(
            f"Hi {team.group_name},\n\n"
            "We received your Packet Capture team registration. "
            "Your team is pending organizer review. We will email you again once your "
            "registration status changes.\n\n"
            "Packet Capture Team"
        ),
    )


def team_approved_email(team: Team) -> EmailMessage:
    return EmailMessage(
        to=team.account.email,
        subject="Packet Capture registration approved",
        text=(
            f"Hi {team.group_name},\n\n"
            "Your Packet Capture registration has been approved. You may now log in "
            "to the participant platform with your team account.\n\n"
            "Packet Capture Team"
        ),
    )


def team_rejected_email(team: Team) -> EmailMessage:
    reason = f"\n\nReason: {team.rejection_reason}" if team.rejection_reason else ""
    return EmailMessage(
        to=team.account.email,
        subject="Packet Capture registration update",
        text=(
            f"Hi {team.group_name},\n\n"
            "Your Packet Capture registration was not approved at this time."
            f"{reason}\n\n"
            "Please contact the organizers if you need help updating your registration.\n\n"
            "Packet Capture Team"
        ),
    )
