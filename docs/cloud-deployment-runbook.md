# Packet Capture Cloud Deployment Runbook

This runbook covers the production direction for the full Packet Capture platform, not only the registration release.

## Target Architecture

- Public frontend: Next.js on Vercel at `https://packetcapture.xyz`.
- Backend API: FastAPI container on AWS, exposed as `https://api.packetcapture.xyz`.
- Database: Amazon RDS for PostgreSQL in private networking.
- Challenge files: private Amazon S3 bucket, downloaded through backend authorization and short-lived signed URLs.
- Transactional email: Resend or SendGrid first; AWS SES is a later option if the society wants email fully inside AWS.
- DNS/security: Cloudflare manages `packetcapture.xyz`, `api.packetcapture.xyz`, TLS proxying, and optional Access rules.
- Extended web/lab challenges: Cloudflare Tunnel + Cloudflare Access, with raw lab ports kept off the public internet.

## Recommended AWS Services

Use these for the first production release:

- Amazon ECR: stores the FastAPI Docker image.
- AWS App Runner: runs the FastAPI backend from the ECR image with HTTPS health checks and simple autoscaling.
- Amazon RDS for PostgreSQL: managed production PostgreSQL with backups.
- Amazon S3: private challenge file storage.
- AWS Secrets Manager or SSM Parameter Store: stores database URL, flag pepper, team fragment pepper, email keys, and admin bootstrap credentials.
- Amazon CloudWatch Logs: backend logs and deployment troubleshooting.
- IAM: least-privilege roles for App Runner access to S3 and secrets.

This is the lowest-ops AWS path that still keeps the important production boundaries: managed database, private files, deployable container, and centralized secrets.

## Required Team Inputs

Ask the infrastructure owners only for items we cannot complete from the repo:

- AWS account access or an owner who can create App Runner, ECR, RDS, S3, IAM, and Secrets Manager resources.
- Cloudflare DNS access or a coordinator who can point `api.packetcapture.xyz` to the backend target.
- Official sender identity, for example `Packet Capture <noreply@packetcapture.xyz>`.
- Transactional email provider decision: Resend, SendGrid, or AWS SES.
- Production admin email to bootstrap the first organizer account.

## Production Environment Variables

Backend required:

```txt
BACKEND_ENV=production
DATABASE_URL=postgresql+psycopg://<user>:<password>@<rds-host>:5432/<database>
FRONTEND_ORIGIN=https://packetcapture.xyz
SESSION_COOKIE_NAME=packet_capture_session
SESSION_COOKIE_SECURE=true
SESSION_EXPIRE_HOURS=12
REGISTRATION_OPEN_BY_DEFAULT=false
FLAG_HASH_SECRET=<unique random secret>
TEAM_FRAGMENT_SECRET=<unique random secret>
CHALLENGE_FILE_STORAGE_PROVIDER=s3
CHALLENGE_FILE_S3_BUCKET=<private-s3-bucket>
CHALLENGE_FILE_S3_PREFIX=challenge-files
CHALLENGE_FILE_S3_PRESIGN_SECONDS=300
EMAIL_PROVIDER=resend
EMAIL_FROM=Packet Capture <noreply@packetcapture.xyz>
RESEND_API_KEY=<provider key>
```

Use `EMAIL_PROVIDER=sendgrid` and `SENDGRID_API_KEY` instead if SendGrid is selected.

Optional bootstrap for first deployment:

```txt
BOOTSTRAP_ADMIN_EMAIL=<organizer email>
BOOTSTRAP_ADMIN_PASSWORD=<temporary strong password>
REQUIRE_TEAM_APPROVAL_ON_START=true
```

Remove or rotate `BOOTSTRAP_ADMIN_PASSWORD` after the first admin login is confirmed.

## Deployment Steps

1. Create the RDS PostgreSQL database and keep it private.
2. Create the private S3 bucket for challenge files.
3. Create an IAM role for the backend with only the needed S3 bucket permissions.
4. Build and push the backend Docker image to ECR.
5. Deploy the image to App Runner.
6. Set backend secrets and environment variables.
7. Confirm `/health` and `/health/db` return success.
8. Add or update Cloudflare DNS for `api.packetcapture.xyz`.
9. Set Vercel frontend variables to use `https://api.packetcapture.xyz`.
10. Register a test team, approve it as admin, upload a small challenge file, and verify participant download.

## Cloudflare Setup

- `packetcapture.xyz` stays public for the frontend.
- `api.packetcapture.xyz` points to the AWS backend target.
- Admin and participant authentication stays enforced by FastAPI.
- Optional Cloudflare Access can be added in front of admin routes or staging deployments.
- Extended challenge lab services should use Cloudflare Tunnel + Access, not public raw ports.

## Smoke Test Checklist

- `GET https://api.packetcapture.xyz/health` returns `200`.
- `GET https://api.packetcapture.xyz/health/db` returns `200`.
- Registration creates a pending team.
- Registration receipt email sends.
- Admin login works.
- Admin approval sends a status email.
- Pending teams cannot access the participant platform.
- Approved teams can access published/unlocked challenges.
- Locked Acts stay hidden or blocked.
- Challenge file upload writes to S3.
- Participant download redirects to a short-lived signed S3 URL only after authorization.
- Raw challenge service ports are not reachable from the public internet.

## Rollback

- Keep the previous backend image tag in ECR.
- If deployment fails, redeploy the last known-good App Runner image.
- Do not roll back database migrations unless a migration-specific rollback has been tested.
- If email delivery fails, set `EMAIL_PROVIDER=none` temporarily; registration and approval should continue because email sends are best-effort.
