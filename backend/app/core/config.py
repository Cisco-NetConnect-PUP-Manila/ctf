from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
