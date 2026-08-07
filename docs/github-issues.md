# GitHub Issues: Packet Capture CTF Website

Reference document: https://docs.google.com/document/d/1IDnVNR2l8t4YCYOqqbSpDNVQ_HLWECdqrtRq04x6BWQ/edit?usp=sharing

Current truth: the deployed website is frontend-only. The public site exists, `/platform` and `/admin` are frontend shells, and the backend/database/auth system does not exist yet.

Use these issues for GitHub self-assignment. Each developer should assign themselves on GitHub and comment with their name, GitHub username, planned scope, and expected blockers.

Suggested milestone: `MVP: Registration + CTF Platform Core`

Suggested labels:

- `priority:p0`
- `priority:p1`
- `frontend`
- `backend`
- `database`
- `auth`
- `admin`
- `platform`
- `deployment`
- `testing`
- `security`
- `ready-for-dev`

Priority order for the first sprint:

1. Backend foundation
2. Database foundation
3. Team registration
4. Login/logout/session
5. Frontend registration/login integration
6. Route protection

## Issue 1: Set Up FastAPI Backend Foundation

Labels: `priority:p0`, `backend`, `ready-for-dev`

Blocked by: None

## What to build

Create the initial FastAPI backend service for the CTF platform. It should run locally, expose a health check endpoint, load environment configuration safely, and provide a clear structure for future auth, registration, challenge, scoring, admin, and logging modules.

## Acceptance criteria

- [ ] FastAPI app can run locally with one documented command.
- [ ] Health check endpoint returns a successful response.
- [ ] Environment variables are loaded from a local `.env` file without committing secrets.
- [ ] Backend has a clear folder/module structure for routes, services, schemas, models, and config.
- [ ] CORS is configured for the local Next.js frontend.
- [ ] README or backend setup notes explain how to run the service locally.

## Issue 2: Set Up PostgreSQL Database And Alembic Migrations

Labels: `priority:p0`, `backend`, `database`, `ready-for-dev`

Blocked by: Issue 1

## What to build

Connect the FastAPI backend to PostgreSQL and add SQLAlchemy 2.x plus Alembic migrations. This becomes the foundation for team registration, authentication, challenges, submissions, scoring, and admin logs.

## Acceptance criteria

- [ ] Backend connects to local PostgreSQL through environment variables.
- [ ] SQLAlchemy 2.x is configured.
- [ ] Alembic is configured and can create/apply migrations.
- [ ] Initial migration includes core tables for team accounts, roles, sessions or session tracking, platform settings, and audit timestamps.
- [ ] Database setup instructions are documented.
- [ ] No SQLite-only implementation is used for project-critical work.

## Issue 3: Build Team Registration MVP

Labels: `priority:p0`, `backend`, `auth`, `database`, `ready-for-dev`

Blocked by: Issues 1, 2

## What to build

Create the backend registration flow for teams. First-version registration fields are Group Name, Email, and Password. Registration must create a team/group account that can later log in to the CTF platform.

## Acceptance criteria

- [ ] `POST /auth/register` or agreed equivalent endpoint exists.
- [ ] Registration accepts Group Name, Email, and Password.
- [ ] Backend validates required fields and duplicate emails/group names.
- [ ] Passwords are securely hashed before storage.
- [ ] Registration respects a `registration_open` platform setting.
- [ ] API returns field-level validation errors that the frontend can display.
- [ ] Plaintext passwords are never logged or returned.

## Issue 4: Build Login, Logout, And Current Account Session

Labels: `priority:p0`, `backend`, `auth`, `security`, `ready-for-dev`

Blocked by: Issue 3

## What to build

Allow registered teams/admins to log in, remain authenticated through a secure server-controlled session, fetch current account details, and log out.

## Acceptance criteria

- [ ] Login endpoint validates email and password.
- [ ] Successful login creates a secure HTTP-only session cookie or equivalent server-side session mechanism.
- [ ] Logout endpoint invalidates the session.
- [ ] `GET /auth/me` returns current account identity, team/group name, role, and status.
- [ ] Expired or missing sessions return 401.
- [ ] Frontend-sensitive secrets are not stored in localStorage.
- [ ] Auth behavior is covered by basic backend tests.

## Issue 5: Build Frontend Registration And Login Flow

Labels: `priority:p0`, `frontend`, `auth`, `platform`, `ready-for-dev`

Blocked by: Issue 4

## What to build

Add participant-facing registration and login screens connected to the FastAPI backend. The flow should feel consistent with the Packet Capture visual style and support success, loading, and error states.

