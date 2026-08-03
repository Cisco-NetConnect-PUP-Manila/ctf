# Packet Capture Developer Handoff

This project is currently a frontend-only Next.js app for **Packet Capture: Beneath the Network**. The public content is aligned with the provided CTF Guidelines and Storyline documentation, but the competition platform and admin panel are still shells. This guide explains what exists, what is missing, and what the next developers should build.

## Current State

- Framework: Next.js App Router
- Main public site route: `/`
- Competition platform shell: `/platform`
- Admin panel shell: `/admin`
- Shared public content source: `app/data.ts`
- Main styles and font rules: `app/globals.css`
- Public assets: `public/fonts`, `public/images`
- Current implementation type: static frontend, no API, no database, no authentication

The site currently includes public sections for:

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

The public content intentionally avoids exposing private flags, final answers, and hidden storyline solutions.

## Important Content Rules

Do not expose any real flag values or final investigation answers in frontend code, public JSON, static files, comments, or generated HTML.

Publicly safe format:

```txt
PacketCapture{FLAG_NAME}
```

Keep secret material only in backend-controlled storage or organizer-only files outside the public frontend bundle.

## Main Missing Work

### 1. Backend/API

The app needs a real backend for all competition behavior.

Required API areas:

- Authentication
- Registration
- Team management
- Challenge loading
- Flag submission
- Score calculation
- Act unlock logic
- Intel Request/hint penalties
- Leaderboard
- Announcements
- Admin operations
- Submission and audit logs
- Platform settings

Suggested starting point:

- Keep public website static where possible.
- Add backend routes or a separate API service.
- Use server-side validation for flags and scoring.
- Never trust frontend state for score, unlocks, rank, penalties, or solved status.

### 2. Database

No database exists yet.

Minimum tables/entities needed:

- users
- teams
- team_members
- registrations
- challenges
- challenge_files
- flags
- submissions
- solves
- acts
- act_unlocks
- intel_requests
- story_fragments
- evidence_items
- announcements
- penalties
- leaderboard_snapshots
- audit_logs
- platform_settings

Security note: flags should be hashed or otherwise protected. Do not store plain flags if avoidable.

### 3. Authentication and Access Control

Needed roles:

- public visitor
- registered participant
- team captain
- organizer/admin

Required behavior:

- Login/logout
- Registration approval or confirmation flow
- Protected `/platform`
- Protected `/admin`
- Role-based authorization
- Session expiration
- Password reset or organizer reset flow

Admin access must be checked on the server, not only hidden in the UI.

### 4. Registration System

Current site only says registration is opening soon.

Needed:

- Registration form
- Team name
- Team members
- Institution/organization
- Contact email
- Team size validation based on organizer rules
- Terms/rules agreement
- Confirmation status
- Organizer approval flow if required
- Registration open/closed state

Public content still has TBA values for contact and timeline. Replace those only after the organizers confirm official details.

### 5. Competition Platform

The `/platform` route is only a frontend shell.

Needed participant pages/modules:

- Dashboard
- Storyline
- Challenges
- Progress
- Investigation Board
- Leaderboard
- Announcements
- Team Profile
- Settings
- Logout

Functional requirements:

- Show current team score and rank
- Show current Act
- Show solved and unsolved challenges
- Lock Acts until minimum Investigation Score is reached
- Keep previous unlocked Acts accessible
- Submit flags through backend validation
- Deduct points when Intel Requests are used
- Save recovered story fragments, keys, files, and evidence
- Support Final Investigation only for qualified teams

### 6. Challenge System

Needed challenge data:

- Act
- Category
- Difficulty
- Public title
- Public mission brief
- Story context
- Objectives
- Point value
- Flag hash / validator
- Attachments
- Hints / Intel Requests
- Hint penalty values
- Unlock requirements
- Visibility state
- Solve state per team

Challenge names and public case names can appear on the site, but correct answers, solution fragments, hidden keys, and final phrases must stay private.

### 7. Scoring Engine

The docs define scoring as Investigation Score first, then tie-breakers.

Needed:

- Score awarded per challenge
- No points for incorrect flags
- Hint/Intel penalties
- Optional penalty adjustments by admin
- Ranking by total Investigation Score
- Tie-breakers:
  - fastest overall completion time
  - lowest accumulated Intel Request penalties
  - earliest successful Final Investigation submission, when applicable

All score math must happen on the backend.

### 8. Leaderboard

Current leaderboard content is static/shell only.

Needed:

