# ADR 0002: Team-Specific Solve Fragments

## Status

Accepted

## Context

Participants can share challenge URLs, screenshots, files, and answers outside the
platform. A CTF site cannot fully prevent human answer sharing, but it can make copied
solve artifacts less useful and keep all real validation server-side.

The project needs to support shared challenge files such as `.raw`, `.pcap`, `.dd`,
`.png`, `.txt`, `.pkz`, and `.pka`, while still giving each team a unique-looking solve
fragment after a correct submission.

## Decision

Use one shared challenge record and shared challenge files by default. Protect all
challenge pages, file downloads, and submissions with authenticated backend checks.

When a team solves a challenge, the backend derives a visible team-specific fragment
from:

- `team_id`
- `challenge_id`
- `TEAM_FRAGMENT_SECRET`

The fragment is returned to that same team after a correct solve and can be derived again
when the team reopens the solved challenge. The database stores only a keyed hash and a
short preview for audit metadata, not the plaintext fragment as source of truth.

## Consequences

- Sharing a challenge URL does not bypass auth, unlock, or visibility checks.
- Sharing Team A's solve fragment does not give Team B the same proof token.
- Shared uploaded challenge files remain simple and cloud-friendly.
- If a future challenge requires embedded per-team flags inside files, that should be a
  separate per-team artifact-generation feature, not a replacement for this baseline.
