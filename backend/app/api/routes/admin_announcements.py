"""Admin announcement management (#19).

Mounted with ``dependencies=[Depends(get_current_admin)]`` at the router level in
main.py, so no individual endpoint can forget the guard. Every mutation is audit logged,
matching the challenge/act admin modules.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.errors import APIError, NOT_FOUND
from app.db.session import get_db
from app.models.account import Account
from app.models.announcement import Announcement, AnnouncementStatus
from app.models.audit_log import AuditLog
from app.schemas.announcement import (
    AnnouncementAdminResponse,
    AnnouncementCreateRequest,
    AnnouncementStatusRequest,
    AnnouncementUpdateRequest,
)

router = APIRouter()


def _to_admin_response(row: Announcement) -> AnnouncementAdminResponse:
    return AnnouncementAdminResponse(
        id=row.id,
        title=row.title,
        body=row.body,
        status=row.status,
        created_by_account_id=row.created_by_account_id,
        published_at=row.published_at,
        archived_at=row.archived_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _load(db: Session, announcement_id: UUID) -> Announcement:
    row = db.get(Announcement, announcement_id)
    if row is None:
        raise APIError(status.HTTP_404_NOT_FOUND, NOT_FOUND, "Announcement not found.")
    return row


@router.get("/announcements", response_model=list[AnnouncementAdminResponse])
def list_announcements(db: Session = Depends(get_db)) -> list[AnnouncementAdminResponse]:
    """All announcements regardless of status, newest first. Admins see drafts too."""
    rows = db.scalars(
        select(Announcement).order_by(Announcement.created_at.desc())
    ).all()
    return [_to_admin_response(row) for row in rows]


@router.post(
    "/announcements",
    response_model=AnnouncementAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_announcement(
    payload: AnnouncementCreateRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AnnouncementAdminResponse:
    # Always starts as a draft; publishing is a deliberate, separately-audited step.
    row = Announcement(
        title=payload.title,
        body=payload.body,
        status=AnnouncementStatus.DRAFT.value,
        created_by_account_id=current_admin.id,
    )
    db.add(row)
    db.flush()

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="announcement.created",
            target_type="announcement",
            target_id=row.id,
            metadata_json={"title": row.title},
        )
    )
    db.commit()
    db.refresh(row)
    return _to_admin_response(row)


@router.patch("/announcements/{announcement_id}", response_model=AnnouncementAdminResponse)
def update_announcement(
    announcement_id: UUID,
    payload: AnnouncementUpdateRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AnnouncementAdminResponse:
    row = _load(db, announcement_id)

    if payload.title is not None:
        row.title = payload.title
    if payload.body is not None:
        row.body = payload.body

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="announcement.updated",
            target_type="announcement",
            target_id=row.id,
            metadata_json={"fields": sorted(payload.model_dump(exclude_unset=True).keys())},
        )
    )
    db.commit()
    db.refresh(row)
    return _to_admin_response(row)


@router.patch("/announcements/{announcement_id}/status", response_model=AnnouncementAdminResponse)
def set_announcement_status(
    announcement_id: UUID,
    payload: AnnouncementStatusRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AnnouncementAdminResponse:
    """Publish / archive / unpublish.

    ``published_at`` is set once on first publish and preserved on re-publish, so the
    participant feed keeps a stable "published on" date. Moving back to draft fully
    unpublishes (both timestamps cleared) so it disappears from the participant feed.
    """
    row = _load(db, announcement_id)
    new_status = payload.status
    now = datetime.now(UTC)

    if new_status is AnnouncementStatus.PUBLISHED:
        if row.published_at is None:
            row.published_at = now
        row.archived_at = None
    elif new_status is AnnouncementStatus.ARCHIVED:
        row.archived_at = now
    elif new_status is AnnouncementStatus.DRAFT:
        row.published_at = None
        row.archived_at = None

    row.status = new_status.value

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action=f"announcement.{new_status.value}",
            target_type="announcement",
            target_id=row.id,
            metadata_json={"title": row.title, "status": new_status.value},
        )
    )
    db.commit()
    db.refresh(row)
    return _to_admin_response(row)
