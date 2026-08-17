import uuid
from pathlib import Path

from sqlalchemy import select

from tests.conftest import TEST_PASSWORD, create_test_account, create_test_team

from app.core.config import settings
from app.models.account import AccountRole
from app.models.act import Act
from app.models.audit_log import AuditLog
from app.models.challenge import Challenge, ChallengeFile, ChallengeStatus
from app.models.team import TeamStatus
from app.services.platform_settings import KEY_SUBMISSIONS_OPEN
from app.models.platform_setting import PlatformSetting


def _act(db_session, number: int = 1) -> Act:
    existing = db_session.scalar(select(Act).where(Act.act_number == number))
    if existing is not None:
        return existing

    act = Act(
        act_number=number,
        slug=f"files-act-{number}-{uuid.uuid4().hex[:6]}",
        title=f"Files Act {number}",
        description="Evidence handling tests.",
        unlock_threshold_percent=20,
        sort_order=number,
        is_active=True,
    )
    db_session.add(act)
    db_session.flush()
    return act


def _challenge(db_session, act: Act, title: str = "Packet Evidence") -> Challenge:
    challenge = Challenge(
        act_id=act.id,
        title=title,
        slug=f"packet-evidence-{uuid.uuid4().hex[:8]}",
        mission_brief="Inspect the private evidence.",
        objectives_json=["Download the artifact"],
        points=100,
        status=ChallengeStatus.PUBLISHED.value,
        is_visible=True,
        sort_order=0,
    )
    db_session.add(challenge)
    db_session.flush()
    return challenge


