"""Admin-only submission monitoring.

This intentionally never returns submitted flag values. Correct flags are never previewed,
and even incorrect attempts are represented only by existing metadata and aggregates.
"""

from collections import defaultdict
from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.session import get_db
from app.models.challenge import Challenge
from app.models.submission import Solve, Submission
from app.models.team import Team
from app.schemas.admin_submission import (
    AdminLeaderboardResponse,
    AdminLeaderboardRow,
    AdminSubmissionMonitorResponse,
    AdminSubmissionMonitorRow,
)
from app.services import scoring

router = APIRouter()

RAPID_SOLVE_SECONDS = 90


@router.get("/submission-monitor", response_model=AdminSubmissionMonitorResponse)
def submission_monitor(db: Session = Depends(get_db)) -> AdminSubmissionMonitorResponse:
    attempts = db.execute(
        select(Submission, Team.group_name, Challenge.title)
        .join(Team, Team.id == Submission.team_id)
        .join(Challenge, Challenge.id == Submission.challenge_id)
        .order_by(Submission.submitted_at.desc())
    ).all()
    solves = {
        (row.team_id, row.challenge_id): row.solved_at
        for row in db.scalars(select(Solve)).all()
    }

    grouped: dict[tuple, dict] = {}
    ip_hash_teams: dict[tuple, set] = defaultdict(set)
    ua_hash_teams: dict[tuple, set] = defaultdict(set)

    for attempt, team_name, challenge_title in attempts:
        key = (attempt.team_id, attempt.challenge_id)
        item = grouped.setdefault(
            key,
            {
                "challenge_id": attempt.challenge_id,
                "challenge_title": challenge_title,
                "team_id": attempt.team_id,
                "team_name": team_name,
                "correct_attempts": 0,
                "incorrect_attempts": 0,
                "first_attempt_at": None,
                "last_attempt_at": None,
                "first_correct_at": None,
            },
        )

        submitted_at = attempt.submitted_at
        if item["first_attempt_at"] is None or submitted_at < item["first_attempt_at"]:
            item["first_attempt_at"] = submitted_at
        if item["last_attempt_at"] is None or submitted_at > item["last_attempt_at"]:
            item["last_attempt_at"] = submitted_at

        if attempt.is_correct:
            item["correct_attempts"] += 1
            if item["first_correct_at"] is None or submitted_at < item["first_correct_at"]:
                item["first_correct_at"] = submitted_at
        else:
            item["incorrect_attempts"] += 1

        if attempt.ip_address_hash:
            ip_hash_teams[(attempt.challenge_id, attempt.ip_address_hash)].add(attempt.team_id)
        if attempt.user_agent_hash:
            ua_hash_teams[(attempt.challenge_id, attempt.user_agent_hash)].add(attempt.team_id)

    rows: list[AdminSubmissionMonitorRow] = []
    for key, item in grouped.items():
        team_id, challenge_id = key
        first_attempt_at: datetime | None = item["first_attempt_at"]
        first_correct_at: datetime | None = item["first_correct_at"]
        solved_at = solves.get(key)
        seconds_to_solve = None
        if first_attempt_at and first_correct_at:
            seconds_to_solve = max(
                0,
                int((first_correct_at - first_attempt_at).total_seconds()),
            )

        ip_shared = 0
        ua_shared = 0
        for (seen_challenge_id, _), teams in ip_hash_teams.items():
            if seen_challenge_id == challenge_id and team_id in teams:
                ip_shared = max(ip_shared, len(teams))
        for (seen_challenge_id, _), teams in ua_hash_teams.items():
            if seen_challenge_id == challenge_id and team_id in teams:
                ua_shared = max(ua_shared, len(teams))

        notes: list[str] = []
        rapid = (
            first_correct_at is not None
            and item["incorrect_attempts"] == 0
            and seconds_to_solve is not None
            and seconds_to_solve <= RAPID_SOLVE_SECONDS
        )
        if rapid:
            notes.append("Correct on first attempt very quickly.")
        if ip_shared > 1:
            notes.append("IP hash also appears for another team on this challenge.")
        if ua_shared > 1:
            notes.append("User-agent hash also appears for another team on this challenge.")

        rows.append(
            AdminSubmissionMonitorRow(
                challenge_id=challenge_id,
                challenge_title=item["challenge_title"],
                team_id=team_id,
                team_name=item["team_name"],
                solved_at=solved_at,
                correct_attempts=item["correct_attempts"],
                incorrect_attempts=item["incorrect_attempts"],
                first_attempt_at=first_attempt_at,
                last_attempt_at=item["last_attempt_at"],
                first_correct_at=first_correct_at,
                seconds_to_solve=seconds_to_solve,
                shared_ip_hash_team_count=ip_shared,
                shared_user_agent_hash_team_count=ua_shared,
                rapid_solve=rapid,
                suspicious_notes=notes,
            )
        )

    rows.sort(
        key=lambda row: (
            bool(row.suspicious_notes),
            row.solved_at or row.last_attempt_at or datetime.min.replace(tzinfo=UTC),
        ),
        reverse=True,
    )
    return AdminSubmissionMonitorResponse(rows=rows)


@router.get("/leaderboard", response_model=AdminLeaderboardResponse)
def leaderboard(db: Session = Depends(get_db)) -> AdminLeaderboardResponse:
    teams = db.scalars(select(Team).order_by(Team.group_name)).all()
    solves = db.scalars(select(Solve)).all()
    submissions = db.scalars(select(Submission)).all()

    solves_by_team: dict = defaultdict(list)
    submissions_by_team: dict = defaultdict(list)
    for solve in solves:
        solves_by_team[solve.team_id].append(solve)
    for submission in submissions:
        submissions_by_team[submission.team_id].append(submission)

    ranked = []
    for team in teams:
        team_solves = solves_by_team.get(team.id, [])
        team_submissions = submissions_by_team.get(team.id, [])
        last_solve_at = max((solve.solved_at for solve in team_solves), default=None)
        ranked.append(
            {
                "team": team,
                "score": scoring.compute_investigation_score(db, team.id),
                "current_act": scoring.current_act_number(db, team.id),
                "solves": len(team_solves),
                "attempts": len(team_submissions),
                "incorrect_attempts": sum(1 for item in team_submissions if not item.is_correct),
                "last_solve_at": last_solve_at,
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["score"],
            item["last_solve_at"] or datetime.max.replace(tzinfo=UTC),
            item["team"].group_name.lower(),
        )
    )

    rows = [
        AdminLeaderboardRow(
            rank=index + 1,
            team_id=item["team"].id,
            team_name=item["team"].group_name,
            team_status=item["team"].status,
            member_count=len(item["team"].members),
            score=item["score"],
            current_act=item["current_act"],
            solves=item["solves"],
            attempts=item["attempts"],
            incorrect_attempts=item["incorrect_attempts"],
            last_solve_at=item["last_solve_at"],
        )
        for index, item in enumerate(ranked)
    ]
    return AdminLeaderboardResponse(rows=rows)
