import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.challenge import Challenge


class ActUnlockReason(str, enum.Enum):
    INITIAL = "initial"
    SCORE_THRESHOLD = "score_threshold"
    ADMIN_OVERRIDE = "admin_override"


class Act(Base):
    """A chapter of the investigation. Terminology is Act everywhere, never Level."""

    __tablename__ = "acts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    act_number: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Absolute threshold wins when set; otherwise the percentage of the Act's reachable
    # points is used. Two columns because the handoff's prose rule (20 percent) and its
    # explicit table (500/700/700/700) contradict each other -- see
    # backend/docs/core-loop-design.md section 6.
    unlock_threshold_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unlock_threshold_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=20)

    sort_order: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    challenges: Mapped[list["Challenge"]] = relationship(
        "Challenge",
        back_populates="act",
        foreign_keys="Challenge.act_id",
    )

    __table_args__ = (
        CheckConstraint("act_number > 0", name="ck_acts_act_number_positive"),
        CheckConstraint(
            "unlock_threshold_percent between 0 and 100",
            name="ck_acts_threshold_percent_range",
        ),
        CheckConstraint(
            "unlock_threshold_points is null or unlock_threshold_points >= 0",
            name="ck_acts_threshold_points_non_negative",
        ),
    )


class ActUnlock(Base):
    """Per-team Act access record.

    Unlocks are never revoked automatically; nothing in the scoring path writes
    ``revoked_at``. Act-wide organizer locking is ``acts.is_active = false``.
    """

    __tablename__ = "act_unlocks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    act_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acts.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(32), nullable=False)

    # Audit snapshots: keep the unlock explainable after an admin edits points.
    source_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    threshold_points: Mapped[int | None] = mapped_column(Integer, nullable=True)

    unlocked_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )

    act: Mapped[Act] = relationship("Act", foreign_keys=[act_id])

    __table_args__ = (
        UniqueConstraint("team_id", "act_id", name="uq_act_unlocks_team_act"),
        CheckConstraint(
            "reason in ('initial', 'score_threshold', 'admin_override')",
            name="ck_act_unlocks_reason",
        ),
    )
