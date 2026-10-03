from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_current_admin
from app.api.routes import (
    admin_acts,
    admin_announcements,
    admin_challenges,
    admin_intel,
    admin_settings,
    admin_submissions,
    admin_teams,
    announcements,
    auth,
    challenges,
    health,
    intel,
    leaderboard,
    platform_settings,
    submissions,
)
from app.core.config import settings
from app.core.csrf import CSRFMiddleware
from app.core.errors import APIError, api_error_handler, validation_error_handler
from app.db.session import SessionLocal
from app.services.production_security import assert_admin_passwords_safe


@asynccontextmanager
async def lifespan(app):
    if settings.backend_env != "local":
        with SessionLocal() as db:
            assert_admin_passwords_safe(db)
    yield


def create_app() -> FastAPI:
    settings.assert_production_ready()

    app = FastAPI(
        title="Packet Capture API",
        version="0.1.0",
        description="Backend API for Packet Capture: Beneath the Network.",
        lifespan=lifespan,
    )

    allowed_origins = [
        origin.strip()
        for origin in settings.frontend_origin.split(",")
        if origin.strip()
    ]
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(announcements.router, tags=["announcements"])
    app.include_router(platform_settings.router, tags=["platform-settings"])
    app.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
    app.include_router(submissions.router, prefix="/challenges", tags=["challenges"])
    app.include_router(intel.router, prefix="/challenges", tags=["intel"])
    app.include_router(leaderboard.router, tags=["leaderboard"])

    # Admin guard is attached at the router level so no individual endpoint can omit it.
    admin_dependencies = [Depends(get_current_admin)]
    app.include_router(
        admin_acts.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )
    app.include_router(
        admin_challenges.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )
    app.include_router(
        admin_intel.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )
    app.include_router(
        admin_announcements.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )
    app.include_router(
        admin_teams.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )
    app.include_router(
        admin_submissions.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )
    app.include_router(
        admin_settings.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=admin_dependencies,
    )

    return app


app = create_app()
