from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Shipped default for local development only. Any non-local environment must override it;
# see Settings.assert_production_ready().
EXAMPLE_FLAG_HASH_SECRET = "change-me-local-flag-hash-secret"
EXAMPLE_TEAM_FRAGMENT_SECRET = "change-me-local-team-fragment-secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    backend_env: str = Field(default="local", alias="BACKEND_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://packet_capture:packet_capture_local_password@localhost:5432/packet_capture_ctf",
        alias="DATABASE_URL",
    )
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    session_cookie_name: str = Field(default="packet_capture_session", alias="SESSION_COOKIE_NAME")
    session_cookie_secure: bool = Field(default=False, alias="SESSION_COOKIE_SECURE")
    session_expire_hours: int = Field(default=12, alias="SESSION_EXPIRE_HOURS")
    registration_open_by_default: bool = Field(default=True, alias="REGISTRATION_OPEN_BY_DEFAULT")
    challenge_file_storage_provider: str = Field(default="local", alias="CHALLENGE_FILE_STORAGE_PROVIDER")
    challenge_file_storage_root: str = Field(
        default="storage/challenge-files",
        alias="CHALLENGE_FILE_STORAGE_ROOT",
    )
    challenge_file_max_bytes: int = Field(default=104_857_600, alias="CHALLENGE_FILE_MAX_BYTES")
    challenge_file_s3_bucket: str | None = Field(default=None, alias="CHALLENGE_FILE_S3_BUCKET")
    challenge_file_s3_prefix: str = Field(default="challenge-files", alias="CHALLENGE_FILE_S3_PREFIX")
    challenge_file_s3_presign_seconds: int = Field(
        default=300,
        alias="CHALLENGE_FILE_S3_PRESIGN_SECONDS",
    )

    email_provider: str = Field(default="none", alias="EMAIL_PROVIDER")
    email_from: str | None = Field(default=None, alias="EMAIL_FROM")
    resend_api_key: str | None = Field(default=None, alias="RESEND_API_KEY")
    sendgrid_api_key: str | None = Field(default=None, alias="SENDGRID_API_KEY")

    # Pepper for challenge flag validators. Losing or rotating it makes every stored
    # validator unverifiable and flags must be re-entered -- store it with the session
    # secret. See app/core/flags.py.
    flag_hash_secret: str = Field(default=EXAMPLE_FLAG_HASH_SECRET, alias="FLAG_HASH_SECRET")
    team_fragment_secret: str = Field(
        default=EXAMPLE_TEAM_FRAGMENT_SECRET,
        alias="TEAM_FRAGMENT_SECRET",
    )

    def assert_production_ready(self) -> None:
        """Fail fast rather than let every environment silently share one pepper."""
        if self.backend_env == "local":
            return
        if not self.database_url or "localhost" in self.database_url or "127.0.0.1" in self.database_url:
            raise RuntimeError("DATABASE_URL must point to a managed production database.")
        if not self.frontend_origin.startswith("https://"):
            raise RuntimeError("FRONTEND_ORIGIN must be an HTTPS origin in production.")
        if not self.session_cookie_secure:
            raise RuntimeError("SESSION_COOKIE_SECURE must be true in production.")
        if not self.flag_hash_secret or self.flag_hash_secret == EXAMPLE_FLAG_HASH_SECRET:
            raise RuntimeError(
                "FLAG_HASH_SECRET must be set to a unique value when BACKEND_ENV is not 'local'."
            )
        if (
            not self.team_fragment_secret
            or self.team_fragment_secret == EXAMPLE_TEAM_FRAGMENT_SECRET
        ):
            raise RuntimeError(
                "TEAM_FRAGMENT_SECRET must be set to a unique value when BACKEND_ENV is not 'local'."
            )
        provider = self.challenge_file_storage_provider.lower()
        if provider not in {"local", "s3"}:
            raise RuntimeError("CHALLENGE_FILE_STORAGE_PROVIDER must be 'local' or 's3'.")
        if provider == "s3" and not self.challenge_file_s3_bucket:
            raise RuntimeError("CHALLENGE_FILE_S3_BUCKET is required when file storage uses S3.")
        email_provider = self.email_provider.lower()
        if email_provider not in {"none", "console", "resend", "sendgrid"}:
            raise RuntimeError("EMAIL_PROVIDER must be one of: none, console, resend, sendgrid.")
        if email_provider != "none" and not self.email_from:
            raise RuntimeError("EMAIL_FROM is required when EMAIL_PROVIDER is enabled.")
        if email_provider == "resend" and not self.resend_api_key:
            raise RuntimeError("RESEND_API_KEY is required when EMAIL_PROVIDER=resend.")
        if email_provider == "sendgrid" and not self.sendgrid_api_key:
            raise RuntimeError("SENDGRID_API_KEY is required when EMAIL_PROVIDER=sendgrid.")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
