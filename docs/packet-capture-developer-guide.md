# Packet Capture Developer Guide

Frontend, Backend, Deployment, CTF Guidelines, and Volunteer Ownership

Audience: website lead, 6 volunteer developers, challenge makers, and organizers.

Purpose: this is the main developer guide the dev team should follow. It explains the current project, agreed stack, missing work, rules that must not be guessed, ownership lanes, and the first end-to-end milestone.

Current truth: the repository is still a frontend-only Next.js project. The public site is built. `/platform` and `/admin` are visual shells. The remaining work is backend, database, authentication, challenge management, scoring, admin operations, API integration, security, testing, and deployment.

If this document conflicts with an old note or chat message, stop and ask the website lead. Do not silently choose a different rule or architecture.

## 1. Read This First

- Do not redesign or rebuild the public landing page unless assigned.
- Do not put real flags, final answers, hidden keys, validator logic, or private challenge files in frontend code or `public/`.
- No real flags or final answers should appear in frontend code, public JSON, comments, static files, or shared screenshots.
- Do not calculate score, unlocks, penalties, solved state, or admin permissions in the frontend.
- Do not start extra modules before the first end-to-end milestone works.
- Use **Act** as the implementation term in UI, API, database names, and code. If organizer notes say "Level", treat it as the equivalent Act/challenge set unless the lead says otherwise.
- Every pull request must point to an assigned task and include test evidence.
- Anything marked Pending Organizer Decision must not be guessed.

## 2. Current Project State

- Framework: Next.js App Router.
- Frontend language: TypeScript.
- Current versions: Next.js 16.2.10, React 19.0.0, TypeScript 5.7.3.
- Public site route: `/`.
- Participant platform shell: `/platform`.
- Admin panel shell: `/admin`.
- Shared public content source: `app/data.ts`.
- Main styling: `app/globals.css`.
- Public assets: `public/fonts` and `public/images`.
- Current implementation: static/frontend-only.
- Already done: favicon, browser tab title, and responsive support for mobile, tablet, and iPad.

The public website currently includes:

- Hero / event intro
- About
- Competition overview
- Four Acts
- Rules
- Scoring / flag format
- FAQ
- Timeline
- Sponsors and partners
- Footer

The current project does not yet have:

- FastAPI backend
- PostgreSQL database
- Authentication and registration
- Protected participant platform
- Protected admin panel
- Challenge CRUD
- Private file storage
- Flag validation
- Scoring and Act progression
- Live leaderboard
- Submission logs
- Audit logs
- Production deployment pipeline

## 3. Scope And Non-Negotiables

Included in the first working release:

- Team registration and login.
- Protected participant and admin routes.
- Admin challenge creation, editing, publishing, archiving, files, hints, and flag validator setup.
- Participant challenge loading and flag submission.
- Backend-controlled scoring, hint penalties, Act progression, and leaderboard.
- Announcements, submission logs, and audit logs.
- Local development setup, staging deployment, production deployment, monitoring, backups, and rollback.

Not included unless assigned separately:

- A new public website design.
- Individual login accounts for every member. First version uses one team account.
- Real-time WebSockets. Polling is enough for the first version.
- Public access to protected challenge files.
- Arbitrary code validators entered by admins.
- Features not listed in this developer guide.

## 4. Agreed Tech Stack

