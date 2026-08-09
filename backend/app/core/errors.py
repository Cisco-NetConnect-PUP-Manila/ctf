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

# Added for challenge management (#11). FORBIDDEN and NOT_FOUND are the codes named in
# docs/api-contract.md section 3; the rest cover admin cases the contract does not yet
# describe and should be added to it rather than dropped.
FORBIDDEN = "FORBIDDEN"
NOT_FOUND = "NOT_FOUND"
TEAM_REQUIRED = "TEAM_REQUIRED"
SLUG_TAKEN = "SLUG_TAKEN"
FLAG_TAKEN = "FLAG_TAKEN"
CHALLENGE_HAS_SOLVES = "CHALLENGE_HAS_SOLVES"
CHALLENGE_HAS_NO_VALIDATOR = "CHALLENGE_HAS_NO_VALIDATOR"

# Flag submission (#13).
LOCKED_CHALLENGE = "LOCKED_CHALLENGE"
ALREADY_SOLVED = "ALREADY_SOLVED"
SUBMISSIONS_CLOSED = "SUBMISSIONS_CLOSED"
RATE_LIMITED = "RATE_LIMITED"


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
