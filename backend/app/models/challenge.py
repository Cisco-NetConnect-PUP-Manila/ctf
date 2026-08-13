import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.act import Act


class ChallengeStatus(str, enum.Enum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FlagValidatorType(str, enum.Enum):
    EXACT = "exact"


class ChallengeCategory(Base):
    __tablename__ = "challenge_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ChallengeDifficulty(Base):
    __tablename__ = "challenge_difficulties"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    act_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("acts.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenge_categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
    difficulty_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenge_difficulties.id", ondelete="RESTRICT"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    mission_brief: Mapped[str] = mapped_column(Text, nullable=False)
    story_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    objectives_json: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    points: Mapped[int] = mapped_column(Integer, nullable=False)

    # status is the lifecycle; is_visible is the organizer's emergency pull switch that
    # does not reset publish metadata. Handoff section 10 step 3 requires both as
    # distinct checks ("published, visible, unlocked, accessible").
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=ChallengeStatus.DRAFT.value,
    )
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # One-word key used by the Final Investigation (#22). Written and read by admin CRUD
    # only -- never exposed to participants, and carries no logic here.
    story_fragment: Mapped[str | None] = mapped_column(String(64), nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    published_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    act: Mapped["Act"] = relationship("Act", back_populates="challenges", foreign_keys=[act_id])
    category: Mapped[ChallengeCategory | None] = relationship(
        "ChallengeCategory",
        foreign_keys=[category_id],
    )
    difficulty: Mapped[ChallengeDifficulty | None] = relationship(
        "ChallengeDifficulty",
        foreign_keys=[difficulty_id],
    )
    flags: Mapped[list["ChallengeFlag"]] = relationship(
        "ChallengeFlag",
        back_populates="challenge",
        cascade="all, delete-orphan",
        foreign_keys="ChallengeFlag.challenge_id",
    )
    files: Mapped[list["ChallengeFile"]] = relationship(
        "ChallengeFile",
        back_populates="challenge",
        cascade="all, delete-orphan",
        foreign_keys="ChallengeFile.challenge_id",
    )

    __table_args__ = (
        CheckConstraint("points >= 0", name="ck_challenges_points_non_negative"),
        CheckConstraint(
            "status in ('draft', 'ready_for_review', 'published', 'archived')",
            name="ck_challenges_status",
        ),
        Index("ix_challenges_act_status", "act_id", "status"),
        Index("ix_challenges_act_sort", "act_id", "sort_order"),
    )


class ChallengeFile(Base):
    """Private challenge artifact metadata.

    The file bytes live behind the backend storage adapter. ``storage_key`` is generated
    internally and never derived from ``original_filename``.
    """

    __tablename__ = "challenge_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    storage_provider: Mapped[str] = mapped_column(String(40), nullable=False, default="local")
    storage_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(16), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uploaded_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    challenge: Mapped[Challenge] = relationship(
        "Challenge",
        back_populates="files",
        foreign_keys=[challenge_id],
    )

    __table_args__ = (
        CheckConstraint("storage_provider in ('local')", name="ck_challenge_files_provider"),
        CheckConstraint(
            "extension in ('.raw', '.pcap', '.dd', '.png', '.txt', '.pkz', '.pka')",
            name="ck_challenge_files_extension",
        ),
        CheckConstraint("size_bytes between 0 and 104857600", name="ck_challenge_files_size"),
        Index(
            "ix_challenge_files_challenge_active",
            "challenge_id",
            postgresql_where=text("is_active = true"),
        ),
    )


class ChallengeFlag(Base):
    """Protected flag validator. The hash is never returned by any endpoint.

    ``flag_hash`` holds ``hmac-sha256$v1$<hex>`` -- see app/core/flags.py. A database
    dump alone cannot be brute-forced back to flags without FLAG_HASH_SECRET.
    """

    __tablename__ = "challenge_flags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("challenges.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    flag_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    validator_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=FlagValidatorType.EXACT.value,
    )
    label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    challenge: Mapped[Challenge] = relationship(
        "Challenge",
        back_populates="flags",
        foreign_keys=[challenge_id],
    )

    __table_args__ = (
        # Only 'exact' is implemented. Widening this later is a one-line migration;
        # allowing a value with no implementation ships a challenge that accepts nothing.
        CheckConstraint("validator_type in ('exact')", name="ck_challenge_flags_validator_type"),
        UniqueConstraint("challenge_id", "flag_hash", name="uq_challenge_flags_challenge_hash"),
        Index(
            "ix_challenge_flags_challenge_active",
            "challenge_id",
            postgresql_where=text("is_active = true"),
        ),
    )