| Layer | Chosen Stack | Notes |
|---|---|---|
| Frontend | Next.js App Router, React, TypeScript, CSS | Keep the current frontend. It calls the backend API and never stores secrets. |
| Backend | FastAPI with Python | One API service for auth, registration, challenges, submissions, scoring, leaderboard, admin actions, and logs. |
| Database | PostgreSQL | Use the same database engine for all developers. SQLite is only for disposable experiments. |
| ORM and migrations | SQLAlchemy 2.x and Alembic | Do not mix SQLAlchemy and SQLModel. Dev 2 owns migration coordination. |
| Local authentication | Email/password with secure server-side session cookies | Hash passwords. Do not store authentication tokens in localStorage. |
| Production authentication | Provider TBD | Keep auth behind backend modules so Cognito, Azure, GCP, Oracle, or another provider can be integrated later. |
| Development file storage | Private backend-controlled local folder | Never place protected challenge files in frontend/public. |
| Production file storage | Private object storage, provider TBD | Downloads must be authorized or use short-lived signed URLs. |
| Frontend deployment | Provider TBD | Use the selected host when the deployment provider is final. |
| Backend deployment | Containerized FastAPI service, provider TBD | Run the API as a container. |
| Production database | Managed PostgreSQL, provider TBD | Store team, challenge, submission, score, and audit data. |
| Monitoring | Provider TBD | Collect API errors, backend logs, auth events, and deployment issues. |
| CI/CD | GitHub Actions | Run build, lint, backend tests, and deployment checks. |

Cloud note: build locally first because the final cloud provider is not confirmed. Keep authentication, storage, and email behind service modules so they can be replaced later without rewriting challenge and scoring logic.

## 5. CTF Rules And Business Logic

### Terminology

- Use Act everywhere in new UI text, API fields, database names, and code.
- Use `current_act`, `act_id`, and `act_unlocks`. Do not create `current_level` or `level_unlocks` in new code.
- Investigation Score means the team score shown on the platform and leaderboard.
- Intel Request means a hint request that may deduct points.

### Level / Act Progression

- A player/team may unlock the next Act when they earn at least 20 percent of the total points of the current challenge set.
- Once the minimum required points are reached, the next Act becomes available.
- Unlocking must be calculated by the backend.
- Previously unlocked Acts should remain accessible unless organizers explicitly lock them.

### Flags

- Public sample format: `PacketCapture{FLAG_NAME}`.
- Pending: final flag list for each challenge is not yet available.
- A real flag or validator must never be returned by the API.
- Backend should store protected validators or hashes, not frontend-visible plaintext answers.
- Normalization rules must be organizer-approved. Do not automatically lowercase, trim internal spaces, or remove characters unless the validator rule says so.

## 6. Roles And Access Control

| Role | Access |
|---|---|
| Public visitor | Public website only. |
| Registered participant/team | Protected `/platform`, visible challenges, submissions, progress, leaderboard, announcements, profile. |
| Team captain | Same as participant for first release unless organizers define captain-only actions. |
| Organizer/admin | Protected `/admin`, challenge management, team management, logs, announcements, settings, controlled overrides. |

Every protected backend endpoint must check role and account status server-side.

## 7. Registration And Authentication Flow

Registration fields:

- Group Name
- Email
- Password

Account setup rule:

- One team/group should use one email account so members can access the same team account.
- The registered email and password are used to log in to the CTF platform.
- Passwords must be hashed. Plaintext passwords must never be logged or stored.

Expected flow:

1. Registration is accepted only while `platform_settings.registration_open` is true.
2. Backend validates fields and returns field-level errors.
3. Login creates a secure HTTP-only session cookie.
4. `GET /auth/me` returns the current account and role.
5. Logout invalidates the session.
6. Expired sessions return 401 and the frontend redirects to login.
7. Password reset uses an organizer reset flow locally, then the selected production auth provider later.

## 8. Participant Platform Requirements

The `/platform` route is currently a frontend shell. It needs:

- Dashboard
- Storyline / Act progression
- Challenges
- Progress
- Investigation Board
- Leaderboard
- Announcements
- Team Profile
- Settings
- Logout

Functional requirements:

- Show current team score and rank.
- Show current Act.
- Show solved and unsolved challenges.
- Lock Acts until the team reaches the 20 percent threshold.
- Submit flags through backend validation.
- Deduct points when Intel Requests are used.
- Save recovered story fragments, keys, files, and evidence.
- Support the Final Investigation only for qualified teams.

## 9. Challenge System Requirements

Challenge data needed:

- Act
- Category
- Difficulty
- Public title
- Public mission brief
- Story context
- Objectives
- Point value
- Protected flag validator/hash
- Attachments
- Hints / Intel Requests
- Hint penalty values
- Unlock requirements
- Visibility state
- Solve state per team

