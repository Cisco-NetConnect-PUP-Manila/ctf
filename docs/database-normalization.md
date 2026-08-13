# Packet Capture Database Normalization

Backend database guide for the Packet Capture CTF platform.

This document defines the normalized data model the backend should follow when building the FastAPI service. It covers the public-facing website needs, participant platform, admin challenge management, registration, scoring, Act progression, challenge files, and auditability.

## 1. Current Project Reality

The current website is a frontend-only Next.js project.

Existing surfaces:

- Public website: `/`
- Participant platform shell: `/platform`
- Admin panel shell: `/admin`

Missing backend features:

- Team registration
- Admin approval
- Login/logout/session
- Challenge management
- Protected challenge files
- Flag validation
- Submissions and solves
- Scoring
- 20 percent Act progression
- Intel Request penalties
- Leaderboard
- Announcements
- Audit logs
- Platform settings

## 2. Design Goals

The database should be:

- Clean: each table represents one concept.
- Secure: secrets, flags, credentials, and protected files are isolated.
- Auditable: important actions can be traced.
- Provider-flexible: storage and deployment should not depend on one cloud provider yet.
- MVP-friendly: registration and login can be built first without blocking future CTF features.
- Backend-owned: scoring, role checks, unlocks, validation, and permissions are never decided by the frontend.

## 3. Normalization Rules

Use a normalized relational model as the source of truth.

- Use PostgreSQL.
- Use IDs and foreign keys for relationships.
- Avoid duplicated text values for controlled fields.
- Use lookup tables for challenge categories and difficulties.
- Store repeated data in child tables, not repeated columns.
- Store source records for scoring instead of only storing total score.
- Store private file metadata in the database, not file bytes.
- Do not store plaintext passwords.
- Do not expose plaintext flags through frontend code, public files, or participant APIs.

## 4. Core Entity Map

```txt
accounts
  |-- participant account -> teams -> team_members
  |-- admin account

acts
  |-- challenges
        |-- challenge_flags
        |-- challenge_files
        |-- hints

teams
  |-- submissions
  |-- solves
  |-- intel_requests
  |-- act_unlocks
  |-- score_adjustments

admins/accounts
  |-- announcements
  |-- platform_settings updates
  |-- audit_logs
```

## 5. Accounts, Teams, And Registration

### accounts

Stores login identity and access role.

```txt
id
email
password_hash
role
status
last_login_at
created_at
updated_at
```

Recommended constraints:

- `email` unique
- `role` allowed values: `participant`, `admin`
- `status` allowed values: `active`, `disabled`
- `password_hash` required

Notes:

- Participant accounts represent teams.
- Admin accounts represent organizers/challenge makers.
- Admin accounts do not need team records.
- Team member emails are not login accounts unless explicitly promoted later.

### teams

Stores participant group profile.

```txt
id
account_id
group_name
leader_member_id
status
approved_by_account_id
approved_at
rejected_by_account_id
rejected_at
rejection_reason
created_at
updated_at
```

Recommended constraints:

- `account_id` unique foreign key to `accounts.id`
- `group_name` unique
- `status` allowed values: `pending`, `approved`, `rejected`, `disabled`
- `approved_by_account_id` references an admin account
- `rejected_by_account_id` references an admin account

Registration rule:

- New teams start as `pending`.
- Only approved teams can access the full participant platform.
- Pending teams may log in only to see an awaiting-approval state.

### team_members

Stores required roster details.

```txt
id
team_id
full_name
email
is_leader
created_at
updated_at
```

Recommended constraints:

- `team_id` foreign key to `teams.id`
- `email` required
- `full_name` required
- each team must have 4 to 5 members
- exactly one member per team has `is_leader = true`
- leader member email must match the participant account email

Implementation note:

- PostgreSQL cannot enforce "minimum 4 members per team" cleanly with a simple column constraint. Enforce the 4 to 5 member rule in the registration backend transaction. A database trigger can be added later if needed.

## 6. Acts And Challenge Metadata

### acts

