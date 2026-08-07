"""Test data builders."""

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.flags import hash_flag
from app.core.security import hash_password
from app.models.account import Account, AccountRole, AccountStatus
from app.models.act import Act
from app.models.challenge import Challenge, ChallengeFlag, ChallengeStatus, FlagValidatorType
from app.models.platform_setting import PlatformSetting
from app.models.team import Team, TeamMember, TeamStatus
from app.services.platform_settings import KEY_SUBMISSION_RATE_LIMIT

PASSWORD = "test-password-123456"


def set_rate_limit(
    db: Session,
    window_seconds: int = 60,
    per_team_per_window: int = 1000,
    per_challenge_per_window: int = 1000,
    cooldown_seconds: int = 0,
) -> None:
    """Write the real platform_settings row.

    Tests configure the limiter through the same path organizers use, rather than
    monkeypatching, so the JSON parsing and defaulting logic is covered too. Defaults here
    are permissive because most tests submit back to back and are not testing the limiter.
    """
    existing = db.scalar(
        select(PlatformSetting).where(PlatformSetting.key == KEY_SUBMISSION_RATE_LIMIT)
    )
    value = {
        "window_seconds": window_seconds,
        "per_team_per_window": per_team_per_window,
        "per_challenge_per_window": per_challenge_per_window,
        "cooldown_seconds": cooldown_seconds,
    }
    if existing is None:
        db.add(PlatformSetting(key=KEY_SUBMISSION_RATE_LIMIT, value_json=value))
    else:
        existing.value_json = value
    db.commit()


@dataclass
class TeamFixture:
    account: Account
    team: Team
    email: str


def make_account(
    db: Session,
    role: AccountRole = AccountRole.PARTICIPANT,
    status: AccountStatus = AccountStatus.ACTIVE,
    email: str | None = None,
) -> Account:
    account = Account(
        email=email or f"{role.value}-{uuid.uuid4().hex[:10]}@example.com",
        password_hash=hash_password(PASSWORD),
        role=role.value,
        status=status.value,
    )
    db.add(account)
    db.flush()
    return account


def make_team(
    db: Session,
    group_name: str | None = None,
    status: TeamStatus = TeamStatus.APPROVED,
) -> TeamFixture:
    account = make_account(db)
    team = Team(
        account_id=account.id,
        group_name=group_name or f"Team {uuid.uuid4().hex[:8]}",
        status=status.value,
    )
    db.add(team)
    db.flush()

    member = TeamMember(
        team_id=team.id,
        full_name="Test Leader",
        email=account.email,
        is_leader=True,
    )
    db.add(member)
    db.flush()
    team.leader_member_id = member.id
    db.commit()

    return TeamFixture(account=account, team=team, email=account.email)


def make_admin(db: Session) -> Account:
    account = make_account(db, role=AccountRole.ADMIN)
    db.commit()
    return account


def get_act(db: Session, act_number: int) -> Act:
    act = db.scalar(select(Act).where(Act.act_number == act_number))
    assert act is not None, f"Act {act_number} missing; use the seed_reference_data fixture"
    return act


def make_challenge(
    db: Session,
    act: Act,
    points: int = 100,
    flag: str | None = "PacketCapture{TEST_FLAG}",
    status: ChallengeStatus = ChallengeStatus.PUBLISHED,
    is_visible: bool = True,
    title: str | None = None,
) -> Challenge:
    suffix = uuid.uuid4().hex[:8]
    challenge = Challenge(
        act_id=act.id,
        title=title or f"Challenge {suffix}",
        slug=f"challenge-{suffix}",
        mission_brief="Find the flag.",
        story_context="Test context.",
        objectives_json=["Do the thing"],
        points=points,
        status=status.value,
        is_visible=is_visible,
        story_fragment="FRAGMENT",
        sort_order=0,
    )
    db.add(challenge)
    db.flush()

    if flag is not None:
        db.add(
            ChallengeFlag(
                challenge_id=challenge.id,
                flag_hash=hash_flag(flag),
                validator_type=FlagValidatorType.EXACT.value,
                label="primary",
                is_active=True,
            )
        )
    db.commit()
    return challenge
