import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnnouncementStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Announcement(Base):
    """An organizer-authored platform message (#19).

    Lifecycle mirrors the challenge model: ``status`` is the source of truth and
    ``published_at`` / ``archived_at`` are audit snapshots of when each transition
    happened. Only ``status == 'published'`` rows are ever returned to participants,
    and that filter lives in the participant route -- never trust the timestamps alone.
    """

    __tablename__ = "announcements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=AnnouncementStatus.DRAFT.value,
    )

    # Author is kept for the admin audit trail. SET NULL so removing an admin account
    # never deletes the announcement history they published.
    created_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "status in ('draft', 'published', 'archived')",
            name="ck_announcements_status",
        ),
        # Participant feed is "published, newest first"; this index serves that ordering.
        Index("ix_announcements_status_published_at", "status", "published_at"),
    )