- Live ranked teams
- Team name
- Investigation Score
- Challenges solved
- Current Act
- Completion time
- Intel penalties
- Final Investigation status when applicable
- Optional freeze mode near awarding

Consider rate-limiting public leaderboard endpoints.

### 9. Admin Panel

The `/admin` route is a visual shell only.

Needed admin modules:

- Admin dashboard
- Challenge management
- Team management
- Leaderboard management
- Announcement management
- Submission logs
- Platform settings

Admin requirements:

- Create/edit/delete challenges
- Upload files
- Configure flags securely
- Configure Intel Requests and penalties
- Lock/unlock Acts or challenges
- View teams
- Reset team password
- Reset team progress
- Apply penalties
- Disqualify teams
- Publish announcements
- View submission logs
- Freeze leaderboard
- Configure event status and registration state

Every admin action should create an audit log.

### 10. File and Attachment Handling

Needed:

- Secure upload storage
- File access control
- Virus/malware scanning if challenge files can be uploaded by organizers
- Download tracking if needed
- Private challenge files gated by team/Act/challenge access

Do not put real challenge attachments directly in `public/` if they should be access-controlled.

### 11. Security Hardening

Needed before launch:

- Server-side authorization checks
- Rate limiting for login and flag submission
- CSRF protection if using cookie sessions
- Input validation
- Output escaping
- Audit logs
- Secure password hashing
- Environment variable management
- No secrets in frontend bundle
- No source maps with sensitive content in production
- Backup and recovery plan

Flag submission should be rate-limited to prevent brute force and automated submission scripts.

### 12. Event Configuration

Still needs organizer-confirmed values:

- Exact registration open date
- Exact registration close date
- Competition start date
- Final submission deadline
- Awarding/closing date
- Official contact channel
- Team size requirements
- Registration URL or form
- Sponsor and partner names/logos
- Final platform URL

These are currently represented as TBA or empty placeholders.

### 13. Testing

Current project only has a build script.

Needed:

- Unit tests for scoring logic
- Unit tests for unlock logic
- Unit tests for flag format validation
- Integration tests for submissions
- Integration tests for Intel Request penalties
- Auth and role access tests
- Admin action tests
- E2E tests for participant flow
- E2E tests for admin flow

Suggested tools:

- Vitest or Jest for unit tests
- Playwright for E2E tests
- API integration tests for backend routes

### 14. Developer Experience

Needed:

- README
- `.env.example`
- setup instructions
- database migration scripts
- seed data for local development
- API contract documentation
- deployment notes
- staging/production environment notes
- lint configuration

Current `package.json` has:

```json
"lint": "next lint"
```

Verify this before relying on it. Newer Next.js versions may require an explicit ESLint setup instead of `next lint`.

## Recommended Build Order

1. Add README and `.env.example`.
2. Choose backend/database stack.
3. Implement auth and role-based access.
4. Build registration and team model.
5. Build challenge schema and admin challenge management.
6. Build flag submission and scoring.
7. Build Act unlock and Intel Request logic.
8. Build participant platform pages using real API data.
9. Build leaderboard.
10. Build announcement system.
11. Build audit logs and admin controls.
12. Add tests and security hardening.
13. Replace TBA event details with official organizer-approved values.
14. Deploy staging, run QA, then deploy production.

## Current Frontend Files To Know

- `app/page.tsx`: public landing/event page
- `app/platform/page.tsx`: participant platform shell
- `app/admin/page.tsx`: admin shell
- `app/data.ts`: centralized public content and module definitions
- `app/components/Nav.tsx`: route-aware navigation
- `app/components/Taskbar.tsx`: bottom navigation/start menu
- `app/components/FaqAccordion.tsx`: one-open-at-a-time FAQ behavior
- `app/components/TimelineWave.tsx`: timeline visualization
- `app/globals.css`: typography, layout, theme, CRT styling

## Launch Readiness Checklist

- [ ] Official dates are confirmed.
- [ ] Official contact channel is confirmed.
- [ ] Registration form is live.
- [ ] Auth is implemented.
- [ ] Participant platform is protected.
- [ ] Admin panel is protected.
- [ ] Challenges are stored outside the public frontend.
- [ ] Real flags are not exposed.
- [ ] Score logic is backend-controlled.
- [ ] Intel penalties are backend-controlled.
- [ ] Leaderboard is live and tested.
- [ ] Submission logs are available to organizers.
- [ ] Rate limiting is enabled.
- [ ] Admin audit logs are enabled.
- [ ] Full participant flow is tested.
- [ ] Full admin flow is tested.
- [ ] Production deployment is verified.

