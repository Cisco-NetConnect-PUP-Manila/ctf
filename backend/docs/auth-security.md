# Authentication hardening

All accounts continue to sign in at `/login`. Organizer accounts additionally require
a six-digit authenticator code. Participants do not need an authenticator.

## Operator setup

1. Rebuild the backend and apply migrations (the Docker startup script does this).
2. Set a dedicated `MFA_ENCRYPTION_KEY` in the deployment secret manager. Generate it
   with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
   Keep it stable and backed up; changing it without re-enrollment locks out organizers.
3. Enroll each organizer from a trusted operator terminal:
   `docker compose exec -it backend python -m app.scripts.configure_admin_mfa --email admin@example.com`.
   Add the displayed private key/URI to the organizer's authenticator app and enter its code.
   Never paste that secret into Git, chat, screenshots, or public logs. Enrollment revokes
   previous sessions. Wait for the next code before logging in.
4. Lost-device recovery uses that same operator-only command. It requires explicit
   replacement confirmation. There is deliberately no password-only or email bypass.

`ADMIN_MFA_REQUIRED` defaults to true. Production refuses to start if it is false or the
encryption key is missing/invalid. Local mode alone supports a development-only derived
encryption key; do not move locally encrypted enrollment secrets into production.
Production also rejects `DEV_ADMIN_*` variables and the shipped bootstrap password.
At startup it also rejects active database admin accounts still using the shipped password.
Remove the Docker development credential variables when using a production manifest.

## Login limits and audit

Five failed password/code attempts against an account start an escalating cooldown
(30 seconds up to 15 minutes). Attempts during cooldown do not extend it. A successful
login resets the account failure budget. Unknown emails receive the same password-work
and throttling treatment. All requests consume an IP budget (`LOGIN_IP_LIMIT`, default
300 per 15 minutes), with a five-minute cooldown on exhaustion. Buckets and advisory
locks live in PostgreSQL, so replicas share limits. This is not a substitute for edge
rate limits, DDoS protection, or monitoring.

Forwarded IPs are ignored by default. Configure `TRUSTED_PROXY_CIDRS` only for immediate
proxies you control that append/overwrite forwarding headers; block direct backend access.
An unconfigured proxy groups users into one IP budget, so tune for shared campus networks.

Failed logins and MFA attempts are audited without passwords/codes. The first password
lockout in a window triggers a best-effort organizer email. Delivery requires a configured
email provider; `none` sends nothing. Review audit logs and provider delivery failures.

## CSRF and sessions

Browser mutations require an exact configured `Origin` and `X-CSRF-Protection: 1`.
The common frontend API client sends the header, and the Next proxy preserves it.
Cookie-authenticated scripts must also send both headers. Public cookie-free CLI login
requests remain supported. CORS, secure HttpOnly SameSite cookies, server role checks,
and MFA-verified admin sessions remain independent defenses. Old password-only admin
sessions are rejected after rollout. Changing an admin password or enrollment revokes
existing sessions; restarting with unchanged local bootstrap credentials does not.

## Verification

Run the PostgreSQL-backed backend pytest suite, frontend lint, and production build.
Manually test authenticator enrollment, missing/invalid/reused/new codes, cooldown,
participant rejection/disable states, and keyboard-only organizer confirmations.
Deployment requires HTTPS, the exact frontend origin, production secrets, and real email
configuration before these controls can be considered operational.
