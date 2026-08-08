# Packet Capture API Contract v1

Version: 1.0.0
Status: FROZEN
Owner: Dev 1
Created: 2026-08-07
Related: GitHub Issue 18 (Prepare API Contract Before Full Frontend Integration)
Supersedes: Developer Guide §13–14 (starting map only — do not treat as final)

This document is the single source of truth for the first-version API. Frontend and
backend developers build against this contract and do not guess endpoint names,
payload shapes, roles, or errors. If something here conflicts with a chat message or
older note, stop and ask the website lead.

## 1. Conventions

- Base URL (local dev): `http://localhost:8001`. Production URL is set later by the lead.
- Auth: HTTP-only session cookie `packet_capture_session`, `SameSite=Lax`, `Secure` in
  staging/production. Frontend must send `credentials: "include"` (fetch) or the
  equivalent. Never store the token in localStorage.
- JSON fields are snake_case. IDs are UUIDs. Datetimes are UTC ISO-8601
  (e.g. `2026-08-07T09:00:00Z`). Convert to local time only for display.
- Real flags, validator logic, and secrets are NEVER returned by any endpoint.
- Public flag format is the sample `PacketCapture{FLAG_NAME}`. Final flags are pending
  organizer confirmation.
- List endpoints return a pagination envelope (see §5).
- HTTP status codes: use the mapping in §4.

## 2. Roles And Access

| Role | Access |
| --- | --- |
| Public | `/health`, `/auth/register`, `/auth/login` |
| Participant | `/auth/me`, `/auth/logout`, `/challenges`, `/challenges/{id}`, `/challenges/{id}/submissions`, `/challenges/{id}/intel-requests`, `/leaderboard`, `/announcements` |
| Admin | All participant endpoints plus every `/admin/*` endpoint |

Rules:

- Participant endpoints require an active session.
- `/admin/*` requires an account with role `admin`.
- Every protected endpoint checks role and account/team status server-side. The
  frontend never decides scoring, unlocks, solves, penalties, or permissions.
- Teams with `status = pending` may log in but cannot access participant challenges
  until approved.

## 3. Error Contract

Every error response uses this envelope:

```json
{
  "code": "CHALLENGE_LOCKED",
  "message": "This challenge is not available yet.",
  "field_errors": {}
}
```

- `code`: stable machine-readable string (see table below).
- `message`: human-readable message for display.
- `field_errors`: optional object mapping field name to message(s), used for
  validation failures on requests with bodies.

| HTTP | code | Meaning |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | Request body/query failed validation (with `field_errors`) |
| 401 | `AUTH_REQUIRED` | No session cookie present |
| 401 | `SESSION_EXPIRED` | Session missing, revoked, or expired |
| 403 | `ACCOUNT_DISABLED` | Account is disabled |
| 403 | `FORBIDDEN` | Role lacks access to this endpoint |
| 403 | `TEAM_NOT_APPROVED` | Team exists but is not approved |
| 403 | `REGISTRATION_CLOSED` | Registration is not open |
| 403 | `SUBMISSIONS_CLOSED` | Competition is not open for submissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `EMAIL_TAKEN` | Email already registered |
| 409 | `GROUP_NAME_TAKEN` | Group name already registered |
| 422 | `LOCKED_CHALLENGE` | Challenge is locked / not accessible to this team |
| 422 | `ALREADY_SOLVED` | Challenge already solved by this team |
| 429 | `RATE_LIMITED` | Too many requests (login, submission) |
| 500 | `INTERNAL_ERROR` | Unexpected server failure |

> Note: the merged backend currently returns plain `detail` strings. This envelope is
> the target contract; aligning the backend to it is a tracked follow-up.

