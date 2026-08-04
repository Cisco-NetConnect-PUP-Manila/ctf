# Packet Capture | Beneath the Network

Packet Capture is a story-driven Capture-the-Flag website for a team-based cyber incident response competition. The current repository contains the public-facing Next.js site plus visual shells for the participant platform and admin panel.

## Developer Handoff

Main project document:
[PACKET CAPTURE CTF WEBSITE - Google Docs](https://docs.google.com/document/d/1IDnVNR2l8t4YCYOqqbSpDNVQ_HLWECdqrtRq04x6BWQ/edit?usp=sharing)

Use the Google Docs handoff as the source of truth for task ownership, feature scope, backend requirements, CTF rules, and volunteer assignments.

## Current Status

- Live front-facing deployment: [https://cnc-pup-ctf.vercel.app/](https://cnc-pup-ctf.vercel.app/)
- Deployment note: the live site is frontend-only and is not yet mobile-friendly.
- Public website: built in Next.js. Mobile/tablet/iPad responsive work is still pending for the deployed frontend-only site.
- Participant platform: `/platform` exists as a frontend shell.
- Admin panel: `/admin` exists as a frontend shell.
- Backend/API: not implemented yet.
- Database: not implemented yet.
- Authentication: not implemented yet.
- Deployment: planned for AWS once the account is ready.

Do not put real flags, final answers, hidden keys, validator logic, or private challenge files in frontend code or the `public/` folder.

## Tech Stack

### Frontend

- Next.js App Router
- React
- TypeScript
- CSS

Current versions are defined in `package.json`.

### Backend

Planned backend stack:

- FastAPI
- Python
- PostgreSQL
- SQLAlchemy 2.x
- Alembic migrations
- Secure HTTP-only session cookies for local auth
- AWS Cognito later for production auth, MFA, password reset, and account verification

### Deployment

Planned AWS deployment stack:

- AWS Amplify Hosting for the frontend
- AWS App Runner for the FastAPI backend
- Amazon RDS PostgreSQL for production data
- Amazon S3 private bucket for protected challenge files
- AWS CloudWatch for logs and monitoring
- GitHub Actions for CI/CD

Local development should continue even without an AWS account. Keep auth, storage, and email logic behind service modules so they can be swapped to AWS services later.

## Local Setup

Install dependencies:

```bash
npm install
```

Run the local development server:

```bash
npm run dev
```

Open:

```txt
http://localhost:3000
```

Build for production:

```bash
npm run build
```

## Available Scripts

```bash
npm run dev
npm run build
npm run start
npm run lint
```

## Main Routes

| Route | Purpose | Status |
|---|---|---|
| `/` | Public CTF website | Built |
| `/platform` | Participant platform | Frontend shell |
| `/admin` | Organizer/admin panel | Frontend shell |

## Project Structure

```txt
app/
  page.tsx              Public website
  platform/page.tsx     Participant platform shell
  admin/page.tsx        Admin panel shell
  data.ts               Shared public content
  globals.css           Global styling and responsive rules
  components/           Shared UI components

public/
  images/               Public images and favicon
  fonts/                Local font assets

docs/
  Developer handoff docs and planning artifacts
```

## CTF Rules To Preserve

- The platform uses four sequential Acts.
- Teams unlock the next Act after earning at least 20 percent of the current Act's total points.
- Score, Act unlocks, hint penalties, solved state, and leaderboard rank must be calculated by the backend.
- Public sample flag format: `PacketCapture{FLAG_NAME}`.
- Final flags are pending organizer confirmation.
- Registration fields for the first version: Group Name, Email, Password.
- One email account should be used per team/group so members can access the same team account.

## Backend Work Still Needed

- Team registration and login
- Protected participant and admin routes
- Challenge CRUD for organizers
- Private challenge file handling
- Flag validation
- Scoring engine
- Act progression logic
- Intel Request/hint penalties
- Leaderboard
- Announcements
- Submission logs
- Audit logs
- Platform settings
- Tests and deployment pipeline

## Contribution Workflow

1. Check the Google Docs handoff and GitHub task assignment before starting.
2. Put your name and GitHub account beside the task you are claiming.
3. Create a feature branch from the agreed base branch.
4. Keep pull requests focused on one task or feature area.
5. Include test/build evidence in the pull request.
6. Never commit real flags, secrets, private challenge files, `.env` files, or generated lock/temp files.

## Notes For Developers

- Keep the current public landing page design unless assigned to change it.
- Use `Act` in new UI text, API fields, database names, and code.
- Do not trust frontend state for scoring, unlocks, roles, or permissions.
- Admin access must be enforced by the backend, not only hidden in the UI.
- Protected challenge files should be served only through authorized backend access or short-lived signed URLs in production.
