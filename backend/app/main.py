from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_current_admin
from app.api.routes import (
    admin_acts,
    admin_announcements,
    admin_challenges,
    admin_settings,
    admin_submissions,
    admin_teams,
    announcements,
    auth,
    challenges,
    health,
    platform_settings,
    submissions,
)
from app.core.config import settings
from app.core.errors import APIError, api_error_handler, validation_error_handler


def create_app() -> FastAPI:
    settings.assert_production_ready()

    app = FastAPI(
        title="Packet Capture API",
        version="0.1.0",
        description="Backend API for Packet Capture: Beneath the Network.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
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
