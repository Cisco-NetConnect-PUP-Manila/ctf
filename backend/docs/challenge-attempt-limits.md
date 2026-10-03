# Challenge attempt limits

In the organizer Challenge Editor, set **Maximum attempts per team** to a whole number
from 1 to 100000, or leave it blank for **Unlimited**. The same field edits an existing
challenge; the challenge manifest shows the saved policy.

Limits apply to each team separately and are shared across all its members, sessions,
and devices. Every evaluated flag (correct or incorrect) counts. Invalid requests,
locked challenges, cooldown denials, and already-solved denials do not consume attempts.
Existing recorded submissions count when a limit is added or changed. Setting a smaller
limit can immediately exhaust a team's budget; raising it or clearing it restores access
without deleting history. No score is deducted merely for exhausting the budget.

The backend enforces count-and-insert under its per-team database lock, so simultaneous
submissions cannot bypass the limit. Participants see their remaining attempt count and
cannot submit through the form when it reaches zero. Direct API requests are still
rejected with `403 ATTEMPTS_EXHAUSTED`. Reload the participant page after an organizer
changes the budget to see the new policy.

API: `max_attempts` is a nullable integer on admin create/update and all challenge
responses. On update, omit it to preserve the current value or explicitly send `null`
to restore unlimited. Participant responses also include `attempts_used` for their own
team only. Existing challenges remain unlimited after the migration.

Test locally: rebuild Docker, create a challenge with a limit of 2, publish it with a
flag, submit two wrong flags as an approved team (observe the usual cooldown), and
verify that a third flag cannot be evaluated. Raise the limit to 3 and reload; one
attempt should be available. Verify a different team retains its own full budget.
