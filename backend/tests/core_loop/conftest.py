"""Fixtures for the core CTF loop tests.

These override the root fixtures for this package only, so the auth tests keep their
rollback isolation untouched.

Two things the core loop needs that rollback isolation cannot give it:

* The code under test commits. Submission scoring is built around a single commit per
  path, and a test that wraps everything in one rolled-back transaction never exercises
  it.
* The concurrency tests need several genuinely simultaneous transactions on separate
  connections, to prove that concurrent correct submissions award points exactly once.

So this package uses a scratch database with TRUNCATE between tests, and a connection
pool larger than the thread count -- too small a pool deadlocks on connection checkout
and looks exactly like a scoring bug.

Never SQLite: it cannot express the partial unique indexes already used in migration
0001, ``SELECT ... FOR UPDATE``, or JSONB, so a SQLite suite would pass while production
scoring is broken.

Point TEST_DATABASE_URL at a scratch database to override the default.
"""

import os
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://packet_capture:change_this_local_password"
    "@localhost:5433/packet_capture_ctf_test"
)
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)

# More than the thread count used by the concurrency tests.
CONCURRENCY_POOL_SIZE = 20

TABLES_TO_TRUNCATE = (
    "act_unlocks",
    "solves",
    "submissions",
    "challenge_flags",
    "challenges",
    "challenge_categories",
    "challenge_difficulties",
    "acts",
    "audit_logs",
    "account_sessions",
    "team_members",
    "teams",
    "accounts",
    "platform_settings",
)


def _create_database_if_missing(url) -> None:
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
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


def _run_migrations() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env={**os.environ, "DATABASE_URL": TEST_DATABASE_URL},
        check=True,
        capture_output=True,
    )


@pytest.fixture(scope="session")
def engine():
    """Overrides the root engine fixture for this package."""
    _create_database_if_missing(make_url(TEST_DATABASE_URL))
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
    # Mirrors the production SessionLocal, autoflush=False included, so the tests
    # exercise the same read-after-write behaviour the app has.
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def clean_database(engine) -> Generator[None, None, None]:
    # Reference data is truncated too and re-seeded per test by seed_reference_data.
    # Sharing it would be faster, but tests legitimately toggle acts.is_active and
    # rewrite thresholds, and leaking that into the next test produces failures that
    # look like scoring bugs.
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
def _point_app_at_test_database(session_factory):
    """Make the app's SessionLocal use the test engine.

    Needed because the service layer opens its own sessions rather than receiving one
    from the request, which is what makes the concurrency tests possible.
    """
    import app.db.session as app_session

    original = app_session.SessionLocal
    app_session.SessionLocal = session_factory
    yield
    app_session.SessionLocal = original


@pytest.fixture
def client(session_factory) -> Generator[TestClient, None, None]:
    """Overrides the root client fixture: real commits, no rollback wrapper."""
    from app.db.session import get_db
    from app.main import create_app

    app = create_app()

    def _get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seed_reference_data(db: Session):
    """Acts, categories and difficulties, matching app/db/seed.py."""
    from app.db.seed import run_seed

    run_seed(db)
    db.commit()
    return db