## Acceptance criteria

- [ ] User can open a registration page or modal from the frontend.
- [ ] Registration form includes Group Name, Email, and Password.
- [ ] Login form uses Email and Password.
- [ ] Forms call the backend API instead of using mock/static data.
- [ ] Loading, success, duplicate account, invalid credentials, and server error states are displayed clearly.
- [ ] Successful login routes the team to `/platform`.
- [ ] UI remains usable on desktop and mobile-width screens.

## Issue 6: Protect Participant Platform Route

Labels: `priority:p0`, `frontend`, `backend`, `auth`, `platform`, `ready-for-dev`

Blocked by: Issues 4, 5

## What to build

Make `/platform` accessible only to authenticated participant/team accounts. Unauthenticated users should be redirected to login, and expired sessions should be handled cleanly.

## Acceptance criteria

- [ ] `/platform` checks the current session before showing participant content.
- [ ] Unauthenticated users are redirected to login.
- [ ] Expired sessions show a clear state and require login again.
- [ ] Current team/group name appears in the platform shell after login.
- [ ] Logout from the platform clears the session.
- [ ] Backend remains the source of truth for authentication state.

## Issue 7: Add Admin Authentication And Role-Based Access

Labels: `priority:p0`, `backend`, `frontend`, `auth`, `admin`, `security`, `ready-for-dev`

Blocked by: Issue 4

## What to build

Protect `/admin` so only organizer/admin accounts can access it. Admin permissions must be enforced by the backend, not only hidden in the frontend.

## Acceptance criteria

- [ ] Account model supports participant/team and admin roles.
- [ ] Admin-only backend endpoints reject non-admin users.
- [ ] `/admin` checks the current user role before showing admin content.
- [ ] Non-admin users receive a clear forbidden/unauthorized state.
- [ ] Admin creation/seed flow is documented for local development.
- [ ] Role checks are covered by basic tests.

## Issue 8: Create Challenge Data Model And Admin Challenge CRUD

Labels: `priority:p0`, `backend`, `database`, `admin`, `ready-for-dev`

Blocked by: Issues 2, 7

## What to build

Allow admins/challenge makers to create and manage challenges from the backend. This is the foundation for showing real challenge data on the participant platform.

## Acceptance criteria

- [ ] Challenge model supports Act, category, difficulty, title, mission brief, story context, objectives, points, visibility state, and publish/archive status.
- [ ] Admin can create, read, update, publish, archive, and delete or disable challenges.
- [ ] Challenge validators/flag hashes are stored securely and never returned to participants.
- [ ] Admin endpoints require admin role.
- [ ] Basic validation prevents invalid points, missing Act, or missing title.
- [ ] Challenge CRUD has basic backend tests.

## Issue 9: Add Protected Challenge File Storage Flow

Labels: `priority:p1`, `backend`, `admin`, `security`, `ready-for-dev`

Blocked by: Issue 8

## What to build

Support protected challenge attachments without placing private files in the frontend `public/` folder. Local development may use a private backend-controlled folder; production should be ready for S3 private buckets or signed URLs later.

## Acceptance criteria

- [ ] Admins can attach files to challenges.
- [ ] Files are not stored in frontend `public/`.
- [ ] Participants can access only files for challenges they are allowed to view.
- [ ] Backend checks authentication and Act/challenge access before file download.
- [ ] File metadata is stored in the database.
- [ ] AWS S3 migration path is documented.

## Issue 10: Build Participant Challenge List From Backend

Labels: `priority:p0`, `frontend`, `backend`, `platform`, `ready-for-dev`

Blocked by: Issue 8

## What to build

Replace mock/static participant challenge content with real published challenge data from the backend. Teams should only see challenges they are allowed to access.

## Acceptance criteria

- [ ] `/platform` fetches challenge data from the backend.
- [ ] Challenges are grouped by Act.
- [ ] Published and accessible challenges are visible to participants.
- [ ] Locked Acts/challenges show a locked state instead of disappearing completely.
- [ ] Challenge cards show title, Act, category, difficulty, points, status, and mission brief.
- [ ] Frontend handles loading, empty, and error states.

## Issue 11: Implement Flag Submission And Solve Tracking

Labels: `priority:p0`, `backend`, `database`, `platform`, `security`, `ready-for-dev`

Blocked by: Issue 10

## What to build

Allow authenticated teams to submit flags for accessible challenges. The backend validates flags, records attempts, records solves, and prevents duplicate score awards.