Stores the competition Acts.

```txt
id
act_number
slug
title
description
unlock_threshold_percent
sort_order
is_active
created_at
updated_at
```

Recommended constraints:

- `slug` unique
- `act_number` unique
- `unlock_threshold_percent` defaults to `20`
- `sort_order` unique

Initial Acts:

- Act I: The Signal
- Act II: The Breach
- Act III: The Echo
- Act IV: Beneath the Network

### challenge_categories

Controlled category lookup.

```txt
id
name
slug
sort_order
is_active
```

Examples:

- OSINT
- Web Penetration Testing
- Digital Forensics
- Networking
- Cisco Packet Tracer

### challenge_difficulties

Controlled difficulty lookup.

```txt
id
name
slug
sort_order
is_active
```

Examples:

- Easy
- Medium
- Hard
- Expert

### challenges

Stores public and admin-managed challenge metadata.

```txt
id
act_id
category_id
difficulty_id
title
slug
mission_brief
story_context
objectives
points
status
created_by_account_id
reviewed_by_account_id
reviewed_at
published_by_account_id
published_at
archived_by_account_id
archived_at
created_at
updated_at
```

Recommended constraints:

- `act_id` foreign key to `acts.id`
- `category_id` foreign key to `challenge_categories.id`
- `difficulty_id` foreign key to `challenge_difficulties.id`
- `slug` unique
- `points` must be greater than or equal to 0
- `status` allowed values: `draft`, `ready_for_review`, `published`, `archived`

Visibility rule:

- Participants only see `published` challenges.
- A published challenge is visible only if the team has access to that challenge's Act.
- Draft, ready-for-review, and archived challenges are admin-only.

## 7. Flags And Validation

### challenge_flags

Stores secret flag validator records.

```txt
id
challenge_id
flag_hash
validator_type
is_active
created_by_account_id
created_at
deactivated_at
```

Recommended constraints:

- `challenge_id` foreign key to `challenges.id`
- `flag_hash` required
- `validator_type` defaults to `exact`
- one challenge can have multiple accepted active validators if organizers need aliases

Security rules:

- Do not store real flags in frontend code.
- Do not store real flags in public JSON.
- Do not return real flags from participant APIs.
- Do not log plaintext submitted flags.
- Hash submitted values and compare with stored validators.

Recommended MVP normalization:

- Trim leading/trailing spaces before validation.
- Do not lowercase.
- Do not remove inner spaces.
- Do not change punctuation.
- Public flag format stays `PacketCapture{FLAG_NAME}`.

## 8. Challenge Files

### challenge_files

Stores private file metadata and a provider-neutral storage reference.

```txt
id
challenge_id
storage_provider
storage_key
original_filename
display_name
extension
content_type
size_bytes
uploaded_by_account_id
is_active
created_at
updated_at
deactivated_at
```

Recommended constraints:

- `challenge_id` foreign key to `challenges.id`
- `storage_provider` starts as `local`; keep the field provider-neutral for future object storage
- `storage_key` required and unique
- `extension` allowed values: `.raw`, `.pcap`, `.dd`, `.png`, `.txt`, `.pkz`, `.pka`
- `size_bytes` must be between 0 and 104857600
- `is_active` controls soft deactivation

Rules:

- Protected challenge files must never be stored in frontend `public/`.
- Store file bytes outside the database; store only metadata and the internal storage key.
- Generate `storage_key` internally. Keep the original filename only as metadata.
- Local development uses backend-controlled private storage.
- Production can later use private cloud object storage through the same backend access checks.
- Participants can download only when logged in, approved, and allowed to access the challenge's Act.
- Locked challenges must not reveal file names, counts, sizes, or download links.
- Admin removal means deactivating the file record, not immediate hard deletion.

## 9. Hints And Intel Requests

### hints

Stores hint content for a challenge.

```txt
id
challenge_id
content
penalty_points
sort_order
is_active
created_at
updated_at
```

Recommended constraints:

