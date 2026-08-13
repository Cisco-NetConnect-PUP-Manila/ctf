"""Admin challenge management (#11).

Mounted with ``dependencies=[Depends(get_current_admin)]`` at the router level in main.py.

No response in this module ever carries a flag value or a flag hash -- only counts and
metadata. ``_challenge_to_admin_response`` is the single mapper, so that property is
checked in one place.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_admin
from app.core.errors import (
    APIError,
    CHALLENGE_HAS_NO_VALIDATOR,
    CHALLENGE_HAS_SOLVES,
    FLAG_TAKEN,
    NOT_FOUND,
    SLUG_TAKEN,
    VALIDATION_ERROR,
)
from app.core.flags import hash_flag
from app.db.session import get_db
from app.models.account import Account
from app.models.act import Act
from app.models.audit_log import AuditLog
from app.models.challenge import (
    Challenge,
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeFile,
    ChallengeFlag,
    ChallengeStatus,
    FlagValidatorType,
)
from app.schemas.challenge import (
    ChallengeAdminResponse,
    ChallengeCreateRequest,
    ChallengeFileResponse,
    ChallengeFlagCreateRequest,
    ChallengeFlagResponse,
    ChallengePublishRequest,
    ChallengeUpdateRequest,
    LookupResponse,
)
from app.services.challenge_files import (
    ChallengeFileTooLarge,
    ChallengeFileStorageError,
    UnsupportedChallengeFileType,
    get_challenge_file_storage,
)

router = APIRouter()


# --------------------------------------------------------------------------- mappers


def _lookup_to_response(row: ChallengeCategory | ChallengeDifficulty | None) -> LookupResponse | None:
    if row is None:
        return None
    return LookupResponse(
        id=row.id,
        name=row.name,
        slug=row.slug,
        sort_order=row.sort_order,
        is_active=row.is_active,
    )


def _active_flag_count(db: Session, challenge_id: UUID) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(ChallengeFlag)
            .where(
                ChallengeFlag.challenge_id == challenge_id,
                ChallengeFlag.is_active.is_(True),
            )
        )
        or 0
    )


def _active_file_count(db: Session, challenge_id: UUID) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(ChallengeFile)
            .where(
                ChallengeFile.challenge_id == challenge_id,
                ChallengeFile.is_active.is_(True),
            )
        )
        or 0
    )


def _challenge_to_admin_response(db: Session, challenge: Challenge) -> ChallengeAdminResponse:
    return ChallengeAdminResponse(
        id=challenge.id,
        act_id=challenge.act_id,
        act_number=challenge.act.act_number,
        title=challenge.title,
        slug=challenge.slug,
        mission_brief=challenge.mission_brief,
        story_context=challenge.story_context,
        objectives=list(challenge.objectives_json or []),
        points=challenge.points,
        status=challenge.status,
        is_visible=challenge.is_visible,
        story_fragment=challenge.story_fragment,
        sort_order=challenge.sort_order,
        category=_lookup_to_response(challenge.category),
        difficulty=_lookup_to_response(challenge.difficulty),
        active_flag_count=_active_flag_count(db, challenge.id),
        active_file_count=_active_file_count(db, challenge.id),
    )


def _file_to_response(file: ChallengeFile) -> ChallengeFileResponse:
    return ChallengeFileResponse(
        id=file.id,
        challenge_id=file.challenge_id,
        display_name=file.display_name,
        original_filename=file.original_filename,
        extension=file.extension,
        content_type=file.content_type,
        size_bytes=file.size_bytes,
        is_active=file.is_active,
    )


def _flag_to_response(flag: ChallengeFlag) -> ChallengeFlagResponse:
    return ChallengeFlagResponse(
        id=flag.id,
        challenge_id=flag.challenge_id,
        label=flag.label,
        validator_type=flag.validator_type,
        is_active=flag.is_active,
    )


# --------------------------------------------------------------------------- helpers


def _load_challenge(db: Session, challenge_id: UUID) -> Challenge:
    challenge = db.scalar(
        select(Challenge)
        .options(
            joinedload(Challenge.act),
            joinedload(Challenge.category),
            joinedload(Challenge.difficulty),
        )
        .where(Challenge.id == challenge_id)
    )
    if challenge is None:
        raise APIError(status.HTTP_404_NOT_FOUND, NOT_FOUND, "Challenge not found.")
    return challenge


def _require_act(db: Session, act_id: UUID) -> Act:
    act = db.get(Act, act_id)
    if act is None:
        raise APIError(
            status.HTTP_400_BAD_REQUEST,
            VALIDATION_ERROR,
            "The referenced Act does not exist.",
            field_errors={"act_id": "Unknown Act."},
        )
    return act


def _require_lookup(db: Session, model: type, row_id: UUID | None, field: str) -> None:
    if row_id is None:
        return
    if db.get(model, row_id) is None:
        raise APIError(
            status.HTTP_400_BAD_REQUEST,
            VALIDATION_ERROR,
            f"The referenced {field} does not exist.",
            field_errors={field: "Unknown value."},
        )


def _require_unique_slug(db: Session, slug: str, exclude_id: UUID | None = None) -> None:
    stmt = select(Challenge.id).where(Challenge.slug == slug)
    if exclude_id is not None:
        stmt = stmt.where(Challenge.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise APIError(
            status.HTTP_409_CONFLICT,
            SLUG_TAKEN,
            "A challenge with this slug already exists.",
            field_errors={"slug": "Already in use."},
        )


# --------------------------------------------------------------------- lookup tables


@router.get("/challenge-categories", response_model=list[LookupResponse])
def list_categories(db: Session = Depends(get_db)) -> list[LookupResponse]:
    rows = db.scalars(
        select(ChallengeCategory).order_by(ChallengeCategory.sort_order, ChallengeCategory.name)
    ).all()
    return [_lookup_to_response(row) for row in rows]


@router.get("/challenge-difficulties", response_model=list[LookupResponse])
def list_difficulties(db: Session = Depends(get_db)) -> list[LookupResponse]:
    rows = db.scalars(
        select(ChallengeDifficulty).order_by(
            ChallengeDifficulty.sort_order, ChallengeDifficulty.name
        )
    ).all()
    return [_lookup_to_response(row) for row in rows]


# ------------------------------------------------------------------------ challenges


@router.get("/challenges", response_model=list[ChallengeAdminResponse])
def list_challenges(
    act_id: UUID | None = None,
    challenge_status: ChallengeStatus | None = None,
    db: Session = Depends(get_db),
) -> list[ChallengeAdminResponse]:
    stmt = (
        select(Challenge)
        .options(
            joinedload(Challenge.act),
            joinedload(Challenge.category),
            joinedload(Challenge.difficulty),
        )
        .join(Act, Act.id == Challenge.act_id)
        .order_by(Act.act_number, Challenge.sort_order, Challenge.title)
    )
    if act_id is not None:
        stmt = stmt.where(Challenge.act_id == act_id)
    if challenge_status is not None:
        stmt = stmt.where(Challenge.status == challenge_status.value)

    return [_challenge_to_admin_response(db, row) for row in db.scalars(stmt).all()]


@router.get("/challenges/{challenge_id}", response_model=ChallengeAdminResponse)
def get_challenge(challenge_id: UUID, db: Session = Depends(get_db)) -> ChallengeAdminResponse:
    return _challenge_to_admin_response(db, _load_challenge(db, challenge_id))


@router.post(
    "/challenges",
    response_model=ChallengeAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_challenge(
    payload: ChallengeCreateRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeAdminResponse:
    _require_act(db, payload.act_id)
    _require_lookup(db, ChallengeCategory, payload.category_id, "category_id")
    _require_lookup(db, ChallengeDifficulty, payload.difficulty_id, "difficulty_id")
    _require_unique_slug(db, payload.slug)

    challenge = Challenge(
        act_id=payload.act_id,
        category_id=payload.category_id,
        difficulty_id=payload.difficulty_id,
        title=payload.title,
        slug=payload.slug,
        mission_brief=payload.mission_brief,
        story_context=payload.story_context,
        objectives_json=payload.objectives,
        points=payload.points,
        status=ChallengeStatus.DRAFT.value,
        is_visible=payload.is_visible,
        story_fragment=payload.story_fragment,
        sort_order=payload.sort_order,
        created_by_account_id=current_admin.id,
    )
    db.add(challenge)
    db.flush()

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge.created",
            target_type="challenge",
            target_id=challenge.id,
            metadata_json={"slug": challenge.slug, "points": challenge.points},
        )
    )
    db.commit()
    return _challenge_to_admin_response(db, _load_challenge(db, challenge.id))


@router.patch("/challenges/{challenge_id}", response_model=ChallengeAdminResponse)
def update_challenge(
    challenge_id: UUID,
    payload: ChallengeUpdateRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeAdminResponse:
    challenge = _load_challenge(db, challenge_id)

    if payload.act_id is not None:
        _require_act(db, payload.act_id)
        challenge.act_id = payload.act_id
    if payload.category_id is not None:
        _require_lookup(db, ChallengeCategory, payload.category_id, "category_id")
        challenge.category_id = payload.category_id
    if payload.difficulty_id is not None:
        _require_lookup(db, ChallengeDifficulty, payload.difficulty_id, "difficulty_id")
        challenge.difficulty_id = payload.difficulty_id
    if payload.slug is not None:
        _require_unique_slug(db, payload.slug, exclude_id=challenge.id)
        challenge.slug = payload.slug

    for field in ("title", "mission_brief", "story_context", "points", "sort_order", "is_visible"):
        value = getattr(payload, field)
        if value is not None:
            setattr(challenge, field, value)

    if payload.objectives is not None:
        challenge.objectives_json = payload.objectives
    if payload.story_fragment is not None:
        challenge.story_fragment = payload.story_fragment

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge.updated",
            target_type="challenge",
            target_id=challenge.id,
            metadata_json={
                "slug": challenge.slug,
                "fields": sorted(payload.model_dump(exclude_unset=True).keys()),
            },
        )
    )
    db.commit()
    return _challenge_to_admin_response(db, _load_challenge(db, challenge.id))


@router.patch("/challenges/{challenge_id}/publish", response_model=ChallengeAdminResponse)
def set_challenge_status(
    challenge_id: UUID,
    payload: ChallengePublishRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeAdminResponse:
    challenge = _load_challenge(db, challenge_id)
    new_status = payload.status
    now = datetime.now(UTC)

    # "At least one active validator before publish" cannot be expressed as a DDL
    # constraint, so it is enforced here. Publishing a challenge with no validator would
    # ship something that silently accepts nothing.
    if new_status is ChallengeStatus.PUBLISHED and _active_flag_count(db, challenge.id) == 0:
        raise APIError(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            CHALLENGE_HAS_NO_VALIDATOR,
            "Add at least one active flag validator before publishing this challenge.",
        )

    challenge.status = new_status.value
    if new_status is ChallengeStatus.PUBLISHED:
        challenge.published_by_account_id = current_admin.id
        challenge.published_at = now
    elif new_status is ChallengeStatus.ARCHIVED:
        challenge.archived_by_account_id = current_admin.id
        challenge.archived_at = now

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action=f"challenge.{new_status.value}",
            target_type="challenge",
            target_id=challenge.id,
            metadata_json={"slug": challenge.slug, "status": new_status.value},
        )
    )
    db.commit()
    return _challenge_to_admin_response(db, _load_challenge(db, challenge.id))


@router.delete("/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(
    challenge_id: UUID,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Response:
    challenge = _load_challenge(db, challenge_id)
    slug = challenge.slug

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge.deleted",
            target_type="challenge",
            target_id=challenge.id,
            metadata_json={"slug": slug},
        )
    )
    db.delete(challenge)

    try:
        db.commit()
    except IntegrityError as exc:
        # solves.challenge_id is ondelete=RESTRICT, so the database refuses to drop a
        # challenge a team has already solved. That is the guardrail; steer to archive.
        db.rollback()
        raise APIError(
            status.HTTP_409_CONFLICT,
            CHALLENGE_HAS_SOLVES,
            "This challenge has recorded solves and cannot be deleted. Archive it instead.",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------- challenge files


@router.get("/challenges/{challenge_id}/files", response_model=list[ChallengeFileResponse])
def list_challenge_files(
    challenge_id: UUID,
    db: Session = Depends(get_db),
) -> list[ChallengeFileResponse]:
    _load_challenge(db, challenge_id)
    rows = db.scalars(
        select(ChallengeFile)
        .where(ChallengeFile.challenge_id == challenge_id)
        .order_by(ChallengeFile.is_active.desc(), ChallengeFile.created_at)
    ).all()
    return [_file_to_response(row) for row in rows]


@router.post(
    "/challenges/{challenge_id}/files",
    response_model=ChallengeFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_challenge_file(
    challenge_id: UUID,
    upload: UploadFile = File(...),
    display_name: str | None = Form(default=None),
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeFileResponse:
    _load_challenge(db, challenge_id)
    storage = get_challenge_file_storage()

    try:
        stored = await storage.save(upload, challenge_id=challenge_id, display_name=display_name)
    except UnsupportedChallengeFileType as exc:
        raise APIError(
            status.HTTP_400_BAD_REQUEST,
            VALIDATION_ERROR,
            "Unsupported challenge file type.",
            field_errors={
                "upload": f"Allowed file types: .raw, .pcap, .dd, .png, .txt, .pkz, .pka. Got {exc}."
            },
        ) from exc
    except ChallengeFileTooLarge as exc:
        raise APIError(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            VALIDATION_ERROR,
            "Challenge file is too large.",
            field_errors={"upload": "Maximum file size is 100 MB."},
        ) from exc
    except ChallengeFileStorageError as exc:
        raise APIError(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            VALIDATION_ERROR,
            "Challenge file storage is not configured correctly.",
        ) from exc

    row = ChallengeFile(
        challenge_id=challenge_id,
        storage_provider=stored.storage_provider,
        storage_key=stored.storage_key,
        original_filename=stored.original_filename,
        display_name=stored.display_name,
        extension=stored.extension,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
        uploaded_by_account_id=current_admin.id,
        is_active=True,
    )
    db.add(row)
    try:
        db.flush()
    except Exception:
        db.rollback()
        storage.delete(stored.storage_key)
        raise

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge_file.uploaded",
            target_type="challenge",
            target_id=challenge_id,
            metadata_json={
                "file_id": str(row.id),
                "display_name": row.display_name,
                "extension": row.extension,
                "size_bytes": row.size_bytes,
            },
        )
    )
    db.commit()
    db.refresh(row)
    return _file_to_response(row)


@router.delete(
    "/challenges/{challenge_id}/files/{file_id}",
    response_model=ChallengeFileResponse,
)
def deactivate_challenge_file(
    challenge_id: UUID,
    file_id: UUID,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeFileResponse:
    row = db.scalar(
        select(ChallengeFile).where(
            ChallengeFile.id == file_id,
            ChallengeFile.challenge_id == challenge_id,
        )
    )
    if row is None:
        raise APIError(status.HTTP_404_NOT_FOUND, NOT_FOUND, "Challenge file not found.")

    if row.is_active:
        row.is_active = False
        row.deactivated_at = datetime.now(UTC)

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge_file.deactivated",
            target_type="challenge",
            target_id=challenge_id,
            metadata_json={"file_id": str(row.id), "display_name": row.display_name},
        )
    )
    db.commit()
    db.refresh(row)
    return _file_to_response(row)


# ----------------------------------------------------------------- flag validators


@router.get("/challenges/{challenge_id}/flags", response_model=list[ChallengeFlagResponse])
def list_challenge_flags(
    challenge_id: UUID,
    db: Session = Depends(get_db),
) -> list[ChallengeFlagResponse]:
    _load_challenge(db, challenge_id)
    rows = db.scalars(
        select(ChallengeFlag)
        .where(ChallengeFlag.challenge_id == challenge_id)
        .order_by(ChallengeFlag.created_at)
    ).all()
    return [_flag_to_response(row) for row in rows]


@router.post(
    "/challenges/{challenge_id}/flags",
    response_model=ChallengeFlagResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_challenge_flag(
    challenge_id: UUID,
    payload: ChallengeFlagCreateRequest,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeFlagResponse:
    _load_challenge(db, challenge_id)

    flag = ChallengeFlag(
        challenge_id=challenge_id,
        flag_hash=hash_flag(payload.value),
        validator_type=FlagValidatorType.EXACT.value,
        label=payload.label,
        is_active=True,
        created_by_account_id=current_admin.id,
    )
    db.add(flag)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise APIError(
            status.HTTP_409_CONFLICT,
            FLAG_TAKEN,
            "This flag is already registered for this challenge.",
            field_errors={"value": "Duplicate flag."},
        ) from exc

    # Deliberately records no part of the flag value -- not even a preview.
    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge_flag.created",
            target_type="challenge",
            target_id=challenge_id,
            metadata_json={"flag_id": str(flag.id), "label": payload.label},
        )
    )
    db.commit()
    db.refresh(flag)
    return _flag_to_response(flag)


@router.delete(
    "/challenges/{challenge_id}/flags/{flag_id}",
    response_model=ChallengeFlagResponse,
)
def deactivate_challenge_flag(
    challenge_id: UUID,
    flag_id: UUID,
    current_admin: Account = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ChallengeFlagResponse:
    flag = db.scalar(
        select(ChallengeFlag).where(
            ChallengeFlag.id == flag_id,
            ChallengeFlag.challenge_id == challenge_id,
        )
    )
    if flag is None:
        raise APIError(status.HTTP_404_NOT_FOUND, NOT_FOUND, "Flag validator not found.")

    # Deactivated rather than deleted: the row is the only record that this validator ever
    # existed, and submissions may already reference the challenge.
    if flag.is_active:
        flag.is_active = False
        flag.deactivated_at = datetime.now(UTC)

    db.add(
        AuditLog(
            actor_account_id=current_admin.id,
            action="challenge_flag.deactivated",
            target_type="challenge",
            target_id=challenge_id,
            metadata_json={"flag_id": str(flag.id)},
        )
    )
    db.commit()
    db.refresh(flag)
    return _flag_to_response(flag)