## 4. Endpoint Map

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/health` | Public | Backend health check |
| GET | `/health/db` | Public | Database reachability check |
| POST | `/auth/register` | Public | Register a team |
| POST | `/auth/login` | Public | Create session |
| POST | `/auth/logout` | Authenticated | End session |
| GET | `/auth/me` | Authenticated | Current account + team |
| GET | `/challenges` | Participant | Accessible challenges |
| GET | `/challenges/{id}` | Participant | Challenge details |
| POST | `/challenges/{id}/submissions` | Participant | Submit a flag |
| POST | `/challenges/{id}/intel-requests` | Participant | Request an Intel/hint |
| GET | `/leaderboard` | Participant | Ranked teams |
| GET | `/announcements` | Participant | Published announcements |
| POST | `/admin/challenges` | Admin | Create challenge |
| PATCH | `/admin/challenges/{id}` | Admin | Edit challenge |
| PATCH | `/admin/challenges/{id}/publish` | Admin | Publish/archive challenge |
| GET | `/admin/submissions` | Admin | Submission logs |
| GET | `/admin/audit-logs` | Admin | Audit logs |
| PATCH | `/admin/platform-settings` | Admin | Update event settings |
| PATCH | `/admin/teams/{id}/approve` | Admin | Approve a pending team |
| PATCH | `/admin/teams/{id}/reject` | Admin | Reject a pending team |

## 5. Response Models

Pagination envelope for list endpoints:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

Account:

```json
{
  "id": "uuid",
  "email": "team@example.com",
  "role": "participant",
  "status": "active"
}
```

Team:

```json
{
  "id": "uuid",
  "group_name": "Group Name",
  "status": "pending",
  "members": [
    { "id": "uuid", "full_name": "Jane Doe", "email": "team@example.com", "is_leader": true }
  ]
}
```

Me (nested shape used by `/auth/register`, `/auth/login`, `/auth/me`):

```json
{
  "account": { "id": "uuid", "email": "team@example.com", "role": "participant", "status": "active" },
  "team": { "id": "uuid", "group_name": "Group Name", "status": "pending", "members": [] }
}
```

> Decision: auth responses use the nested `{account, team}` shape to match the merged
> backend. Team `status` values: `pending`, `approved`, `rejected`, `disabled`.

Challenge (participant view):

```json
{
  "id": "uuid",
  "act_id": "uuid",
  "title": "Hidden Profile",
  "category": "OSINT",
  "difficulty": "easy",
  "points": 50,
  "visible": true,
  "locked": false,
  "solved": false,
  "files": [],
  "hints_available": 2
}
```

SubmissionResult:

```json
{
  "correct": true,
  "awarded_points": 50,
  "current_score": 150,
  "solved": true,
  "message": "Correct.",
  "next_act_unlocked": null
}
```

LeaderboardRow:

```json
{
  "rank": 1,
  "team_name": "Group Name",
  "score": 800,
  "solved_count": 6,
  "current_act": 2,
  "last_solve_time": "2026-08-07T09:00:00Z",
  "penalties": 25
}
```

Announcement:

```json
{
  "id": "uuid",
  "title": "Act I is live",
  "body": "The Signal has begun.",
  "published_at": "2026-08-07T09:00:00Z"
}
```

## 6. Endpoint Details

### 6.1 Auth

**POST /auth/register** (Public)

Request:

```json
{
  "group_name": "Team Alpha",
  "email": "team@example.com",
  "password": "min-12-chars",
  "members": [
    { "full_name": "Jane Doe", "email": "team@example.com" },
    { "full_name": "John Doe", "email": "john@example.com" },
    { "full_name": "Sam Smith", "email": "sam@example.com" },
    { "full_name": "Alex Lee", "email": "alex@example.com" }
  ]
}
```

- `members` must have 4–5 entries. One entry must match the login `email`; that member
  becomes the leader.
- 201 → Me model. Errors: `REGISTRATION_CLOSED`, `VALIDATION_ERROR`, `EMAIL_TAKEN`,
  `GROUP_NAME_TAKEN`.

> Pending organizer confirmation: final team-size rule. Contract keeps the 4–5 roster.

**POST /auth/login** (Public)

Request: `{ "email": "...", "password": "..." }`. Response: Me model + sets
`packet_capture_session` cookie. Errors: `VALIDATION_ERROR` (invalid credentials),
`ACCOUNT_DISABLED`.

**POST /auth/logout** (Authenticated)

Response: 204, clears cookie.

**GET /auth/me** (Authenticated)

Response: Me model. Errors: `AUTH_REQUIRED`, `SESSION_EXPIRED`.

### 6.2 Challenges

**GET /challenges** (Participant)

Response: pagination envelope of Challenge. Only published, Act-accessible challenges.
Locked Acts appear with `locked: true` rather than disappearing.

**GET /challenges/{id}** (Participant)

Response: Challenge details including mission brief/story context/objectives (fields
listed in §7 admin fields are not exposed to participants). Errors: `NOT_FOUND`,
`LOCKED_CHALLENGE`.

### 6.3 Submissions

**POST /challenges/{id}/submissions** (Participant)

Request:

```json
{ "flag": "PacketCapture{PHANTOM_TRACE}" }
```

Response: SubmissionResult. Errors: `AUTH_REQUIRED`, `TEAM_NOT_APPROVED`,
`SUBMISSIONS_CLOSED`, `NOT_FOUND`, `LOCKED_CHALLENGE`, `ALREADY_SOLVED`,
`RATE_LIMITED`.

Rules: backend validates the flag; incorrect submissions award nothing; duplicate
correct submissions award 0 (no double points); scoring and Act-unlock updates happen
in one backend transaction.

### 6.4 Intel Requests

**POST /challenges/{id}/intel-requests** (Participant)

Request:

```json
{ "hint_id": "uuid" }
```

Response:

```json
{ "hint": "Look at the image metadata.", "penalty_points": 25, "total_penalty": 25 }
```

Rules: penalty recorded by backend and applied to score. Re-requesting the same hint
does not duplicate the penalty by default.

### 6.5 Leaderboard & Announcements

**GET /leaderboard** (Participant)

Response: pagination envelope of LeaderboardRow, ranked by Investigation Score, then
fastest completion, then lowest penalties, then earliest Final Investigation.

**GET /announcements** (Participant)

Response: pagination envelope of published Announcement.

### 6.6 Admin

All admin endpoints require role `admin`.

**POST /admin/challenges** — create. **PATCH /admin/challenges/{id}** — edit.
**PATCH /admin/challenges/{id}/publish** — body `{ "status": "published" | "archived" | "ready_for_review" | "draft" }`.

Admin challenge payload (create/edit) supports: `act_id`, `category_id`,
`difficulty_id`, `title`, `mission_brief`, `story_context`, `objectives`, `points`,
`status`, `flags` (protected, hashed), `hints`, `files`. Real flags are never
returned by any participant-facing endpoint.

**GET /admin/submissions** — submission log rows: `id`, `team_name`, `challenge_title`,
`is_correct`, `submitted_at`.

**GET /admin/audit-logs** — rows: `id`, `actor_account_id`, `action`, `target_type`,
`target_id`, `metadata`, `created_at`.

**PATCH /admin/platform-settings** — body (any subset):

```json
{ "registration_open": true, "competition_status": "upcoming", "leaderboard_visible": false }
```

**PATCH /admin/teams/{id}/approve** / **/reject** — body `{ "reason": "..." }` for
reject. Approval required for teams to access challenges.

## 7. Admin-Only Challenge Fields

`flags`, `hints` content, internal notes, and validator data are admin-only. The
participant Challenge model (§5) is the only challenge shape the frontend/platform
uses.

## 8. Open Items — Do Not Guess

- Final flag list for each challenge.
- Final registration open/close dates and competition timeline.
- Final team-size rule (contract keeps 4–5 for now).
- Whether registration requires organizer approval (approve/reject endpoints are
  included and match CONTEXT.md).
- Whether leaderboard freezes before awarding.
- Whether Final Investigation is auto-validated or manually judged.
- The "time-based scoring" note (decaying points). This contract keeps the documented
  20%-threshold Act progression + Intel penalties model until the lead confirms. If
  confirmed, the SubmissionResult `awarded_points` semantics change.

## 9. Changelog

| Version | Date | Notes |
| --- | --- | --- |
| 1.0.0 | 2026-08-07 | Initial frozen v1 contract |