Admin challenge makers must be able to:

- Create, edit, publish, archive, and delete challenges.
- Upload challenge files.
- Configure points, validators, hints, and penalties.
- Control visibility.
- Lock or unlock Acts/challenges when organizers require it.

## 10. Scoring, Progression, And Leaderboard

Submission flow:

1. Authenticate the team and confirm the account is approved and active.
2. Confirm the competition is open for submissions.
3. Load the challenge and verify it is published, visible, unlocked, and accessible.
4. Apply rate limiting before validator work.
5. Create a submission attempt.
6. Validate the flag on the server.
7. If incorrect, update the attempt and return the result.
8. If correct, prevent duplicate awards using a database constraint or transaction lock.
9. Create the solve only if one does not already exist.
10. Update team score, check the 20 percent threshold, create any new `act_unlock`, and commit once.
11. Return awarded points, current score, solved state, newly unlocked Act, and the
    team-specific solve fragment for correct submissions.

Official ranking priority:

1. Highest total Investigation Score.
2. Fastest overall completion time.
3. Lowest accumulated Intel Request penalties.
4. Earliest successful Final Investigation submission, when applicable.

## 11. Admin Panel Requirements

The `/admin` route is currently a frontend shell. It needs:

- Admin dashboard
- Challenge management
- Team management
- Leaderboard management
- Announcement management
- Submission logs
- Platform settings

Admin requirements:

- Create/edit/delete/archive challenges.
- Upload files.
- Configure flags securely.
- Configure Intel Requests and penalties.
- Lock/unlock Acts or challenges.
- View teams.
- Reset team password or trigger reset.
- Reset team progress only if organizers allow it.
- Apply penalties.
- Disqualify teams.
- Publish announcements.
- View submission logs.
- Freeze leaderboard.
- Configure event status and registration state.
- Create an audit log for every important admin action.

## 12. Minimum Database Model

| Table | Purpose |
|---|---|
| `accounts` | Login identity, email, password hash or provider subject later, role, status. |
| `teams` | Group name, account email, score, current Act, registration status. |
| `team_members` | Optional until organizers require member records. |
| `acts` | Act order, name, total points, unlock threshold, visibility. |
| `challenges` | Public metadata, points, difficulty, objectives, visibility, unlock requirements. |
| `challenge_files` | Backend-controlled attachment metadata and storage keys. |
| `flags` | Protected validator/hash, never returned to frontend. |
| `submissions` | Every flag attempt, timestamp, correctness, team, challenge. |
| `solves` | One successful solve per team/challenge. |
| `act_unlocks` | Act progression records per team. |
| `intel_requests` | Hint usage and penalty records. |
| `announcements` | Organizer updates. |
| `audit_logs` | Admin actions, auth-sensitive events, score changes, unlocks. |
| `platform_settings` | Registration state, event state, leaderboard freeze, submission state. |

Database rule: use UTC timestamps in storage. Convert only for display. Add foreign keys, indexes, and unique constraints before the first shared migration is merged.

## 13. API Contract To Freeze Before Frontend Integration

| Area | Minimum Contract |
|---|---|
| Auth user | `id`, `email`, `role`, `team_id`, `registration_status`, `created_at` |
| Team | `id`, `group_name`, `email`, `score`, `current_act`, `status` |
| Challenge | `id`, `act_id`, `title`, `category`, `difficulty`, `points`, `visible`, `locked`, `solved`, `files`, `hints_available` |
| Submission response | `correct`, `awarded_points`, `current_score`, `solved`, `message`, `next_act_unlocked`, `team_fragment` |
| Leaderboard row | `rank`, `team_name`, `score`, `solved_count`, `current_act`, `last_solve_time`, `penalties` |
| Error response | `code`, `message`, optional `field_errors` |

Standard error example:

`{ "code": "CHALLENGE_LOCKED", "message": "This challenge is not available yet." }`

## 14. Initial API Endpoint Map