## Acceptance criteria

- [ ] Flag submission endpoint exists for a challenge.
- [ ] Backend validates that the team can access the challenge.
- [ ] Correct submissions create a solve record.
- [ ] Incorrect submissions create a submission attempt record but award no points.
- [ ] Duplicate correct submissions do not award points twice.
- [ ] API never returns real flags or validator logic.
- [ ] Submission flow has basic backend tests.

## Issue 12: Implement Scoring And 20 Percent Act Progression

Labels: `priority:p0`, `backend`, `database`, `platform`, `ready-for-dev`

Blocked by: Issue 11

## What to build

Calculate Investigation Score and Act unlocks on the backend. A team unlocks the next Act after earning at least 20 percent of the current Act's total points.

## Acceptance criteria

- [ ] Backend calculates team Investigation Score from solves and penalties.
- [ ] Backend calculates current Act access.
- [ ] Next Act unlocks when the team reaches at least 20 percent of the current Act's total points.
- [ ] Previously unlocked Acts remain accessible unless an admin/platform setting says otherwise.
- [ ] Frontend displays score, current Act, and unlock progress from backend data.
- [ ] Scoring and progression logic have automated tests.

## Issue 13: Implement Intel Request / Hint Penalty System

Labels: `priority:p1`, `backend`, `database`, `platform`, `ready-for-dev`

Blocked by: Issues 10, 12

## What to build

Allow selected challenges to provide Intel Requests/hints with point penalties. Hint usage and penalties must be tracked by the backend.

## Acceptance criteria

- [ ] Admin can configure hint text and penalty value per challenge.
- [ ] Participant can request available Intel for an accessible challenge.
- [ ] Backend records each Intel Request.
- [ ] Backend applies the configured penalty to score calculation.
- [ ] Frontend shows used hints and penalty impact.
- [ ] Re-requesting the same hint does not duplicate the penalty unless organizers explicitly configure otherwise.

## Issue 14: Implement Leaderboard MVP

Labels: `priority:p1`, `backend`, `frontend`, `platform`, `ready-for-dev`

Blocked by: Issue 12

## What to build

Show a backend-calculated leaderboard using Investigation Score as the primary ranking factor. Include tie-breaker-ready fields without exposing private data.

## Acceptance criteria

- [ ] Leaderboard endpoint returns ranked teams.
- [ ] Ranking uses total Investigation Score first.
- [ ] Returned data includes team/group name, score, solved count, current Act, and timing/penalty fields when available.
- [ ] `/platform` displays live leaderboard data from the backend.
- [ ] Frontend handles loading, empty, and error states.
- [ ] Leaderboard does not expose emails, passwords, private notes, flags, or admin-only data.

## Issue 15: Build Announcements System MVP

Labels: `priority:p1`, `backend`, `frontend`, `admin`, `platform`, `ready-for-dev`

Blocked by: Issues 7, 10

## What to build

Allow admins to publish announcements and participants to view them in the platform.

## Acceptance criteria

- [ ] Admin can create, edit, publish, and archive announcements.
- [ ] Participant platform displays published announcements.
- [ ] Announcements support title, body, status, author/admin, and timestamps.
- [ ] Archived/unpublished announcements are hidden from participants.
- [ ] Admin endpoints require admin role.

## Issue 16: Implement Admin Submission Logs And Audit Logs

Labels: `priority:p1`, `backend`, `database`, `admin`, `security`, `ready-for-dev`

Blocked by: Issues 11, 13

## What to build

Give organizers visibility into important platform activity such as logins, registrations, flag submissions, correct/incorrect attempts, Intel usage, score changes, unlock events, and admin actions.

## Acceptance criteria

- [ ] Backend records important auth, submission, scoring, unlock, and admin events.
- [ ] Admin can view submission logs.
- [ ] Admin can view audit logs.
- [ ] Logs include actor, action, timestamp, target, and relevant metadata.
- [ ] Logs do not expose plaintext passwords or real flags.
- [ ] Admin log endpoints require admin role.

## Issue 17: Make The Deployed Frontend Mobile, Tablet, And iPad Friendly

Labels: `priority:p0`, `frontend`, `testing`, `ready-for-dev`

Blocked by: None

## What to build

Make the live front-facing frontend-only website usable across mobile, tablet, and iPad dimensions while preserving the Packet Capture CRT/terminal visual direction.

## Acceptance criteria

