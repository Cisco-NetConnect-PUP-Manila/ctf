import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.core.security import hash_password, normalize_email
from app.db.session import get_db
from app.main import create_app
from app.models.account import Account, AccountRole, AccountStatus
from app.models.platform_setting import PlatformSetting
from app.models.team import Team, TeamMember, TeamStatus

TEST_PASSWORD = "test-password-1234"

TEST_DATABASE_URL = make_url(settings.database_url).set(
    database="packet_capture_ctf_test"
).render_as_string(hide_password=False)

TABLES_TO_TRUNCATE = (
    "act_unlocks",
    "solves",
    "submissions",
    "challenge_files",
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


def _create_database_if_missing() -> None:
    url = make_url(TEST_DATABASE_URL)
    app_database_url = make_url(settings.database_url)
    admin_engine = create_engine(app_database_url, isolation_level="AUTOCOMMIT")
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
    config = Config("alembic.ini")
    original_database_url = settings.database_url
    settings.database_url = TEST_DATABASE_URL
    try:
        command.upgrade(config, "head")
    finally:
        settings.database_url = original_database_url


@pytest.fixture(scope="session")
def engine():
    _create_database_if_missing()
    _run_migrations()
    test_engine = create_engine(TEST_DATABASE_URL)
    yield test_engine
    test_engine.dispose()


@pytest.fixture(autouse=True)
def clean_database(engine):
    with engine.connect() as conn:
        conn.execute(text(f"truncate table {', '.join(TABLES_TO_TRUNCATE)} restart identity cascade"))
        conn.commit()
    yield


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


def seed_registration_open(session: Session, open_flag: bool) -> None:
    existing = session.query(PlatformSetting).filter_by(key="registration_open").first()
    if existing:
        existing.value_json = open_flag
    else:
        setting = PlatformSetting(key="registration_open", value_json=open_flag)
        session.add(setting)
    session.flush()


def create_test_account(
    session: Session,
    *,
    email: str = "team@example.com",
    password: str = TEST_PASSWORD,
    role: str = AccountRole.PARTICIPANT.value,
    status: str = AccountStatus.ACTIVE.value,
) -> Account:
    account = Account(
        email=normalize_email(email),
        password_hash=hash_password(password),
        role=role,
        status=status,
    )
    session.add(account)
    session.flush()
    return account


def create_test_team(
    session: Session,
    account: Account,
    *,
    group_name: str = "Test Team",
    team_status: str = TeamStatus.PENDING.value,
    members: list[dict] | None = None,
) -> Team:
    team = Team(
        account_id=account.id,
        group_name=group_name,
        status=team_status,
    )
    session.add(team)
    session.flush()

    member_data = members or [{"full_name": "Leader Name", "email": account.email, "is_leader": True}]
    leader_member = None
    for m in member_data:
        member = TeamMember(
            team_id=team.id,
            full_name=m["full_name"],
            email=normalize_email(m["email"]),
            is_leader=m.get("is_leader", False),
        )
        session.add(member)
        if member.is_leader:
            leader_member = member

    session.flush()
    team.leader_member_id = leader_member.id if leader_member else None
    session.flush()
    return team
