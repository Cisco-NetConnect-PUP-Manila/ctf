from tests.conftest import (
    TEST_PASSWORD,
    create_test_account,
    create_test_team,
    seed_registration_open,
)


def build_payload(*, group_name="New Team", email="team@test.com", password=TEST_PASSWORD, members=None):
    if members is None:
        members = [
            {"full_name": "Leader Name", "email": email},
            {"full_name": "Member Two", "email": "two@test.com"},
            {"full_name": "Member Three", "email": "three@test.com"},
            {"full_name": "Member Four", "email": "four@test.com"},
        ]
    return {"group_name": group_name, "email": email, "password": password, "members": members}


class TestRegistration:
    def test_pydantic_validation_short_password(self, client, db_session):
        seed_registration_open(db_session, True)
        payload = build_payload(password="short")
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "password" in data["field_errors"]

    def test_registration_closed(self, client, db_session):
        seed_registration_open(db_session, False)
        resp = client.post("/auth/register", json=build_payload())
        assert resp.status_code == 403
        assert resp.json()["code"] == "REGISTRATION_CLOSED"

    def test_email_taken(self, client, db_session):
        seed_registration_open(db_session, True)
        create_test_account(db_session, email="team@test.com")
        resp = client.post("/auth/register", json=build_payload())
        assert resp.status_code == 409
        assert resp.json()["code"] == "EMAIL_TAKEN"

    def test_group_name_taken(self, client, db_session):
        seed_registration_open(db_session, True)
        account = create_test_account(db_session, email="existing@test.com")
        create_test_team(db_session, account, group_name="My Team")
        resp = client.post("/auth/register", json=build_payload(group_name="My Team"))
        assert resp.status_code == 409
        assert resp.json()["code"] == "GROUP_NAME_TAKEN"

    def test_duplicate_member_emails(self, client, db_session):
        seed_registration_open(db_session, True)
        payload = build_payload(members=[
            {"full_name": "A", "email": "team@test.com"},
            {"full_name": "B", "email": "team@test.com"},
            {"full_name": "C", "email": "three@test.com"},
            {"full_name": "D", "email": "four@test.com"},
        ])
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "members" in data["field_errors"]

    def test_login_email_not_in_members(self, client, db_session):
        seed_registration_open(db_session, True)
        payload = build_payload(
            email="outsider@test.com",
            members=[
                {"full_name": "A", "email": "a@test.com"},
                {"full_name": "B", "email": "b@test.com"},
                {"full_name": "C", "email": "c@test.com"},
                {"full_name": "D", "email": "d@test.com"},
            ],
        )
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert data["code"] == "VALIDATION_ERROR"
        assert "email" in data["field_errors"]

    def test_successful_registration(self, client, db_session):
        seed_registration_open(db_session, True)
        resp = client.post("/auth/register", json=build_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["account"]["email"] == "team@test.com"
        assert data["account"]["role"] == "participant"
        assert data["account"]["status"] == "active"
        assert data["team"]["group_name"] == "New Team"
        assert data["team"]["status"] == "pending"
        assert len(data["team"]["members"]) == 4
        assert data["team"]["members"][0]["is_leader"] is True
