import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Hint(Base):
    __tablename__ = "hints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    penalty_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    challenge = relationship("Challenge", foreign_keys=[challenge_id])

    __table_args__ = (
        CheckConstraint("penalty_points >= 0", name="ck_hints_penalty_non_negative"),
        Index("ix_hints_challenge_sort", "challenge_id", "sort_order"),
    )


class IntelRequest(Base):
    __tablename__ = "intel_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hints.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # Snapshot the configured value so later admin edits do not rewrite score history.
    penalty_points: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    hint: Mapped[Hint] = relationship("Hint", foreign_keys=[hint_id])

    __table_args__ = (
        CheckConstraint("penalty_points >= 0", name="ck_intel_requests_penalty_non_negative"),
        UniqueConstraint("team_id", "hint_id", name="uq_intel_requests_team_hint"),
        Index("ix_intel_requests_team_challenge", "team_id", "challenge_id"),
    )
