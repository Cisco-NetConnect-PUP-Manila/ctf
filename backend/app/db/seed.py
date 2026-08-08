"""Seed initial platform settings and default data for local development."""

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.platform_setting import PlatformSetting


def seed():
    db = SessionLocal()
    try:
        _seed_platform_settings(db)
        db.commit()
        print("Seed completed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _seed_platform_settings(db):
    defaults = {
        "registration_open": True,
    }
    for key, value in defaults.items():
        existing = db.query(PlatformSetting).filter_by(key=key).first()
        if existing is None:
            db.add(PlatformSetting(key=key, value_json=value))
            print(f"  Created platform_setting: {key} = {value}")
        else:
            print(f"  Already exists: {key}")


if __name__ == "__main__":
    seed()
