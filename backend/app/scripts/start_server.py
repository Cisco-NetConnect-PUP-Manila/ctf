"""Start FastAPI with migrations and reference data in place."""

import os
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

from app.db.session import SessionLocal
from app.db.seed import seed
from app.models.platform_setting import PlatformSetting
from app.scripts.create_admin import create_admin


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def run_migrations() -> None:
    alembic_config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(alembic_config, "head")


def configure_team_approval() -> None:
    if not _env_bool("REQUIRE_TEAM_APPROVAL_ON_START"):
        return

    with SessionLocal() as db:
        setting = db.query(PlatformSetting).filter_by(key="require_team_approval").first()
        if setting is None:
            db.add(PlatformSetting(key="require_team_approval", value_json=True))
        else:
            setting.value_json = True
        db.commit()
        print("Configured platform setting: require_team_approval=true")


def bootstrap_admin_from_env() -> bool:
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    if not email and not password:
        return False
    if not email or not password:
        raise RuntimeError(
            "BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD must be set together."
        )

    create_admin(email, password)
    return True


def bootstrap() -> None:
    run_migrations()
    seed()
    configure_team_approval()

    if bootstrap_admin_from_env():
        return

    if os.getenv("BACKEND_ENV", "local").lower() != "local":
        return

    email = os.getenv("DEV_ADMIN_EMAIL")
    password = os.getenv("DEV_ADMIN_PASSWORD")
    if email and password:
        create_admin(email, password)
    else:
        print("Local admin bootstrap skipped: DEV_ADMIN_EMAIL/PASSWORD are not configured.")


def main() -> None:
    bootstrap()
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