- `challenge_id` foreign key to `challenges.id`
- `penalty_points` must be greater than or equal to 0
- `sort_order` controls hint order

### intel_requests

Stores a team's use of a hint/Intel Request.

```txt
id
team_id
challenge_id
hint_id
penalty_points
requested_at
```

Recommended constraints:

- `team_id` foreign key to `teams.id`
- `challenge_id` foreign key to `challenges.id`
- `hint_id` foreign key to `hints.id`
- unique constraint on `team_id`, `hint_id` unless organizers explicitly allow repeat penalties

Rules:

- The backend records Intel usage.
- The backend applies penalties to score calculation.
- Re-requesting the same hint should not duplicate the penalty by default.

## 10. Submissions, Solves, And Scoring

### submissions

Stores every flag attempt.

```txt
id
team_id
challenge_id
submitted_value_hash
submitted_value_preview
is_correct
created_solve_id
submitted_at
ip_address_hash
user_agent_hash
```

Recommended constraints:

- `team_id` foreign key to `teams.id`
- `challenge_id` foreign key to `challenges.id`
- `created_solve_id` nullable foreign key to `solves.id`

Rules:

- Store correct and incorrect attempts.
- Do not store plaintext submitted flags forever.
- Use `submitted_value_hash` for traceability.
- `submitted_value_preview` may be optional and should not reveal full secret values.

### solves

Stores successful challenge completions.

```txt
id
team_id
challenge_id
submission_id
points_awarded
team_fragment_hash
team_fragment_preview
solved_at
```

Recommended constraints:

- `team_id` foreign key to `teams.id`
- `challenge_id` foreign key to `challenges.id`
- `submission_id` foreign key to `submissions.id`
- unique constraint on `team_id`, `challenge_id`

Rules:

- Solves are the source of truth for completed challenges.
- A team can only solve a challenge once.
- Duplicate correct submissions do not award points again.
- `points_awarded` should snapshot the challenge value at solve time.
- `team_fragment_hash` stores a keyed hash of the team-specific solve fragment.
- `team_fragment_preview` is audit/debug metadata only; the API derives the full
  displayed fragment from `team_id`, `challenge_id`, and `TEAM_FRAGMENT_SECRET`.

### score_adjustments

Stores manual admin score corrections.

```txt
id
team_id
points_delta
reason
created_by_account_id
created_at
```

Recommended constraints:

- `team_id` foreign key to `teams.id`
- `created_by_account_id` references an admin account
- `reason` required

Scoring formula:

```txt
Investigation Score =
  sum(solves.points_awarded)
  - sum(intel_requests.penalty_points)
  + sum(score_adjustments.points_delta)
```

Rules:

- Do not use `teams.total_score` as the source of truth.
- Leaderboard should be computed from source records.
- Optional cached leaderboard snapshots may be added later, but they must not replace source records.

## 11. Act Progression

### act_unlocks

Stores recorded Act access for teams.

```txt
id
team_id
act_id
unlocked_by_account_id
reason
unlocked_at
```

Recommended constraints:

- `team_id` foreign key to `teams.id`
- `act_id` foreign key to `acts.id`
- `unlocked_by_account_id` nullable foreign key to `accounts.id`
- unique constraint on `team_id`, `act_id`
- `reason` allowed values: `initial`, `score_threshold`, `admin_override`

Rules:

- Act I should be unlocked by default for approved teams.
- The backend calculates when the next Act is eligible.
- The next Act unlocks when a team earns at least 20 percent of the current Act's total challenge points.
- Previously unlocked Acts remain accessible unless organizers explicitly disable access.
- Store unlock events for auditability and stability.

## 12. Leaderboard

The leaderboard can be computed from normalized source records.

Recommended returned fields:

```txt
rank
team_id
group_name
investigation_score
solved_count
current_act
intel_penalty_total
last_solve_at
final_investigation_submitted_at
```

Ranking order:

1. Highest Investigation Score
2. Fastest overall completion time
3. Lowest accumulated Intel Request penalties
4. Earliest successful Final Investigation submission, when applicable

