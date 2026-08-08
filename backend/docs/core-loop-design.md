# Core CTF Loop — Design (#11, #13, #14)

Owner: **Dev 3**. Status: design frozen for implementation.

This covers the chain that makes the competition function: *admin creates a challenge →
team sees it → submits a flag → score awarded exactly once → next Act unlocks*.

Governing specs: `docs/packet-capture-developer-guide.md` (handoff) and
`docs/database-normalization.md` (DB spec). Where they conflict, this document names the
conflict rather than silently picking a side — see [Open decisions](#open-decisions).

> **Status:** this is the Wave 1 design deliverable. It was written before
> `docs/api-contract.md` was frozen, and the two disagree on error codes and statuses.
> **The frozen contract wins.** See
> [Contract reconciliation](#contract-reconciliation-required) for the exact deltas and
> the follow-up work they imply — the implementation described here has not yet been
> aligned.

---

## 1. Scope

| Issue | Delivers |
|---|---|
| #11 | `acts`, `challenge_categories`, `challenge_difficulties`, `challenges`, `challenge_flags`, `act_unlocks` + admin CRUD |
| #13 | `submissions`, `solves` + the flag submission flow |
| #14 | Scoring, Act threshold evaluation, participant challenge/progress reads |

**Not in scope** (other lanes): `challenge_files` (#16), `intel_requests` (#17),
leaderboard (#18), announcements (#19), admin log views (#20), Final Investigation (#22),
admin RBAC hardening (#9).

---

## 2. Terminology

Per handoff §5, the term is **Act** everywhere — UI, API fields, DB names, code.
Use `act_id`, `current_act`, `act_unlocks`. **Never** `level`, `current_level`,
`level_unlocks`.

- **Investigation Score** — the team score shown on the platform and leaderboard.
- **Intel Request** — a hint request that may deduct points (#17, not ours).

---

## 3. Schema

Follows the conventions already set by migration `20260807_0001`: UUID PKs
(`default=uuid.uuid4`), `DateTime(timezone=True)` with `server_default=func.now()`, enums
as `String(32)` + `CheckConstraint` (no PG enum types), UTC in storage.

### `acts`

| Column | Notes |
|---|---|
| `act_number` | Integer, unique. 1–4 |
| `slug`, `title`, `description` | `slug` unique |
| `unlock_threshold_points` | Integer **NULL** — absolute; **wins when set** |
| `unlock_threshold_percent` | Integer NOT NULL default `20` — fallback |
| `sort_order` | Integer, unique |
| `is_active` | Boolean default true — organizer act-wide lock |

Two threshold columns is the entire resolution of the 20%-vs-table contradiction (§6).

### `challenge_categories` / `challenge_difficulties`

Identical shape: `name` uniq, `slug` uniq, `sort_order`, `is_active`. Mandated by
`database-normalization.md`; without them `category` becomes free text that a later dev has
to migrate away from.

### `challenges`

| Column | Notes |
|---|---|
| `act_id` | FK `acts` RESTRICT |
| `category_id`, `difficulty_id` | FK RESTRICT, nullable |
| `title`, `slug` (uniq), `mission_brief`, `story_context` | |
| `objectives_json` | JSONB `list[str]` |
| `points` | Integer, check ≥ 0 |
| `status` | `draft` / `ready_for_review` / `published` / `archived` |
| `is_visible` | Boolean default true |
| `story_fragment` | String(64) NULL — **#22 only** |
| `sort_order` | |
| publish/archive/review audit columns | actor + timestamp |

**`status` and `is_visible` are deliberately separate.** Handoff §10 step 3 requires four
distinct checks — "published, visible, unlocked, accessible". `status` is the lifecycle;
`is_visible=false` is the organizer's emergency pull switch that doesn't reset publish
metadata.

`story_fragment` is written and read by admin CRUD, **never exposed to participants**, and
carries no logic here. #22 builds the Investigation Board on top of it.

### `challenge_flags`

Named per `database-normalization.md` (the handoff calls it `flags` — see
[Open decisions](#open-decisions)).

| Column | Notes |
|---|---|
| `challenge_id` | FK CASCADE |
| `flag_hash` | String(128), `hmac-sha256$v1$<64 hex>` |
| `validator_type` | check `('exact')` only |
| `label`, `is_active`, `created_by_account_id`, `deactivated_at` | |

Unique `(challenge_id, flag_hash)`; partial index where `is_active`.

`validator_type` intentionally allows only `exact`. Widening it later is a one-line
migration; allowing values we haven't implemented is how you ship a challenge that silently
accepts nothing.

"At least one active flag before publish" cannot be a DDL constraint — the publish endpoint
enforces it and returns `CHALLENGE_HAS_NO_VALIDATOR`.

### `act_unlocks`

`team_id` FK CASCADE, `act_id` FK RESTRICT, `reason` in
`initial`/`score_threshold`/`admin_override`, `source_score`, `threshold_points`,
`unlocked_at`, `revoked_at` NULL. **Unique `(team_id, act_id)`.**

Lives in #11's migration because it is part of the Act model and #13's lock check reads it.
#14 owns *writing* threshold-driven rows.

`source_score` and `threshold_points` snapshot the numbers at unlock time so an unlock stays
explainable after an admin edits points.

### `submissions` (#13)

`team_id`, `challenge_id` (both FK RESTRICT), `submitted_value_hash` (sha256 hex),
`submitted_value_preview` String(32) NULL, `is_correct`, `ip_address_hash`,
`user_agent_hash`, `submitted_at`. Index `(team_id, submitted_at)` serves the rate limiter.

**`submitted_value_preview` is populated only for incorrect attempts** (`raw[:8] + "…"`) and
set to `NULL` when correct. The only submissions guaranteed to *be* a real flag are the
correct ones, and an admin log screenshot is the likeliest leak path.

### `solves` (#13)

`team_id`, `challenge_id`, `submission_id` UNIQUE, `points_awarded` (check ≥ 0), `solved_at`.

**`UNIQUE (team_id, challenge_id)`** — this is the correctness guarantee, not a nicety.

`challenge_id` is `ondelete=RESTRICT` on purpose: it makes hard-deleting a solved challenge
impossible at the DB level, which is exactly the guardrail you want behind an admin delete
button during a live event.

`points_awarded` snapshots `challenges.points` at solve time, so re-pointing a challenge
mid-event never rewrites history.

---

## 4. Where the score lives — derived, no column on `teams`

`compute_investigation_score(team_id)` = `SUM(solves.points_awarded)`.

`database-normalization.md` §10 states it directly: *"Do not use `teams.total_score` as the
source of truth. Leaderboard should be computed from source records."*

The deciding argument is **ownership**, not performance. The eventual formula is
`solves − intel penalties (#17) + adjustments`, and two of those three terms belong to
developers landing later. A denormalized counter makes every future contributor a possible
source of silent score corruption — and score corruption in a live CTF is unrecoverable by
inspection. A derived score has exactly one definition in one function.

The `Team` API contract's `score` / `current_act` fields are satisfied as **computed
response fields**. No contract violation.

If leaderboard profiling ever demands it (#18), add `teams.cached_score` + `cached_at` as an
explicitly-labelled cache that scoring logic never reads.

---

## 5. Submission transaction

Isolation assumption: **PostgreSQL default `READ COMMITTED`**. We deliberately do not
require `SERIALIZABLE` — that would push retry loops into every call site, and correctness
here is achievable with one row lock plus a unique index.

Logic lives in `app/services/submissions.py::submit_flag(db, team, ...)`, **not the route**.
That split is what makes real concurrency testable: N threads × N sessions × N connections,
deterministically. `TestClient` cannot do that.

### Order (handoff §10)

```
team gating → competition open → load challenge → Act access check
  → rate limit → create attempt → validate
  → incorrect: commit, return
  → correct: finalize attempt → SAVEPOINT insert solve → evaluate unlocks
             → audit log → flush → single commit
```

### Two mechanisms, both required

**1. `SELECT ... FROM teams WHERE id = :id FOR UPDATE`**, taken before the rate check and
held to commit.

This is *not* redundant with the unique constraint. It fixes a second race the constraint
cannot see: a team submits correct flags for challenge A and challenge B concurrently.
Under READ COMMITTED neither transaction sees the other's uncommitted solve, so each
computes Act progress without the other's points. If A alone and B alone are each below
threshold but A+B crosses it, **no `act_unlock` row is created and the team is stuck on a
locked Act with a passing score**. That is a lost *read*, not a duplicate write — no unique
index catches it.

One row, one lock, always the same acquisition order, so no deadlock. A team is a single
shared account submitting from one UI; serializing their own submissions costs nothing real.
`lock_timeout` is set so a stuck lock surfaces as an error rather than a hang.

**2. `UNIQUE(team_id, challenge_id)` on `solves`**, wrapped in `db.begin_nested()`.

The DB-level arbiter and defence in depth — it is what still holds if a future code path
forgets the lock. With the lock held it should essentially never fire, but it must exist and
it must be tested.

### The SAVEPOINT subtlety

In PostgreSQL a constraint violation **aborts the entire transaction**; every subsequent
statement fails with `25P02`, and SQLAlchemy puts the `Session` in rollback-only state. So
the naive form:

```python
try:
    db.add(solve); db.flush()
except IntegrityError:
    db.rollback()      # ← also discards the submission attempt we are REQUIRED to record
```

...either loses the attempt row or explodes on the next query. `db.begin_nested()` issues a
real `SAVEPOINT`; on `IntegrityError` SQLAlchemy emits `ROLLBACK TO SAVEPOINT`, unwinding
only the failed insert and leaving the outer transaction alive.

The duplicate-submission test asserts **the second attempt row still exists** — that is what
catches anyone later "simplifying" this back to a plain rollback.

### The `autoflush=False` trap

`SessionLocal` is built with `autoflush=False`. A `select(func.sum(...))` will therefore
**not** flush pending ORM objects first — so a score read after `db.add(solve)` returns the
score *without* the new solve, and we hand the participant a stale number. Every
read-after-write in this path needs an explicit `db.flush()`.

### Atomicity

**Exactly one `commit()` per path**, at the end. Everything before it is one transaction;
any exception propagates and `get_db()`'s `finally: db.close()` rolls it back and releases
the lock. That satisfies "DB write failure during scoring must not create partial score
state" structurally rather than by care.

> **Review rule: no helper called by `submit_flag` may ever call `commit()`.**

### Information leakage

Unpublished, invisible, and nonexistent challenges all return **404 `CHALLENGE_NOT_FOUND`**.
Never distinguish them — distinguishing leaks the challenge roster before release.

---

## 6. Threshold resolution

```python
def resolve_threshold(act, act_total_points) -> int:
    if act.unlock_threshold_points is not None:
        return act.unlock_threshold_points
    return ceil(act_total_points * act.unlock_threshold_percent / 100)
```

**The contradiction.** The handoff says "20 percent of the total points of the current
challenge set" in three places. The flags table gives an explicit
*Minimum Required to Unlock Next Act* column:

| Act | Total | Table says | 20% would be |
|---|---|---|---|
| I — The Signal | 800 | **500** (62.5%) | 160 |
| II — The Breach | 1,125 | **700** (62.2%) | 225 |
| III — The Echo | 1,125 | **700** (62.2%) | 225 |
| IV — Beneath the Network | 1,000 | **700** (70.0%) | 200 |

Not even a consistent percentage, so no formula recovers the table. Per the website lead's
decision, **the seed ships the explicit table** in `unlock_threshold_points`, with
`unlock_threshold_percent = 20` retained as the fallback. Organizers can switch to the
percentage rule by nulling one column — no migration.

**Denominator = `published` AND `is_visible` challenges only.** The denominator must be
*reachable* points. Counting drafts means a challenge author leaving something unpublished
silently raises the bar and can make an Act mathematically impossible to escape.

Accepted consequence: unpublishing a challenge mid-event lowers the denominator and can
retroactively qualify teams. Combined with never-auto-revoke, progression is monotonic in
the team's favour — the right bias for a live event.

**Act progress uses raw solve points**, not penalty-adjusted score. Otherwise #17's hint
penalties could push a team *backwards* out of an Act they already entered, contradicting
"previously unlocked Acts remain accessible".

### Evaluation

`evaluate_act_unlocks()` iterates **all** unlocked Acts in `act_number` order, not just the
solved challenge's Act. That makes it self-healing — if an admin edits points or a
threshold, the team's next submission repairs their progression with no backfill job — and
lets a single call cascade multiple unlocks. Four rows; the cost is irrelevant.

Idempotent via `uq_act_unlocks_team_act` + savepoint.

Re-evaluated: inside the submission transaction, and via
`POST /admin/teams/{id}/recompute-progression`. **Never on a GET** — a GET must not write.

`ensure_initial_act_unlock()` grants Act I lazily (`reason='initial'`) so we never have to
touch Dev 1's registration route.

### Revocation

**Unlocks are never automatically revoked.** Nothing in our code sets `revoked_at`.
Act-wide organizer locking is `acts.is_active = false`, which removes the Act for everyone
without destroying per-team history. Per-team revocation is admin-only and not built until
organizers ask for it.

---

## 7. Flag validator storage — HMAC-SHA256 with a server-side pepper

Neither obvious option is right:

- **Argon2** (the existing `password_hash`) — wrong tool. ~50–100 ms per verify × multiple
  active validators per challenge, executed **while holding the team row lock**. That is a
  trivially reachable CPU DoS and makes the concurrency tests slow and flaky.
- **Plain SHA-256** — near useless here. Flags are low-entropy, human-authored, and follow a
  *published* format `PacketCapture{NAME}`. Anyone who dumps the DB recovers every flag with
  a wordlist in seconds — exactly the scenario hashing exists for.

**Chosen: HMAC-SHA256 keyed with `FLAG_HASH_SECRET`**, stored as `hmac-sha256$v1$<hex>`.

- Microseconds per verification — no CPU DoS, no lock held during hashing, fast tests.
- **A database dump alone is worthless.** Recovering flags needs the DB *and* the app
  environment secret. That is the realistic leak (a pg dump, a backup file, a `psql`
  screenshot in a group chat).
- Constant-time compare via `hmac.compare_digest`.
- The `$v1$` prefix makes key rotation a versioned re-hash, not a schema change.

Cost, stated plainly: **losing the pepper makes every stored validator unverifiable** and
flags must be re-entered. `FLAG_HASH_SECRET` goes in the same secret store as the session
secret, with a startup assertion that it is non-empty and not the example value outside
local env — a silently-defaulted pepper would mean every environment shares a key.

### Normalization

`normalize_flag(raw)` → **`raw.strip()` only**.

Per `database-normalization.md` §7: trim leading/trailing spaces; **do not** lowercase;
**do not** remove inner spaces; **do not** change punctuation. Handoff §5 requires
normalization rules to be organizer-approved and the rules §5 forbids guessing are exactly
these — we treat §7 as the approval and flag it for one-line confirmation.

Submissions longer than `MAX_FLAG_LENGTH` (512) are rejected **before** hashing.

**Never log the raw value or its normalized form, at any level.**

---

## 8. Rate limiting — DB-backed, no Redis

One indexed query over `submissions` (sliding window + per-challenge cap + cooldown).
Config in `platform_settings` key `submission_rate_limit`, so organizers retune mid-event
without a deploy.

Proposed defaults — **organizer-tunable, our proposal not a rule**: 60 s window,
5 per challenge, 20 per team, 2 s cooldown.

**Why this one is exact.** A DB counter under READ COMMITTED is normally only approximate,
because concurrent uncommitted inserts are invisible to `COUNT`. Here the limiter runs
*after* the team `FOR UPDATE` lock, so every prior submission by that team is committed and
visible. The limit is per-team and only that team can race its own counter — so the window
is exact for the only dimension that matters. Cross-team flooding is a reverse-proxy/WAF
concern, not this limiter's job.

**Rejected requests create no `submissions` row.** Counting rejections would let a spammer
extend their own lockout indefinitely (every retry pushes the window forward) and let anyone
inflate the submissions table without bound. They emit
`audit_logs(action="submission.rate_limited")` instead.

Returns 429 with `Retry-After`. Built on a generic `count_in_window()` helper so Dev 1 can
reuse it for the login rate limit mandated by handoff §15 (#9) rather than inventing a
second mechanism.

---

## 9. API contract (for #10)

**Frozen submission response** — `POST /challenges/{id}/submissions`:

```json
{
  "correct": true,
  "awarded_points": 100,
  "current_score": 350,
  "solved": true,
  "message": "Flag accepted.",
  "next_act_unlocked": { "id": "...", "act_number": 2, "title": "The Breach" }
}
```

`next_act_unlocked` is `null` when nothing new unlocked.

**Error envelope** — `{code, message, field_errors?}` per handoff §13:

```json
{ "code": "CHALLENGE_LOCKED", "message": "This challenge is not available yet." }
```

Delivered by `APIError(HTTPException)` putting a dict in `detail`, plus one exception
handler. **Existing auth routes are not touched**: the handler passes non-dict details
through as `{"detail": "..."}`, so `/auth/*` responses stay byte-identical and the frontend
cannot regress. Migration to codes is per-callsite whenever the auth owner wants it.

`RequestValidationError` is deliberately **not** handled — adding a handler would change
`/auth/register`'s 422 shape and break Dev 2's integration.

### Codes emitted

| Code | HTTP | When |
|---|---|---|
| `CHALLENGE_NOT_FOUND` | 404 | unknown, unpublished, or invisible |
| `CHALLENGE_LOCKED` | 403 | Act not unlocked for this team |
| `ALREADY_SOLVED` | 409 | duplicate correct submission |
| `RATE_LIMITED` | 429 | window exceeded (+ `Retry-After`) |
| `COMPETITION_CLOSED` | 403 | submissions disabled |
| `TEAM_NOT_APPROVED` | 403 | approval required and not granted |
| `TEAM_REQUIRED` | 403 | account has no team |
| `ADMIN_REQUIRED` | 403 | non-admin on `/admin/*` |
| `CHALLENGE_HAS_SOLVES` | 409 | delete blocked; archive instead |
| `CHALLENGE_HAS_NO_VALIDATOR` | 422 | publish blocked; no active flag |
| `VALIDATION_ERROR` | 422 | field errors from our routes |

A locked **Act** returns `CHALLENGE_LOCKED`, not a new `ACT_LOCKED` — handoff §13 froze that
code and the participant-visible outcome is identical. The message differentiates.

---

## 10. Admin guarding (seam with #9)

`get_current_admin` and `get_current_team` go in the **existing** `app/api/deps.py`, ~6
lines each. #9's owner expands the bodies (admin session policy, scopes, step-up auth); our
routes depend on the **name**, not the implementation.

A separate `deps_admin.py` would be worse — #9 would then have two places to reconcile and
would likely delete ours.

Attached at **router level**, not per-route, so no endpoint can forget it:

```python
app.include_router(admin_challenges.router, prefix="/admin", tags=["admin"],
                   dependencies=[Depends(get_current_admin)])
```

> **Contract for #9 to preserve:** `Depends(get_current_admin) -> Account`, raises 403
> `ADMIN_REQUIRED`. Internals are theirs to rewrite.

**Team approval** is gated on `platform_settings["require_team_approval"]`, default
**false**. The handoff lists "whether registration requires organizer approval" as an
explicit *Pending Organizer Decision*, so it becomes config rather than a guess — and the
end-to-end milestone stays testable before #9 ships an approval route.

---

## 11. Test plan

Real PostgreSQL, **never SQLite** — SQLite cannot express partial unique indexes (already
used in `0001`), `SELECT ... FOR UPDATE`, or JSONB. It would pass while production is
broken, the worst possible outcome for scoring code.

Isolation by `TRUNCATE ... RESTART IDENTITY CASCADE`, **not** transaction-rollback: the code
under test commits, and the concurrency tests need genuinely committed transactions on
separate connections. Test engine `pool_size` must exceed the thread count or the
concurrency test deadlocks on connection checkout and looks like a scoring bug.

Mandated paths (handoff §17): **correct · incorrect · duplicate · locked · concurrent**.

| Test | Asserts |
|---|---|
| Correct | 1 attempt `is_correct=true`, 1 solve, `points_awarded == challenge.points`, preview `NULL` |
| Incorrect | 1 attempt, **0** solves, score unchanged, preview truncated ≠ submitted value |
| Duplicate | 409 `ALREADY_SOLVED`, still 1 solve, **2nd attempt row still exists** (proves the savepoint) |
| Locked | 403 `CHALLENGE_LOCKED`, **no** attempt row |
| Draft | 404 `CHALLENGE_NOT_FOUND`, not 403 — roster not leaked |
| Concurrent A | 8 threads on a `Barrier` → exactly 1 solve, exactly 1 caller with points, rest `ALREADY_SOLVED`. **Must also pass with the team lock removed**, proving the constraint+savepoint backstop is not dead code |
| Concurrent B | Deterministic collision: A inserts uncommitted, B blocks on the index, A commits → B gets `ALREADY_SOLVED` *and* B's attempt row survives |
| Concurrent C | Two simultaneous correct submissions for *different* challenges whose sum crosses the threshold → unlock **is** created. Fails without the team lock |

Progression: `earned == required` unlocks and `required − 1` does not;
`unlock_threshold_points=500` overrides `percent=20` on the 800-point Act I (pins the
documented contradiction as a test); NULL falls back to the percentage; drafts excluded from
the denominator; archiving a solved challenge does not change historical score.

Security regression: sweep every participant response asserting `PacketCapture{` never
appears and no `flag`/`flag_hash` key is present; assert `caplog.text` contains neither the
raw nor normalized flag after correct and incorrect submissions; non-admin → 403 on every
`/admin/*`.

---

## Contract reconciliation required

`docs/api-contract.md` was frozen after this design was written. It is the declared
single source of truth, so **every disagreement below resolves in the contract's
favour** and the code must change, not the contract.

| Situation | This design / current code | Frozen contract | Action |
|---|---|---|---|
| Challenge locked for team | 403 `CHALLENGE_LOCKED` | **422 `LOCKED_CHALLENGE`** | rename + restatus |
| Already solved | 409 `ALREADY_SOLVED` | **422 `ALREADY_SOLVED`** | restatus |
| Unknown/unpublished challenge | 404 `CHALLENGE_NOT_FOUND` | **404 `NOT_FOUND`** | rename |
| Submissions disabled | 403 `COMPETITION_CLOSED` | **403 `SUBMISSIONS_CLOSED`** | rename |
| Non-admin on `/admin/*` | 403 `ADMIN_REQUIRED` | **403 `FORBIDDEN`** | rename |
| Request validation failure | 422 `VALIDATION_ERROR` | **400 `VALIDATION_ERROR`** | restatus |
| Unauthenticated | `{"detail": "..."}` | **401 `AUTH_REQUIRED` / `SESSION_EXPIRED`** | owned by auth (#9) |

Two codes in this design have no contract equivalent because they are admin-only and the
contract does not cover admin error cases: `CHALLENGE_HAS_SOLVES` (delete blocked by a
recorded solve) and `CHALLENGE_HAS_NO_VALIDATOR` (publish blocked with no active flag).
They should be added to the contract rather than dropped.

One point to raise rather than implement silently: the contract specifies **422** for
`ALREADY_SOLVED`. 409 Conflict is the conventional status for "this already exists", and
422 normally means the request body was unprocessable — which is not what happened. The
contract's own preamble says to stop and ask the website lead on conflicts, so this needs
a ruling before the rename lands. The rename itself is not in dispute; only the status.

Note also that the contract records the backend as "currently returning plain `detail`
strings" with the envelope as a target. That is now out of date: the `{code, message}`
envelope described in §9 is implemented, and existing auth routes were deliberately left
on the old shape so the frontend could not regress.

## Open decisions

Flagged rather than guessed, per handoff §1.

1. **Act thresholds** — the 20% rule vs. the explicit 500/700/700/700 table. Lead chose the
   table; seeded as data, with the percentage retained as fallback. Are those numbers final
   given point totals may still shift as challenges are authored?
2. **Act IV's threshold gates nothing in our scope** — there is no Act V. It presumably
   gates the Final Investigation (#22). Seeded but unused by us.
3. **Do Intel penalties (#17) reduce Act-progression eligibility, or only leaderboard
   score?** We implement leaderboard-only. Needs sign-off *with* #17's owner, whose code
   could otherwise change our numbers by accident.
4. **Act denominator = published AND visible.** Recommended; materially changes thresholds,
   so worth explicit confirmation.
5. **Trim-outer-whitespace normalization** — `database-normalization.md` §7 specifies it;
   handoff §5 says such rules need organizer approval. We treat §7 as the approval.
6. **`ALREADY_SOLVED` — 409 envelope, or 200 with `awarded_points: 0`?** We implement 409.
   Belongs in the #10 contract freeze, not a unilateral call.
7. **Rate limit numbers**, and whether rejected attempts count against the window (we say
   no).
8. **Table name `flags` (handoff §12) vs `challenge_flags` (normalization doc).** We use
   `challenge_flags`.
9. **May admins revoke a team's Act access per-team?** Column exists; no endpoint until
   asked.
