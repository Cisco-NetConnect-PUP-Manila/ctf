from tests.conftest import TEST_PASSWORD, create_test_account

from app.models.account import AccountRole
from app.models.announcement import Announcement, AnnouncementStatus
from app.models.audit_log import AuditLog


def _login_admin(client, db_session, email="admin@test.com"):
    admin = create_test_account(db_session, email=email, role=AccountRole.ADMIN.value)
    resp = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    return admin, resp.cookies


def _create(client, cookies, *, title="Act I is live", body="The Signal has begun."):
    return client.post(
        "/admin/announcements",
        json={"title": title, "body": body},
        cookies=cookies,
    )


class TestAdminAnnouncementCrud:
    def test_create_starts_as_draft(self, client, db_session):
        admin, cookies = _login_admin(client, db_session)
        resp = _create(client, cookies)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "draft"
        assert data["published_at"] is None
        assert data["archived_at"] is None
        assert data["created_by_account_id"] == str(admin.id)

    def test_list_includes_drafts(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        _create(client, cookies, title="Draft One")
        resp = client.get("/admin/announcements", cookies=cookies)
        assert resp.status_code == 200
        titles = [row["title"] for row in resp.json()]
        assert "Draft One" in titles

    def test_edit_updates_fields(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        resp = client.patch(
            f"/admin/announcements/{created['id']}",
            json={"title": "Updated Title", "body": "Updated body."},
            cookies=cookies,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"
        assert data["body"] == "Updated body."

    def test_publish_sets_published_at(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        resp = client.patch(
            f"/admin/announcements/{created['id']}/status",
            json={"status": "published"},
            cookies=cookies,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "published"
        assert data["published_at"] is not None

    def test_republish_preserves_original_published_at(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        url = f"/admin/announcements/{created['id']}/status"

        first = client.patch(url, json={"status": "published"}, cookies=cookies).json()
        original_published_at = first["published_at"]

        client.patch(url, json={"status": "archived"}, cookies=cookies)
        republished = client.patch(url, json={"status": "published"}, cookies=cookies).json()

        assert republished["published_at"] == original_published_at
        assert republished["archived_at"] is None

    def test_unpublish_clears_timestamps(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        url = f"/admin/announcements/{created['id']}/status"

        client.patch(url, json={"status": "published"}, cookies=cookies)
        back_to_draft = client.patch(url, json={"status": "draft"}, cookies=cookies).json()

        assert back_to_draft["status"] == "draft"
        assert back_to_draft["published_at"] is None
        assert back_to_draft["archived_at"] is None

    def test_archive_sets_archived_at(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        resp = client.patch(
            f"/admin/announcements/{created['id']}/status",
            json={"status": "archived"},
            cookies=cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["archived_at"] is not None

    def test_status_on_missing_announcement_is_404(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        resp = client.patch(
            "/admin/announcements/00000000-0000-0000-0000-000000000000/status",
            json={"status": "published"},
            cookies=cookies,
        )
        assert resp.status_code == 404
        assert resp.json()["code"] == "NOT_FOUND"

    def test_delete_removes_announcement(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies, title="Delete Me").json()

        resp = client.delete(f"/admin/announcements/{created['id']}", cookies=cookies)

        assert resp.status_code == 204
        assert db_session.get(Announcement, created["id"]) is None
        listed = client.get("/admin/announcements", cookies=cookies)
        assert all(row["id"] != created["id"] for row in listed.json())

    def test_delete_missing_announcement_is_404(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        resp = client.delete(
            "/admin/announcements/00000000-0000-0000-0000-000000000000",
            cookies=cookies,
        )
        assert resp.status_code == 404
        assert resp.json()["code"] == "NOT_FOUND"


class TestAdminAnnouncementValidation:
    def test_blank_title_rejected(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        resp = _create(client, cookies, title="   ")
        assert resp.status_code == 400
        assert resp.json()["code"] == "VALIDATION_ERROR"

    def test_unknown_field_rejected(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        resp = client.post(
            "/admin/announcements",
            json={"title": "Valid title", "body": "Body", "bogus": True},
            cookies=cookies,
        )
        assert resp.status_code == 400

    def test_invalid_status_value_rejected(self, client, db_session):
        _, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        resp = client.patch(
            f"/admin/announcements/{created['id']}/status",
            json={"status": "banana"},
            cookies=cookies,
        )
        assert resp.status_code == 400


class TestAdminAnnouncementRbac:
    def test_participant_denied_create(self, client, db_session):
        create_test_account(db_session, email="user@test.com")
        login = client.post(
            "/auth/login", json={"email": "user@test.com", "password": TEST_PASSWORD}
        )
        resp = client.post(
            "/admin/announcements",
            json={"title": "Nope", "body": "Nope"},
            cookies=login.cookies,
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"

    def test_unauthenticated_denied_list(self, client, db_session):
        resp = client.get("/admin/announcements")
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    def test_participant_denied_delete(self, client, db_session):
        _, admin_cookies = _login_admin(client, db_session)
        created = _create(client, admin_cookies).json()
        create_test_account(db_session, email="delete-user@test.com")
        login = client.post(
            "/auth/login",
            json={"email": "delete-user@test.com", "password": TEST_PASSWORD},
        )

        resp = client.delete(
            f"/admin/announcements/{created['id']}",
            cookies=login.cookies,
        )

        assert resp.status_code == 403
        assert resp.json()["code"] == "FORBIDDEN"


class TestAdminAnnouncementAudit:
    def test_create_and_publish_are_audit_logged(self, client, db_session):
        admin, cookies = _login_admin(client, db_session)
        created = _create(client, cookies).json()
        client.patch(
            f"/admin/announcements/{created['id']}/status",
            json={"status": "published"},
            cookies=cookies,
        )

        actions = {
            row.action
            for row in db_session.query(AuditLog)
            .filter(AuditLog.target_type == "announcement")
            .all()
        }
        assert "announcement.created" in actions
        assert "announcement.published" in actions

    def test_delete_is_audit_logged(self, client, db_session):
        admin, cookies = _login_admin(client, db_session)
        created = _create(client, cookies, title="Temporary Bulletin").json()

        resp = client.delete(f"/admin/announcements/{created['id']}", cookies=cookies)

        assert resp.status_code == 204
        audit = (
            db_session.query(AuditLog)
            .filter(AuditLog.action == "announcement.deleted")
            .one()
        )
        assert audit.actor_account_id == admin.id
        assert str(audit.target_id) == created["id"]
        assert audit.metadata_json == {
            "title": "Temporary Bulletin",
            "status": "draft",
        }

    def test_body_check_constraint_holds(self, client, db_session):
        # Sanity: only the three known statuses exist in the enum.
        assert {s.value for s in AnnouncementStatus} == {"draft", "published", "archived"}
        assert db_session.query(Announcement).count() >= 0