This is a starting map only. Final request/response fields should be tracked in backend docs or GitHub issues once implementation starts.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Backend health check |
| POST | `/auth/register` | Public | Register a team |
| POST | `/auth/login` | Public | Create session |
| POST | `/auth/logout` | Authenticated | End session |
| GET | `/auth/me` | Authenticated | Return current account |
| GET | `/challenges` | Participant | Return accessible challenges |
| GET | `/challenges/{id}` | Participant | Return challenge details |
| GET | `/challenges/{id}/files` | Participant | Return active files for an unlocked challenge |
| GET | `/challenges/{id}/files/{file_id}/download` | Participant | Download an active challenge file |
| POST | `/challenges/{id}/submissions` | Participant | Submit a flag |
| POST | `/challenges/{id}/intel-requests` | Participant | Request hint / Intel |
| GET | `/leaderboard` | Participant | Return ranked teams |
| GET | `/announcements` | Participant | Return active announcements |
| POST | `/admin/challenges` | Admin | Create challenge |
| PATCH | `/admin/challenges/{id}` | Admin | Edit challenge |
| PATCH | `/admin/challenges/{id}/publish` | Admin | Publish/archive challenge |
| GET | `/admin/challenges/{id}/files` | Admin | List challenge file metadata |
| POST | `/admin/challenges/{id}/files` | Admin | Upload `.raw`, `.pcap`, `.dd`, `.png`, `.txt`, `.pkz`, or `.pka` evidence |
| DELETE | `/admin/challenges/{id}/files/{file_id}` | Admin | Soft-deactivate a challenge file |
| GET | `/admin/submissions` | Admin | View submission logs |
| GET | `/admin/audit-logs` | Admin | View audit logs |
| PATCH | `/admin/platform-settings` | Admin | Update event settings |

## 15. Security And Edge-Case Rules

- Rate-limit login and flag submission.
- Use HTTP-only, Secure, SameSite cookies in staging and production.
- Add CSRF protection for state-changing cookie-authenticated requests.
- Do not log plaintext passwords, session cookies, raw secrets, or full flags.
- Private challenge files require authorization.
- Private challenge files are max 100 MB each and must use backend storage, not frontend `public/`.
- Locked challenges must not reveal file names, counts, sizes, or download links.
- Challenge URLs may be shared, but every challenge read, file download, and flag
  submission must be authorized by the backend for the logged-in team.
- Correct submissions return a team-specific solve fragment. A fragment from Team A
  must not be accepted as proof for Team B.
- Duplicate correct submission awards zero additional points.
- Locked challenge submission returns `CHALLENGE_LOCKED`.
- Already solved challenge returns `ALREADY_SOLVED`.
- Concurrent correct submissions must still award points once.
- Database write failure during scoring must not create partial score state.

## 16. Six-Developer Recommended Ownership

| Dev Lane | Primary Owner | Scope | First Deliverable |
|---|---|---|---|
| Dev 1 |  | FastAPI foundation, auth, registration, role middleware, API health checks. | Running backend with `/health`, `/auth/me`, registration and login flow. |
| Dev 2 |  | PostgreSQL schema, SQLAlchemy models, Alembic migrations, seed data, repository layer. | Shared schema and seed script for accounts, teams, acts, sample challenges. |
| Dev 3 |  | Admin challenge management backend. | Admin can create/edit/publish a challenge and configure points, hints, files, validator. |
| Dev 4 |  | Participant platform frontend and API integration. | Participant dashboard and challenge list using backend data. |
| Dev 5 |  | Scoring, submissions, Act unlocks, leaderboard, audit logs. | Correct flag creates one solve, updates score, unlocks at 20 percent, updates leaderboard. |
| Dev 6 |  | Admin frontend, QA, release polish, docs/checklists. | Admin UI can manage challenge records and see logs; final QA checklist. |

Live task claiming, status, blockers, and GitHub accounts should be tracked in GitHub Issues or GitHub Projects, not duplicated in this developer guide.

## 17. First End-To-End Milestone

Build this before expanding modules:

