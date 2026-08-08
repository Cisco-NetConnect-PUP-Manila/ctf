from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

EMAIL_TAKEN = "EMAIL_TAKEN"
GROUP_NAME_TAKEN = "GROUP_NAME_TAKEN"
REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
AUTH_REQUIRED = "AUTH_REQUIRED"
SESSION_EXPIRED = "SESSION_EXPIRED"
VALIDATION_ERROR = "VALIDATION_ERROR"
TEAM_NOT_APPROVED = "TEAM_NOT_APPROVED"
INTERNAL_ERROR = "INTERNAL_ERROR"


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field_errors: dict | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.field_errors = field_errors or {}


async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "field_errors": exc.field_errors,
        },
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    field_errors: dict[str, list[str]] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = ".".join(str(part) for part in loc if part not in ("body", "__root__"))
        if field:
            field_errors.setdefault(field, []).append(error.get("msg", "Invalid value."))

    return JSONResponse(
        status_code=400,
        content={
            "code": VALIDATION_ERROR,
            "message": "Request validation failed.",
            "field_errors": field_errors,
        },
    )
