"""Start FastAPI, bootstrapping reproducible local-development data first."""

import os
from pathlib import Path

import uvicorn
from alembic import command
from alembic.config import Config

from app.db.seed import seed
from app.scripts.create_admin import create_admin


def bootstrap_local() -> None:
    if os.getenv("BACKEND_ENV", "local").lower() != "local":
        return

    alembic_config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(alembic_config, "head")
    seed()

    email = os.getenv("DEV_ADMIN_EMAIL")
    password = os.getenv("DEV_ADMIN_PASSWORD")
    if email and password:
        create_admin(email, password)
    else:
        print("Local admin bootstrap skipped: DEV_ADMIN_EMAIL/PASSWORD are not configured.")


def main() -> None:
    bootstrap_local()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
