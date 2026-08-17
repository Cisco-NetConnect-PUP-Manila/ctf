"""Public-safe platform settings.

Only expose competition state needed by public/participant UI. Mutations stay under the
admin router.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.platform_settings import PlatformSettingsResponse
from app.services import platform_settings as settings_service

router = APIRouter()


@router.get("/platform-settings", response_model=PlatformSettingsResponse)
def read_public_platform_settings(
    db: Session = Depends(get_db),
) -> PlatformSettingsResponse:
    return PlatformSettingsResponse(**settings_service.get_all_settings(db))
