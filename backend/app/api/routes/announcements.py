"""Participant announcements feed (#19).

Read-only. Returns only published announcements, newest first, in the shared pagination
envelope required by docs/api-contract.md section 6.5. Any authenticated account may
read the feed -- event updates should reach pending teams too, so this uses
``get_current_account`` rather than the approval-gated team guard.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_account
from app.db.session import get_db
from app.models.account import Account
from app.models.announcement import Announcement, AnnouncementStatus
from app.schemas.announcement import AnnouncementResponse
from app.schemas.common import Page

router = APIRouter()


@router.get("/announcements", response_model=Page[AnnouncementResponse])
def list_published_announcements(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Page[AnnouncementResponse]:
    published = Announcement.status == AnnouncementStatus.PUBLISHED.value

    total = int(
        db.scalar(select(func.count()).select_from(Announcement).where(published)) or 0
    )

    rows = db.scalars(
        select(Announcement)
        .where(published)
        # Newest published first; created_at breaks ties for items published together.
        .order_by(Announcement.published_at.desc(), Announcement.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        AnnouncementResponse(
            id=row.id,
            title=row.title,
            body=row.body,
            published_at=row.published_at,
        )
        for row in rows
    ]

    return Page[AnnouncementResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=page * page_size < total,
    )
