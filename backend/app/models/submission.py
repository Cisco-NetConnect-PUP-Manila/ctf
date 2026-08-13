import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Submission(Base):
    """Every flag attempt, correct or not."""

    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenges.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Unkeyed SHA-256 of the normalized value, for duplicate-attempt analysis only.
    # Not a validator -- see app/core/flags.py.
    submitted_value_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Populated ONLY for incorrect attempts. Correct submissions are by definition real
    # flags, and an admin log screenshot is the likeliest way one leaks.
    submitted_value_preview: Mapped[str | None] = mapped_column(String(32), nullable=True)

    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ip_address_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        # Serves the rate limiter's sliding-window count.
        Index("ix_submissions_team_submitted_at", "team_id", "submitted_at"),
        Index("ix_submissions_team_challenge_time", "team_id", "challenge_id", "submitted_at"),
        Index("ix_submissions_challenge_submitted_at", "challenge_id", "submitted_at"),
    )


class Solve(Base):
    """One successful solve per team per challenge.

    ``UNIQUE (team_id, challenge_id)`` is the correctness guarantee for concurrent
    submissions, not a convenience -- see app/services/submissions.py.
    """

    __tablename__ = "solves"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # RESTRICT makes hard-deleting a solved challenge impossible at the database
        # level. The admin delete endpoint turns that into CHALLENGE_HAS_SOLVES.
        ForeignKey("challenges.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
        nullable=False,
    )
    # Snapshot of challenges.points at solve time, so re-pointing a challenge mid-event
    # never rewrites history.
    points_awarded: Mapped[int] = mapped_column(Integer, nullable=False)
    team_fragment_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    team_fragment_preview: Mapped[str | None] = mapped_column(String(40), nullable=True)
    solved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    submission: Mapped[Submission] = relationship("Submission", foreign_keys=[submission_id])

    __table_args__ = (
        UniqueConstraint("team_id", "challenge_id", name="uq_solves_team_challenge"),
        CheckConstraint("points_awarded >= 0", name="ck_solves_points_non_negative"),
        # Leaderboard tiebreak on last solve time (#18).
        Index("ix_solves_team_solved_at", "team_id", "solved_at"),
    )
