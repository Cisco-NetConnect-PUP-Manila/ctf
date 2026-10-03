"""Origin + non-simple header protection for browser mutations.

Cookie-authenticated scripts must send the same headers as the web client.
Requests without cookies or browser Origin remain usable by CLI clients.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            browser_or_session = origin is not None or settings.session_cookie_name in request.cookies or request.headers.get("sec-fetch-site") is not None
            allowed = {value.strip() for value in settings.frontend_origin.split(",") if value.strip()}
            if browser_or_session and (origin not in allowed or request.headers.get("x-csrf-protection") != "1"):
                return JSONResponse({"code": "CSRF_REJECTED", "message": "Request origin could not be verified. Reload the page and try again."}, status_code=403)
        return await call_next(request)
