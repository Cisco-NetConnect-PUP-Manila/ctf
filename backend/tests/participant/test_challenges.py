import uuid

from sqlalchemy import select

from tests.conftest import TEST_PASSWORD, create_test_account, create_test_team

from app.models.act import Act
from app.models.challenge import Challenge, ChallengeStatus
from app.models.team import TeamStatus


def _act(db_session, number: int) -> Act:
    existing = db_session.scalar(select(Act).where(Act.act_number == number))
    if existing is not None:
        return existing
    act = Act(
        act_number=number,
        slug=f"test-act-{number}",
        title=f"Test Act {number}",
        description=f"Act {number} description",
        unlock_threshold_percent=20,
        sort_order=number,
        is_active=True,
    )
    db_session.add(act)
    db_session.flush()
    return act


def _challenge(
    db_session,
    act: Act,
    *,
    title: str,
    status: ChallengeStatus = ChallengeStatus.PUBLISHED,
    visible: bool = True,
) -> Challenge:
    challenge = Challenge(
        act_id=act.id,
        title=title,
        slug=f"{title.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}",
        mission_brief=f"Mission brief for {title}",
        story_context="Participant-safe context",
        objectives_json=["Inspect the evidence"],
        points=100,
        status=status.value,
        is_visible=visible,
        story_fragment="SECRET_FRAGMENT",
        sort_order=0,
    )
    db_session.add(challenge)
    db_session.flush()
    return challenge


def _login_team(client, db_session):
    email = f"challenge-team-{uuid.uuid4().hex[:8]}@example.com"
    account = create_test_account(db_session, email=email)
    create_test_team(
        db_session,
        account,
        group_name="Challenge Readers",
        team_status=TeamStatus.APPROVED.value,
    )
    response = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200
    return response.cookies


def test_challenge_list_requires_authentication(client):
    response = client.get("/challenges")
    assert response.status_code == 401


def test_list_groups_published_challenges_and_keeps_locked_acts(client, db_session):
    act_one = _act(db_session, 1)
    act_two = _act(db_session, 2)
    open_challenge = _challenge(db_session, act_one, title="Visible Signal")
    locked_challenge = _challenge(db_session, act_two, title="Locked Breach")
    draft = _challenge(
        db_session,
        act_one,
        title="Draft Leak",
        status=ChallengeStatus.DRAFT,
    )
    hidden = _challenge(db_session, act_one, title="Hidden Leak", visible=False)
    db_session.flush()

    response = client.get("/challenges", cookies=_login_team(client, db_session))
    assert response.status_code == 200
    body = response.json()
    returned = {
        challenge["id"]: challenge
        for group in body["acts"]
        for challenge in group["challenges"]
    }

    assert returned[str(open_challenge.id)]["locked"] is False
    assert returned[str(locked_challenge.id)]["locked"] is True
    assert str(draft.id) not in returned
    assert str(hidden.id) not in returned
    assert body["current_act"] == 1


def test_participant_shape_never_exposes_flag_or_admin_fields(client, db_session):
    challenge = _challenge(db_session, _act(db_session, 1), title="Safe Shape")
    db_session.flush()

    response = client.get("/challenges", cookies=_login_team(client, db_session))
    item = next(
        challenge_item
        for group in response.json()["acts"]
        for challenge_item in group["challenges"]
        if challenge_item["id"] == str(challenge.id)
    )

    assert set(item) == {
        "id",
        "act_id",
        "act_number",
        "title",
        "slug",
        "category",
        "difficulty",
        "points",
        "mission_brief",
        "story_context",
        "objectives",
        "locked",
        "solved",
        "awarded_points",
    }
    assert "flag" not in str(item).lower()
    assert "story_fragment" not in item


def test_locked_challenge_detail_is_rejected(client, db_session):
    challenge = _challenge(db_session, _act(db_session, 2), title="Future Evidence")
    db_session.flush()

    response = client.get(
        f"/challenges/{challenge.id}",
        cookies=_login_team(client, db_session),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "LOCKED_CHALLENGE"


def test_draft_challenge_detail_looks_missing(client, db_session):
    challenge = _challenge(
        db_session,
        _act(db_session, 1),
        title="Unreleased Evidence",
        status=ChallengeStatus.DRAFT,
    )
    db_session.flush()

    response = client.get(
        f"/challenges/{challenge.id}",
        cookies=_login_team(client, db_session),
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