- [ ] Public homepage sections fit on common mobile widths without horizontal overflow.
- [ ] `/platform` shell remains usable on mobile/tablet widths even while backend is pending.
- [ ] `/admin` shell remains readable on tablet/iPad widths.
- [ ] Navigation and taskbar do not overlap important content.
- [ ] Text does not overflow buttons, cards, sections, or tables.
- [ ] Verified with desktop, tablet/iPad, and mobile viewport checks.
- [ ] The deployed link reflects the responsive fixes after merge/deploy.

## Issue 18: Prepare API Contract Before Full Frontend Integration

Labels: `priority:p0`, `backend`, `frontend`, `platform`, `admin`, `ready-for-dev`

Blocked by: Issues 1, 2

## What to build

Freeze a first-version API contract so frontend and backend developers can work without guessing endpoint names, payload shapes, roles, and expected errors.

## Acceptance criteria

- [ ] API endpoint map is documented for auth, challenges, submissions, leaderboard, announcements, and admin actions.
- [ ] Request/response examples are included for registration, login, current account, challenge list, and flag submission.
- [ ] Error format is consistent and documented.
- [ ] Role/access expectations are listed per endpoint.
- [ ] Frontend developers can build against the contract without reading backend internals.

## Issue 19: Add MVP Testing And QA Checklist

Labels: `priority:p1`, `testing`, `backend`, `frontend`, `ready-for-dev`

Blocked by: Issues 3, 4, 5, 10, 11, 12

## What to build

Create the basic test and QA coverage needed before the MVP is considered ready for demo.

## Acceptance criteria

- [ ] Backend tests cover registration, login, auth role checks, challenge access, flag submission, scoring, and Act unlocks.
- [ ] Frontend QA checklist covers registration, login, route protection, challenge list, submission feedback, leaderboard, and responsive behavior.
- [ ] Pull request template or contributor notes require test/build evidence.
- [ ] MVP can be verified locally by a developer following documented steps.

## Issue 20: Prepare Cloud-Ready Deployment Plan And Environment Setup

Labels: `priority:p1`, `deployment`, `backend`, `frontend`, `database`, `security`, `ready-for-dev`

Blocked by: Issues 1, 2, 4

## What to build

Prepare the project for deployment once the final cloud provider is selected. Local development should remain usable before the cloud account/provider is ready.

## Acceptance criteria

- [ ] Required environment variables are documented for frontend and backend.
- [ ] Local, staging, and production environment expectations are documented.
- [ ] Provider-neutral targets are listed: frontend hosting, containerized FastAPI backend hosting, managed PostgreSQL, private object storage, monitoring/logging, and GitHub Actions.
- [ ] Backend storage/auth modules are structured so AWS, Azure, GCP, Oracle, or another provider can be added later.
- [ ] Deployment checklist includes build, migration, secret, rollback, and monitoring steps.

## Issue 21: Add Platform Settings For Competition Control

Labels: `priority:p1`, `backend`, `admin`, `database`, `ready-for-dev`

Blocked by: Issues 2, 7

## What to build

Create backend-managed platform settings so organizers can control registration state, competition state, leaderboard visibility, and rule toggles without code edits.

## Acceptance criteria

- [ ] Database stores platform settings such as `registration_open`, competition status, and leaderboard visibility.
- [ ] Admin can view and update platform settings.
- [ ] Registration flow reads `registration_open` from backend settings.
- [ ] Participant platform respects relevant competition state settings.
- [ ] Settings updates are audit logged.

## Issue 22: Final Investigation Access And Evidence Tracking

Labels: `priority:p1`, `backend`, `frontend`, `platform`, `database`, `ready-for-dev`

Blocked by: Issues 11, 12

## What to build

Track recovered story fragments, keys, files, and evidence across Acts so qualified teams can access the Final Investigation when organizers enable it.

## Acceptance criteria

- [ ] Backend can record evidence/story fragments unlocked by solved challenges.
- [ ] Participant platform shows recovered evidence in an investigation board.
- [ ] Final Investigation remains locked until qualification rules are met.
- [ ] Final Investigation access is controlled by backend logic.
- [ ] No hidden final answers or private keys are exposed in frontend code.

## Accuracy Notes

These issues are aligned to the current repository and the latest developer guide. They are safe as the GitHub issue baseline for the dev team.

Still pending from organizers and should not be guessed:

- Final flag list
- Final challenge files
- Final registration open/close dates
- Final team size rules
- Final contact channel
- Final production cloud provider/account details
- Any custom scoring exceptions beyond the documented 20 percent Act progression and Intel penalties
