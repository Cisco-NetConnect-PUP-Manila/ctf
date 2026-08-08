"""Seed initial platform settings and reference data for local development.

Idempotent: safe to re-run. Deliberately seeds no challenges and no flags -- real flags
must never live in the repository, so challenge makers enter them through the admin panel.

Act unlock thresholds
---------------------
The handoff prose says "20 percent of the total points of the current challenge set", but
the flags table gives explicit per-Act minimums (500/700/700/700) that work out to
62-70 percent. Both are in the same document and no formula reconciles them.

Per the website lead's decision the explicit table is seeded into
``unlock_threshold_points``, which overrides ``unlock_threshold_percent``. Organizers can
switch back to the percentage rule by clearing that column through the admin API -- no
migration needed. See backend/docs/core-loop-design.md section 6.
"""

from dataclasses import dataclass

import app.models  # noqa: F401  -- registers every mapper before any query runs
from app.db.session import SessionLocal
from app.models.act import Act
from app.models.challenge import ChallengeCategory, ChallengeDifficulty
from app.models.platform_setting import PlatformSetting


@dataclass(frozen=True)
class ActSeed:
    act_number: int
    slug: str
    title: str
    description: str
    unlock_threshold_points: int


ACTS: tuple[ActSeed, ...] = (
    ActSeed(
        act_number=1,
        slug="the-signal",
        title="Act I - The Signal",
        description="Open-source intelligence. Every investigation begins with a single anomaly.",
        unlock_threshold_points=500,
    ),
    ActSeed(
        act_number=2,
        slug="the-breach",
        title="Act II - The Breach",
        description="Web penetration testing. Abandoned applications that were never meant to be found.",
        unlock_threshold_points=700,
    ),
    ActSeed(
        act_number=3,
        slug="the-echo",
        title="Act III - The Echo",
        description="Digital forensics. Every deleted file leaves behind a memory.",
        unlock_threshold_points=700,
    ),
    ActSeed(
        act_number=4,
        slug="beneath-the-network",
        title="Act IV - Beneath the Network",
        description="Cisco Packet Tracer. The final layer is hidden in the network itself.",
        # Gates nothing in the core loop -- there is no Act V. It presumably gates the
        # Final Investigation (issue #22); confirm with organizers before relying on it.
        unlock_threshold_points=700,
    ),
)

CATEGORIES: tuple[tuple[str, str], ...] = (
    ("OSINT", "osint"),
    ("Web Penetration Testing", "web-penetration-testing"),
    ("Digital Forensics", "digital-forensics"),
    ("Cisco Packet Tracer", "cisco-packet-tracer"),
)

DIFFICULTIES: tuple[tuple[str, str], ...] = (
    ("Easy", "easy"),
    ("Medium", "medium"),
    ("Hard", "hard"),
    ("Expert", "expert"),
)


def run_seed(db):
    """Seed into a caller-provided session. Does not commit."""
    _seed_platform_settings(db)
    _seed_acts(db)
    _seed_categories(db)
    _seed_difficulties(db)


def seed():
    db = SessionLocal()
    try:
        run_seed(db)
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


def _seed_acts(db):
    for item in ACTS:
        if db.query(Act).filter_by(act_number=item.act_number).first() is not None:
            print(f"  Already exists: act {item.act_number}")
            continue
        db.add(
            Act(
                act_number=item.act_number,
                slug=item.slug,
                title=item.title,
                description=item.description,
                unlock_threshold_points=item.unlock_threshold_points,
                unlock_threshold_percent=20,
                sort_order=item.act_number,
                is_active=True,
            )
        )
        print(f"  Created act: {item.act_number} = {item.title}")


def _seed_categories(db):
    for index, (name, slug) in enumerate(CATEGORIES):
        if db.query(ChallengeCategory).filter_by(slug=slug).first() is not None:
            continue
        db.add(ChallengeCategory(name=name, slug=slug, sort_order=index, is_active=True))
        print(f"  Created challenge_category: {name}")


def _seed_difficulties(db):
    for index, (name, slug) in enumerate(DIFFICULTIES):
        if db.query(ChallengeDifficulty).filter_by(slug=slug).first() is not None:
            continue
        db.add(ChallengeDifficulty(name=name, slug=slug, sort_order=index, is_active=True))
        print(f"  Created challenge_difficulty: {name}")


if __name__ == "__main__":
    seed()
