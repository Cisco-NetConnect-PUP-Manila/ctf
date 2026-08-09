from datetime import UTC, datetime, timedelta

from tests.conftest import TEST_PASSWORD, create_test_account

from app.models.account import AccountRole
from app.models.announcement import Announcement, AnnouncementStatus


def _make(db_session, *, title, status, published_at=None):
    row = Announcement(
        title=title,
        body=f"Body for {title}",
        status=status.value,
        published_at=published_at,
    )
    db_session.add(row)
    db_session.flush()
    return row


def _login_participant(client, db_session, email="user@test.com"):
    create_test_account(db_session, email=email)
    resp = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    return resp.cookies


class TestParticipantAnnouncementsFeed:
    def test_requires_authentication(self, client, db_session):
        resp = client.get("/announcements")
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    def test_only_published_are_returned(self, client, db_session):
        now = datetime.now(UTC)
        _make(db_session, title="Draft", status=AnnouncementStatus.DRAFT)
        _make(db_session, title="Published", status=AnnouncementStatus.PUBLISHED, published_at=now)
        _make(db_session, title="Archived", status=AnnouncementStatus.ARCHIVED, published_at=now)

        cookies = _login_participant(client, db_session)
        resp = client.get("/announcements", cookies=cookies)
        assert resp.status_code == 200
        body = resp.json()
        titles = [item["title"] for item in body["items"]]
        assert titles == ["Published"]
        assert body["total"] == 1

    def test_response_shape_hides_internal_fields(self, client, db_session):
        _make(
            db_session,
            title="Published",
            status=AnnouncementStatus.PUBLISHED,
            published_at=datetime.now(UTC),
        )
        cookies = _login_participant(client, db_session)
        item = client.get("/announcements", cookies=cookies).json()["items"][0]
        assert set(item.keys()) == {"id", "title", "body", "published_at"}
        assert "status" not in item
        assert "created_by_account_id" not in item

    def test_newest_published_first(self, client, db_session):
        now = datetime.now(UTC)
        _make(
            db_session,
            title="Older",
            status=AnnouncementStatus.PUBLISHED,
            published_at=now - timedelta(hours=2),
        )
        _make(
            db_session,
            title="Newer",
            status=AnnouncementStatus.PUBLISHED,
            published_at=now,
        )
        cookies = _login_participant(client, db_session)
        titles = [i["title"] for i in client.get("/announcements", cookies=cookies).json()["items"]]
        assert titles == ["Newer", "Older"]

    def test_pagination_envelope(self, client, db_session):
        now = datetime.now(UTC)
        for n in range(3):
            _make(
                db_session,
                title=f"Published {n}",
                status=AnnouncementStatus.PUBLISHED,
                published_at=now - timedelta(minutes=n),
            )
        cookies = _login_participant(client, db_session)

        page1 = client.get("/announcements?page=1&page_size=2", cookies=cookies).json()
        assert page1["total"] == 3
        assert page1["page_size"] == 2
        assert len(page1["items"]) == 2
        assert page1["has_more"] is True

        page2 = client.get("/announcements?page=2&page_size=2", cookies=cookies).json()
        assert len(page2["items"]) == 1
        assert page2["has_more"] is False

    def test_admin_may_also_read_feed(self, client, db_session):
        _make(
            db_session,
            title="Published",
            status=AnnouncementStatus.PUBLISHED,
            published_at=datetime.now(UTC),
        )
        create_test_account(db_session, email="admin@test.com", role=AccountRole.ADMIN.value)
        login = client.post(
            "/auth/login", json={"email": "admin@test.com", "password": TEST_PASSWORD}
        )
        resp = client.get("/announcements", cookies=login.cookies)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
