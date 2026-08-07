"""Error envelope matching the handoff API contract: {code, message, field_errors?}.

Existing auth routes raise plain ``HTTPException`` with a string detail and must keep
rendering ``{"detail": "..."}`` exactly as they do today -- the frontend already consumes
that shape. The handler below therefore only rewrites responses whose detail is a dict
carrying a ``code``, leaving every other route byte-identical.

``RequestValidationError`` is deliberately NOT handled here: overriding it would change
the 422 shape of /auth/register's field validation and break frontend integration.
"""

from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class APIError(HTTPException):
    """HTTPException that renders the documented {code, message} envelope."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field_errors: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"code": code, "message": message}
        if field_errors:
            payload["field_errors"] = field_errors
        super().__init__(status_code=status_code, detail=payload, headers=headers)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail, headers=exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=exc.headers,
    )


def register_error_handlers(app: Any) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