Optional later table:

### leaderboard_snapshots

```txt
id
snapshot_at
snapshot_json
created_by_account_id
reason
```

Use snapshots only for freezing or archiving rankings, not as the main scoring source.

## 13. Announcements

### announcements

Stores admin-created platform messages.

```txt
id
title
body
status
created_by_account_id
published_at
archived_at
created_at
updated_at
```

Recommended constraints:

- `created_by_account_id` references an admin account
- `status` allowed values: `draft`, `published`, `archived`

Rules:

- Participants only see published announcements.
- Admin actions should be audit logged.

## 14. Platform Settings

### platform_settings

Stores event-wide controls.

```txt
id
key
value_json
updated_by_account_id
updated_at
```

Recommended keys:

```txt
registration_open
competition_status
leaderboard_visible
team_min_members
team_max_members
```

Default values:

```txt
registration_open = true or false, depending on organizers
team_min_members = 4
team_max_members = 5
leaderboard_visible = false until organizers enable it
```

Rules:

- Registration must read `registration_open`.
- Platform access should respect competition status.
- Settings updates must be audit logged.

## 15. Audit Logs

### audit_logs

Stores important admin and system actions.

```txt
id
actor_account_id
action
target_type
target_id
metadata_json
created_at
```

Recommended logged actions:

- team registered
- team approved
- team rejected
- team disabled
- admin logged in
- challenge created
- challenge updated
- challenge published
- challenge archived
- flag validator changed
- challenge file uploaded
- platform setting changed
- flag submitted
- challenge solved
- Intel Request used
- score adjusted
- Act unlocked
- announcement published

Security rules:

- Audit logs must not store plaintext passwords.
- Audit logs must not store plaintext flags.
- Metadata should be useful but not secret-bearing.

## 16. Recommended Migration Order

Build the backend in this order:

1. `accounts`
2. `teams`
3. `team_members`
4. `platform_settings`
5. `acts`
6. `challenge_categories`
7. `challenge_difficulties`
8. `challenges`
9. `challenge_flags`
10. `challenge_files`
11. `hints`
12. `submissions`
13. `solves`
14. `intel_requests`
15. `score_adjustments`
16. `act_unlocks`
17. `announcements`
18. `audit_logs`
19. optional `leaderboard_snapshots`

## 17. MVP Build Order

For the Sunday registration target, build only the minimum usable path first:

1. FastAPI foundation
2. PostgreSQL connection
3. Accounts table
4. Teams table
5. Team members table
6. Registration transaction
7. Login/logout/session
8. Admin approval
9. Frontend registration form
10. Frontend login flow
11. Pending/approved platform access states
12. QA for registration, login, and approval

## 18. Registration Transaction Rule

Registration should be one database transaction:

```txt
create account
create team with pending status
create 4 to 5 team_members
mark exactly one member as leader
ensure leader email matches account email
write audit log
commit
```

If any step fails, rollback everything.

## 19. Security Checklist

- [ ] Hash passwords.
- [ ] Do not store plaintext passwords.
- [ ] Do not store protected files in frontend `public/`.
- [ ] Do not expose plaintext flags through APIs.
- [ ] Do not log plaintext submitted flags.
- [ ] Use backend role checks for `/admin`.
- [ ] Use backend account/team checks for `/platform`.
- [ ] Use backend Act access checks for challenge visibility and file downloads.
- [ ] Use unique constraints for email, group name, and one solve per team/challenge.
- [ ] Use audit logs for sensitive admin/system actions.
- [ ] Keep cloud storage provider-neutral until the provider is final.

## 20. Final Recommended Schema List

Core tables:

```txt
accounts
teams
team_members
platform_settings
acts
challenge_categories
challenge_difficulties
challenges
challenge_flags
challenge_files
hints
submissions
solves
intel_requests
score_adjustments
act_unlocks
announcements
audit_logs
leaderboard_snapshots optional
```

This schema is normalized enough for the full CTF platform while staying practical for the first FastAPI backend implementation.
