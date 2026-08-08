from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health
from app.core.config import settings
from app.core.errors import APIError, api_error_handler, validation_error_handler


def create_app() -> FastAPI:
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

    return app


app = create_app()