1. Backend runs locally with FastAPI and PostgreSQL.
2. A team can register using Group Name, Email, and Password.
3. An approved team can log in and open `/platform`.
4. An admin can log in and create one sample challenge.
5. The admin can publish the challenge.
6. The participant can see the challenge if it is visible and unlocked.
7. The participant can submit an incorrect flag and see a clear response.
8. The participant can submit the correct flag.
9. Backend creates one solve and awards points once.
10. When the team reaches the 20 percent threshold, the next Act unlocks.
11. Leaderboard updates using backend-calculated score.
12. Submission and audit logs show the full flow.
13. Tests cover correct, incorrect, duplicate, locked, and concurrent submission paths.

## 18. Git, Setup, Testing, And Deployment

Pull request rules:

- One PR should focus on one assigned task or tightly related group of tasks.
- PR title should mention the task/workstream.
- PR description must include what changed, how it was tested, and screenshots for UI work.
- Do not merge backend schema changes without migration review.
- Do not merge scoring/auth/admin permission changes without reviewer approval.

Local setup requirements:

- Frontend `.env.example`.
- Backend `.env.example`.
- Database migration command.
- Seed command.
- README setup steps.

Testing requirements:

- Backend tests with Pytest.
- Scoring and unlock unit tests.
- Submission integration tests.
- Auth and role access tests.
- Admin action tests.
- Playwright E2E tests for participant and admin flows when the API is ready.
- Frontend build check with `npm.cmd run build`.

Deployment requirements:

- Staging before production.
- GitHub Actions pipeline.
- Database backup and restore test.
- Smoke test after deployment: public site, login, platform, admin, sample challenge, submission, leaderboard.
- Rollback plan for frontend, backend, and database migrations.

## 19. Event Configuration And Pending Decisions

Do not invent these:

- Exact registration open date.
- Exact registration close date.
- Competition start date.
- Final submission deadline.
- Awarding/closing date.
- Official contact channel.
- Team size requirements.
- Registration URL or form.
- Sponsor and partner names/logos.
- Final platform URL.
- Whether registration requires organizer approval.
- Whether leaderboard freezes before awarding.
- Whether Final Investigation is auto-validated or manually judged.

## 20. Current Frontend Files To Know

| File | Purpose |
|---|---|
| `app/page.tsx` | Public Packet Capture website. |
| `app/platform/page.tsx` | Participant platform shell waiting for backend data. |
| `app/admin/page.tsx` | Admin shell waiting for auth and admin APIs. |
| `app/data.ts` | Central public content and module definitions. |
| `app/globals.css` | Theme, CRT styling, responsive rules, layout system. |
| `app/components/Nav.tsx` | Route-aware top navigation. |
| `app/components/Taskbar.tsx` | Bottom taskbar/start menu and timezone display. |
| `app/components/FaqAccordion.tsx` | FAQ behavior. |
| `app/components/TimelineWave.tsx` | Timeline visualization with mobile fallback. |

## 21. Definition Of Done

Feature done:

- API endpoint is implemented and documented.
- Frontend handles loading, empty, success, error, locked, and unauthorized states.
- Role and permission checks happen on the backend.
- Tests cover risky logic, especially scoring and unlocks.
- No secrets or private challenge material are exposed.
- Feature works on desktop, mobile, tablet, and iPad dimensions.

Launch ready:

- Official dates, contact channel, and registration rules are confirmed.
- Production environment variables are configured.
- Database backup and restore procedure is tested.
- Frontend build passes.
- Backend test suite passes.
- Admin and participant flows pass end-to-end QA.
- Rate limiting is enabled.
- Admin audit logs are enabled.
- Production deployment is verified.

## 22. Team Lead Checklist

- [ ] Every task has an owner and GitHub account.
- [ ] API contracts are agreed before frontend/backend work diverges.
- [ ] Challenge makers know not to put real flags in frontend/public files.
- [ ] Each PR states which workstream/task it closes.
- [ ] Scoring and unlock changes are reviewed carefully.
- [ ] Admin endpoints are checked for server-side role protection.
- [ ] Build/test checks pass before merge.
- [ ] Organizer-dependent pending decisions are tracked separately.
- [ ] First end-to-end milestone works before extra polish.
