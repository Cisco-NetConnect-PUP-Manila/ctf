"""Start FastAPI with migrations and reference data in place."""

import os
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

from app.db.seed import seed
from app.scripts.create_admin import create_admin


def run_migrations() -> None:
    alembic_config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(alembic_config, "head")


def bootstrap() -> None:
    run_migrations()
    seed()

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
