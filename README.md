# Packet Capture | Beneath the Network

Packet Capture is a story-driven Capture-the-Flag website for a team-based cyber incident response competition. The current repository contains the public-facing Next.js site plus visual shells for the participant platform and admin panel.

## Developer Guide

Main project document:
[PACKET CAPTURE CTF WEBSITE - Google Docs](https://docs.google.com/document/d/1IDnVNR2l8t4YCYOqqbSpDNVQ_HLWECdqrtRq04x6BWQ/edit?usp=sharing)

Use the Google Docs developer guide as the source of truth for task ownership, feature scope, backend requirements, CTF rules, and volunteer assignments.

## Current Status

- Live frontend domain: [https://packetcapture.xyz/](https://packetcapture.xyz/)
- Public website: Next.js App Router frontend.
- Registration: participant registration flow posts to the FastAPI backend and creates pending teams.
- Authentication: backend-owned login/session handling with secure HTTP-only cookies.
- Participant platform: backend-authorized challenge listing, details, submissions, and private file access.
- Admin panel: organizer login, registration/team review, challenge management, file upload, announcements, and audit logging.
- Backend/API: FastAPI service in `backend/`.
- Database: PostgreSQL managed through SQLAlchemy models and Alembic migrations.
- Challenge files: backend-managed private storage; local Docker uses a volume, production should use private S3.
- Email notifications: provider-neutral transactional email scaffold for registration receipt and approval/status emails.
- Deployment direction: AWS for backend/database/storage, Vercel for frontend, Cloudflare for DNS/security.

Do not put real flags, final answers, hidden keys, validator logic, or private challenge files in frontend code or the `public/` folder.

## Tech Stack

### Frontend

- Next.js App Router
- React
- TypeScript
- CSS

Current versions are defined in `package.json`.

### Backend

Backend stack:

- FastAPI
- Python
- PostgreSQL
- SQLAlchemy 2.x
- Alembic migrations
- Secure HTTP-only session cookies for local auth
- Production auth provider is still TBD; keep auth behind backend modules so Cognito, Azure, GCP, Oracle, or another provider can be integrated later.

### Deployment

Current production direction:

- Frontend: Vercel, already mapped to `https://packetcapture.xyz/`.
- Backend: FastAPI Docker image on AWS, recommended first path is ECR + App Runner.
- API domain: `https://api.packetcapture.xyz`.
- Database: Amazon RDS for PostgreSQL.
- Challenge files: private Amazon S3 bucket with short-lived signed downloads after backend authorization.
- Email: Resend or SendGrid for the initial release; AWS SES can replace it later.
- DNS/security: Cloudflare manages the domain, TLS proxying, and optional Access rules.
- Extended web/lab challenges: Cloudflare Tunnel + Cloudflare Access; raw service ports should not be public.
- Monitoring/logging: AWS CloudWatch for backend logs.
- CI/CD: GitHub Actions can build, test, and push the backend image when AWS access is ready.

See [docs/cloud-deployment-runbook.md](docs/cloud-deployment-runbook.md) for the production environment variables, AWS services, deployment steps, smoke tests, and rollback notes.

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

## Docker Setup

Recommended on Windows: run the helper script. It writes the team-standard local ports to `.env`, starts Docker Compose, and runs backend migrations.

```bash
scripts\docker-dev.cmd
```

Team-standard local URLs:

```txt
Frontend:     http://localhost:3001
Backend docs: http://localhost:8001/docs
PostgreSQL:   localhost:5433
```

Shared local admin login:

```txt
Email:    admin@example.com
Password: AdminPassword123!
```

When `BACKEND_ENV=local`, Docker automatically applies migrations, seeds the Acts and
challenge lookups, and creates or resets this development-only admin before FastAPI
starts. Override `DEV_ADMIN_EMAIL` and `DEV_ADMIN_PASSWORD` in `.env` when needed.
These defaults must never be used in a deployed environment.

Challenge evidence uploads are private backend-managed files. Local Docker stores them
in the `challenge-files` Docker volume at `/app/storage/challenge-files`; production can
replace that with private object storage while keeping the same API contract.

Check the current Docker URLs anytime:

```bash
scripts\docker-status.cmd
```

If a dev already has another project using one of those ports, they can either stop that project or intentionally run:

```bash
scripts\docker-dev.cmd -AutoPorts
```

Manual setup is also available. Copy the example environment file if you want local overrides:

```bash
copy .env.example .env
```

Build and run the frontend, backend, and PostgreSQL:

```bash
docker compose up --build
```

If your machine uses the standalone Compose command, run:

```bash
docker-compose up --build
```

Open the frontend:

```txt
http://localhost:3001
```

Open the backend API docs:

```txt
http://localhost:8001/docs
```

PostgreSQL runs on:

```txt
localhost:5433
```

Default local database values are defined in `.env.example`. The FastAPI backend should use the Docker database host `postgres` when running inside Compose, and `localhost` when running directly on the host machine.

Run backend migrations from `backend/` after the database is available:

```bash
alembic upgrade head
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
  Developer guide and planning artifacts
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

1. Check the Google Docs developer guide and GitHub task assignment before starting.
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
