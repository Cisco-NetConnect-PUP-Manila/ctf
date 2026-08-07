"""Test fixtures.

Runs against a REAL PostgreSQL database, never SQLite. SQLite cannot express the partial
unique indexes already used in migration 0001, ``SELECT ... FOR UPDATE``, or JSONB -- a
SQLite suite would pass while production scoring is broken, which is the worst possible
outcome for this code.

Isolation is by TRUNCATE, not by wrapping each test in a rolled-back transaction: the code
under test commits, and the concurrency tests need genuinely committed transactions on
separate connections.

Set TEST_DATABASE_URL to point at a scratch database. It defaults to the local
docker-compose Postgres with a ``_test`` suffix on the database name.
"""

import os
import subprocess
import sys
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://packet_capture:change_this_local_password"
    "@localhost:5433/packet_capture_ctf_test"
)
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)

# The app reads settings at import time, so the environment must be set before any
# `app.*` import happens.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("BACKEND_ENV", "local")
os.environ.setdefault("FLAG_HASH_SECRET", "test-flag-hash-secret")

# Concurrency tests run more threads than the default QueuePool size of 5; too small a
# pool deadlocks on connection checkout and looks exactly like a scoring bug.
CONCURRENCY_POOL_SIZE = 20

TABLES_TO_TRUNCATE = (
    "act_unlocks",
    "solves",
    "submissions",
    "challenge_flags",
    "challenges",
    "audit_logs",
    "account_sessions",
    "team_members",
    "teams",
    "accounts",
    "platform_settings",
)


def _run_migrations() -> None:
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env=env,
        check=True,
        capture_output=True,
    )


@pytest.fixture(scope="session")
def engine():
    from sqlalchemy.engine import make_url

    url = make_url(TEST_DATABASE_URL)
    admin_url = url.set(database="postgres")

    # Create the scratch database if it is missing. AUTOCOMMIT because CREATE DATABASE
    # cannot run inside a transaction block.
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("select 1 from pg_database where datname = :name"),
                {"name": url.database},
            ).scalar()
            if not exists:
                conn.execute(text(f'create database "{url.database}"'))
    finally:
        admin_engine.dispose()

    _run_migrations()

    test_engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=CONCURRENCY_POOL_SIZE,
        max_overflow=10,
    )
    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    # Mirrors the production SessionLocal, including autoflush=False -- the tests must
    # exercise the same read-after-write behaviour the app has.
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def clean_database(engine) -> Generator[None, None, None]:
    with engine.connect() as conn:
        conn.execute(
            text(f"truncate table {', '.join(TABLES_TO_TRUNCATE)} restart identity cascade")
        )
        conn.commit()
    yield


@pytest.fixture
def db(session_factory) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session", autouse=True)
def _patch_app_session(engine, session_factory):
    """Point the app's SessionLocal at the test engine.

    Done once per session so TestClient requests and direct service calls share one
    database.
    """
    import app.db.session as app_session

    app_session.engine = engine
    app_session.SessionLocal = session_factory
    yield


@pytest.fixture
def seed_reference_data(db: Session):
    """Acts, categories and difficulties, matching app/db/seed.py."""
    from app.db.seed import run_seed

    run_seed(db)
    return db


@pytest.fixture
def unique_email():
    def _make(prefix: str = "user") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"

    return _make
