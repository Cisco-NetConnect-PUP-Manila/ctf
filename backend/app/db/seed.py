"""Idempotent reference-data seed: Acts, categories, difficulties.

Run with:  python -m app.db.seed

Deliberately does NOT seed challenges or flags. Real flags must never live in the
repository -- challenge makers enter them through the admin panel.

Act unlock thresholds
---------------------
The handoff prose says "20 percent of the total points of the current challenge set", but
the flags table gives explicit per-Act minimums (500/700/700/700) that work out to
62-70 percent. Both are in the same document and they cannot be reconciled by any formula.

Per the website lead's decision the explicit table is seeded into
``unlock_threshold_points``, which overrides ``unlock_threshold_percent``. Organizers can
switch back to the percentage rule by clearing that column through the admin API -- no
migration needed. See backend/docs/core-loop-design.md section 6.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.act import Act
from app.models.challenge import ChallengeCategory, ChallengeDifficulty


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


def seed_acts(db: Session) -> int:
    created = 0
    for item in ACTS:
        existing = db.scalar(select(Act).where(Act.act_number == item.act_number))
        if existing is not None:
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
        created += 1
    return created


def seed_categories(db: Session) -> int:
    created = 0
    for index, (name, slug) in enumerate(CATEGORIES):
        if db.scalar(select(ChallengeCategory).where(ChallengeCategory.slug == slug)) is not None:
            continue
        db.add(ChallengeCategory(name=name, slug=slug, sort_order=index, is_active=True))
        created += 1
    return created


def seed_difficulties(db: Session) -> int:
    created = 0
    for index, (name, slug) in enumerate(DIFFICULTIES):
        if db.scalar(select(ChallengeDifficulty).where(ChallengeDifficulty.slug == slug)) is not None:
            continue
        db.add(ChallengeDifficulty(name=name, slug=slug, sort_order=index, is_active=True))
        created += 1
    return created


def run_seed(db: Session) -> dict[str, int]:
    counts = {
        "acts": seed_acts(db),
        "categories": seed_categories(db),
        "difficulties": seed_difficulties(db),
    }
    db.commit()
    return counts


def main() -> None:
    db = SessionLocal()
    try:
        counts = run_seed(db)
    finally:
        db.close()
    print(
        "Seed complete. Created "
        f"{counts['acts']} acts, {counts['categories']} categories, "
        f"{counts['difficulties']} difficulties."
    )


if __name__ == "__main__":
    main()
