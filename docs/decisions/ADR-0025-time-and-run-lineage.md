# ADR-0025: Bounded self-scheduling and data-only run lineage

Status: Accepted for S018. Extends versioned runtime policies and complete-step
checkpoints; preserves supervisor deadline authority and three-repository roles.

## Time and waking

Habitat 0.5.0 reserves `supervisor-time` services `time.remaining` and
`time.sleep`. Remaining time is an integer-millisecond snapshot of the original
active wall-clock budget, excluding operator-paused downtime and excluding any
deadline grace. It is advisory, not a promise of execution time or a way to
extend the deadline.

New policy `self-scheduled-v1` retains quiet idling after tool-free replies and
adds explicit sleep requests. `time.sleep {seconds: N}` schedules one wake at a
relative active-time target; N is a positive integer bounded by configured
`max_sleep_s` (1-3600, default 3600) and the remaining original budget. It returns
immediately, then inference stops at the complete-turn barrier. Further calls
in that same turn are refused. The supervisor binds requests to recorded calls,
rechecks policy/permissions and records scheduling/waking. It refuses model
input preparation while a wake is pending. No artificial message, tool call,
model inference or simulated field advance occurs during waiting.

The existing 250 ms state-barrier cadence checks wakes while retaining deadline,
resource and pause enforcement. Sleeping consumes active time. Private wake
state is inserted into protected checkpoints by the supervisor, never accepted
from worker state. A durable-in-checkpoint wake-ready latch handles a checkpoint
at the wake/acknowledgement boundary. Resume preserves the active-time target;
paused wall time does not bring it forward. Quiet/legacy policy behaviour is
unchanged. A quiet idle with no requested wake remains idle until stopped.

## Run lineage

Operator-only `ols run CONFIG --from-run ARCHIVE` creates a new run from a
verified completed parent's final complete-step checkpoint, never its live
workspace. The source must be under the selected data root, stopped and locked;
the final snapshot must match the terminal completed-step count. Protected
workspace ZIP and SQLite snapshot bytes are copied and pinned in the child
archive before safe restoration into a fresh child workspace.

The child records a portable `lineage.json`, copied source snapshot evidence and
a launch-event digest binding. The parent gets an exclusive child-reference
sidecar under `children/`; its existing log, summary and checkpoint bytes remain
unchanged. These are recorded links, not a cryptographic chronology attestation.
Each archive can be verified independently; portable verification does not
require its relatives. A parent sidecar does not attest a child's final outcome.

Only workspace files and agent memory transfer. Child conversation, model,
permissions, budgets, policy, wake schedule, private phenomena state and trusted
executable-tool registrations start fresh from its own configuration. Saved
source/procedures are files; executable tools must be revalidated in the child.
No claim of cognitive continuity is made. New lineage cannot be requested by an
agent capability or inferred from a prompt. Cross-root imports are excluded.

## Validation and exclusions

Acceptance uses fake clocks for boundaries and real supervisor/container flows
for sleep/wake, pause/resume, deadline priority and two-run project continuation.
Corrupt/live/incomplete sources, path escapes, snapshot tampering and authority
inheritance are refused/tested. No new dependencies, downloads, hosted inference,
system scheduler, new network access or field-time automation are needed.
Existing schema extensions and checkpoint components suffice. S019 remains next
only after all S018 acceptance checks pass.
