"""Admin endpoints for organizer-controlled platform settings (Issue #21).

The admin guard is attached at router registration in ``main.py`` via
``dependencies=[Depends(get_current_admin)]`` so no endpoint here can omit it. The
``admin`` parameter is still injected on PATCH where the actor id is needed for audit
logging.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.account import Account
from app.schemas.platform_settings import PlatformSettingsResponse, PlatformSettingsUpdate
from app.services import platform_settings as settings_service

router = APIRouter()


@router.get("/platform-settings", response_model=PlatformSettingsResponse)
def read_platform_settings(db: Session = Depends(get_db)) -> PlatformSettingsResponse:
    return PlatformSettingsResponse(**settings_service.get_all_settings(db))


@router.patch("/platform-settings", response_model=PlatformSettingsResponse)
def update_platform_settings(
    payload: PlatformSettingsUpdate,
    db: Session = Depends(get_db),
    admin: Account = Depends(get_current_admin),
) -> PlatformSettingsResponse:
    updated = settings_service.update_settings(
        db,
        changes=payload.to_changes(),
        actor_account_id=admin.id,
    )
    db.commit()
    return PlatformSettingsResponse(**updated)
