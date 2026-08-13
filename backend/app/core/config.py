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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