def _login_admin(client, db_session):
    create_test_account(db_session, email="file-admin@test.com", role=AccountRole.ADMIN.value)
    response = client.post(
        "/auth/login",
        json={"email": "file-admin@test.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    return response.cookies


def _login_team(client, db_session):
    email = f"file-team-{uuid.uuid4().hex[:8]}@test.com"
    account = create_test_account(db_session, email=email)
    create_test_team(
        db_session,
        account,
        group_name=f"File Team {uuid.uuid4().hex[:6]}",
        team_status=TeamStatus.APPROVED.value,
    )
    response = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200
    return response.cookies


def test_admin_uploads_allowed_challenge_file(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    challenge = _challenge(db_session, _act(db_session))
    cookies = _login_admin(client, db_session)

    response = client.post(
        f"/admin/challenges/{challenge.id}/files",
        data={"display_name": "Traffic Capture"},
        files={"upload": ("original-name.pcap", b"pcap bytes", "application/vnd.tcpdump.pcap")},
        cookies=cookies,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["display_name"] == "Traffic Capture"
    assert body["original_filename"] == "original-name.pcap"
    assert body["extension"] == ".pcap"
    assert body["size_bytes"] == len(b"pcap bytes")

    row = db_session.scalar(select(ChallengeFile).where(ChallengeFile.id == body["id"]))
    assert row is not None
    assert "original-name" not in row.storage_key
    assert (Path(tmp_path) / row.storage_key).is_file()


def test_admin_upload_rejects_unsupported_extension(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    challenge = _challenge(db_session, _act(db_session))
    cookies = _login_admin(client, db_session)

    response = client.post(
        f"/admin/challenges/{challenge.id}/files",
        files={"upload": ("malware.exe", b"nope", "application/octet-stream")},
        cookies=cookies,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert db_session.query(ChallengeFile).count() == 0


def test_unauthenticated_user_cannot_upload_challenge_file(
    client, db_session, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    challenge = _challenge(db_session, _act(db_session))

    response = client.post(
        f"/admin/challenges/{challenge.id}/files",
        files={"upload": ("evidence.txt", b"private", "text/plain")},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_REQUIRED"
    assert db_session.query(ChallengeFile).count() == 0
    assert list(Path(tmp_path).rglob("*")) == []


def test_participant_cannot_upload_challenge_file(
    client, db_session, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    challenge = _challenge(db_session, _act(db_session))
    team_cookies = _login_team(client, db_session)

    response = client.post(
        f"/admin/challenges/{challenge.id}/files",
        files={"upload": ("evidence.txt", b"private", "text/plain")},
        cookies=team_cookies,
    )

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
    assert db_session.query(ChallengeFile).count() == 0
    assert list(Path(tmp_path).rglob("*")) == []


def test_oversized_upload_leaves_no_file_or_metadata(
    client, db_session, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    monkeypatch.setattr(settings, "challenge_file_max_bytes", 4)
    challenge = _challenge(db_session, _act(db_session))
    cookies = _login_admin(client, db_session)

    response = client.post(
        f"/admin/challenges/{challenge.id}/files",
        files={"upload": ("too-large.raw", b"12345", "application/octet-stream")},
        cookies=cookies,
    )

    assert response.status_code == 413
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert db_session.query(ChallengeFile).count() == 0
    assert [path for path in Path(tmp_path).rglob("*") if path.is_file()] == []


def test_admin_deactivates_file_without_deleting_metadata(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    challenge = _challenge(db_session, _act(db_session))
    cookies = _login_admin(client, db_session)
    uploaded = client.post(
        f"/admin/challenges/{challenge.id}/files",
        files={"upload": ("evidence.txt", b"notes", "text/plain")},
        cookies=cookies,
    ).json()

    response = client.delete(
        f"/admin/challenges/{challenge.id}/files/{uploaded['id']}",
        cookies=cookies,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    row = db_session.get(ChallengeFile, uploaded["id"])
    assert row is not None
    assert row.deactivated_at is not None
    assert db_session.query(AuditLog).filter(AuditLog.action == "challenge_file.deactivated").count() == 1


def test_admin_reactivates_existing_challenge_file(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    challenge = _challenge(db_session, _act(db_session))
    cookies = _login_admin(client, db_session)
    uploaded = client.post(
        f"/admin/challenges/{challenge.id}/files",
        files={"upload": ("evidence.txt", b"notes", "text/plain")},
        cookies=cookies,
    ).json()
    client.delete(
        f"/admin/challenges/{challenge.id}/files/{uploaded['id']}",
        cookies=cookies,
    )

    response = client.patch(
        f"/admin/challenges/{challenge.id}/files/{uploaded['id']}/reactivate",
        cookies=cookies,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True
    row = db_session.get(ChallengeFile, uploaded["id"])
    assert row is not None
    assert row.deactivated_at is None
    assert db_session.query(AuditLog).filter(
        AuditLog.action == "challenge_file.reactivated"
    ).count() == 1


def test_participant_downloads_only_unlocked_active_files(client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "challenge_file_storage_root", str(tmp_path))
    db_session.add(PlatformSetting(key=KEY_SUBMISSIONS_OPEN, value_json=True))
    db_session.flush()
    open_challenge = _challenge(db_session, _act(db_session, 1), title="Open Evidence")
    locked_challenge = _challenge(db_session, _act(db_session, 2), title="Locked Evidence")
    admin_cookies = _login_admin(client, db_session)
    team_cookies = _login_team(client, db_session)

    opened = client.post(
        f"/admin/challenges/{open_challenge.id}/files",
        files={"upload": ("traffic.raw", b"raw bytes", "application/octet-stream")},
        cookies=admin_cookies,
    ).json()
    locked = client.post(
        f"/admin/challenges/{locked_challenge.id}/files",
        files={"upload": ("future.raw", b"locked bytes", "application/octet-stream")},
        cookies=admin_cookies,
    ).json()

    list_response = client.get(f"/challenges/{open_challenge.id}/files", cookies=team_cookies)
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == opened["id"]

    download = client.get(
        f"/challenges/{open_challenge.id}/files/{opened['id']}/download",
        cookies=team_cookies,
    )
    assert download.status_code == 200
    assert download.content == b"raw bytes"

    locked_response = client.get(f"/challenges/{locked_challenge.id}/files", cookies=team_cookies)
    assert locked_response.status_code == 422
    assert locked_response.json()["code"] == "LOCKED_CHALLENGE"

    client.delete(f"/admin/challenges/{open_challenge.id}/files/{opened['id']}", cookies=admin_cookies)
    inactive_download = client.get(
        f"/challenges/{open_challenge.id}/files/{opened['id']}/download",
        cookies=team_cookies,
    )
    assert inactive_download.status_code == 404
    assert locked["original_filename"] == "future.raw"
