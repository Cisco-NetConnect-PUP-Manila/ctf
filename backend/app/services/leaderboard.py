from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.act import Act, ActUnlock
from app.models.intel import IntelRequest
from app.models.submission import Solve
from app.models.team import Team, TeamStatus


@dataclass(frozen=True)
class LeaderboardEntry:
    rank: int
    team_id: UUID
    team_name: str
    investigation_score: int
    solved_count: int
    current_act: int
    intel_penalty: int
    last_solve_at: datetime | None


def calculate_leaderboard(db: Session) -> list[LeaderboardEntry]:
    """Calculate participant-safe rankings from authoritative score records.

    Only approved teams are public. Solve points and Intel penalties are snapshots, so
    later challenge or hint edits cannot rewrite competition history.
    """
    teams = db.execute(
        select(Team.id, Team.group_name)
        .where(Team.status == TeamStatus.APPROVED.value)
        .order_by(Team.group_name)
    ).all()

    solve_rows = db.execute(
        select(
            Solve.team_id,
            func.coalesce(func.sum(Solve.points_awarded), 0),
            func.count(Solve.id),
            func.max(Solve.solved_at),
        ).group_by(Solve.team_id)
    ).all()
    solves = {
        team_id: {
            "points": int(points or 0),
            "count": int(count or 0),
            "last_solve_at": last_solve_at,
        }
        for team_id, points, count, last_solve_at in solve_rows
    }

    penalties = {
        team_id: int(total or 0)
        for team_id, total in db.execute(
            select(
                IntelRequest.team_id,
                func.coalesce(func.sum(IntelRequest.penalty_points), 0),
            ).group_by(IntelRequest.team_id)
        ).all()
    }

    current_acts = {
        team_id: int(act_number or 0)
        for team_id, act_number in db.execute(
            select(ActUnlock.team_id, func.max(Act.act_number))
            .join(Act, Act.id == ActUnlock.act_id)
            .where(ActUnlock.revoked_at.is_(None), Act.is_active.is_(True))
            .group_by(ActUnlock.team_id)
        ).all()
    }

    ranked: list[dict] = []
    for team_id, team_name in teams:
        solve = solves.get(
            team_id,
            {"points": 0, "count": 0, "last_solve_at": None},
        )
        penalty = penalties.get(team_id, 0)
        ranked.append(
            {
                "team_id": team_id,
                "team_name": team_name,
                "investigation_score": solve["points"] - penalty,
                "solved_count": solve["count"],
                "current_act": current_acts.get(team_id, 0),
                "intel_penalty": penalty,
                "last_solve_at": solve["last_solve_at"],
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["investigation_score"],
            item["last_solve_at"] or datetime.max.replace(tzinfo=UTC),
            item["team_name"].casefold(),
        )
    )

    return [
        LeaderboardEntry(rank=index + 1, **item)
        for index, item in enumerate(ranked)
    ]
