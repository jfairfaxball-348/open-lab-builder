# S006d engineering check: bounded supervisor recovery

Date: 2026-11-14. These are engineering checks with scripted/fake models, not
experiments about agent behaviour. No model download, system setting change,
OS startup task or real host reboot was performed.

## Delivered scope

Opt-in `extensions.recovery`, one long-lived supervisor across worker segments,
a shared persisted restart budget, pre-execution model-attempt reservations,
active-time accounting, OS writer serialization with verified process birth
identity, interrupted-run startup scanning (`ols recover`) and asynchronous
model-server identity/availability probes. ADR-0011 specifies policy, actions,
accounting and refusal behaviour. Contracts use existing extension objects;
no schema, world release or copied world fixture changed. No dependency added.
Resource enforcement/sampling remain S006e.

## Automated validation

Baseline Builder: `uv sync`, `uv run olb state`, `uv run olb check --tests`:
305 tests and all six health checks passed. Baseline Simulation: `uv sync`,
`uv run pytest`: 159 tests passed.

Simulation `uv run ruff check .` passed. Full `uv run pytest` passed 186 tests
(27 new recovery tests). The native supervisor-death test was then tightened
to kill the archive's exact verified supervisor PID, because a Windows virtual
environment redirector can have a different PID; the focused test passed.
Two mocked Linux identity-path tests were added to distinguish a missing process
from an unreadable boot identity; these do not constitute Linux execution.
Final post-review `uv run ruff check .; uv run pytest` passed: 188 tests in
123.11 seconds, including 29 new recovery tests. Simulation committed and
pushed as `7e636d4`.
Builder `uv run ruff check .` and `uv run olb check --tests` passed: 305 tests
and all six health checks. Privacy and whitespace checks passed in both repos.

Coverage includes a real worker kill and automatic checkpoint recovery;
repeated crashes exhausting the shared retry budget; manual resume unable to
bypass that budget; deadline and interrupted model attempts retaining original
budgets; a killed real Windows supervisor, confirmed worker death via Job
Object, stale-owner evidence and startup resume of the same append-only archive;
downtime exclusion with conservative reservation charging; live OS locks,
live process birth identities, PID reuse, absent owners, foreign/malformed
owners and inspection failure; corrupt/partial logs, corrupt checkpoints,
invalid accounting and exhausted step budgets; no replay of completed or
unopted runs; failed/expired accounting; invalid configuration and missing
checkpoint configuration; fake-model health success/failure, missing identity
and a supervisor timeout for a blocked health probe. Existing pause/resume,
artifact, model, authority and checkpoint-integrity tests remain enabled.

Refusals append supervisor actions only under exclusive ownership of a valid
log. Unsafe ownership and partial logs are left unchanged and reported by the
CLI. A refusal does not forge a summary. No assertion was weakened or failing
test omitted.

## Independent native CLI checks

The shipped `experiments/scripted-recovery.json` uses minimal world 0.6.0,
two delayed scripted steps, working notes and SQLite memory, a 20-second budget,
eight attempt slots and two allowed restarts. A separate harness launches the
CLI and inspects its own newly created archive. It verifies the supervisor and
worker's recorded OS birth identities before fault injection. Raw command
output and local-only harness evidence are under Simulation `.local/s006d/`.

- First harness: its extra assumption that launcher PID equals supervisor PID
  failed before injecting the worker fault. Cleanup interrupted the run. Both
  recorded processes were subsequently confirmed absent, and the startup scan
  resumed `run-20261114t111721z-d1fda6` to completion with a retained stale-lock
  marker. It finished with 35 events and 4.078 active seconds; `ols verify`
  reported the archive intact. The harness assumption was corrected.
- Verified worker fault: `run-20261114t111831z-64db06` completed after one
  automatic restart, with 37 events and 3.282 active seconds. Its existing log
  prefix was preserved byte for byte. Three completed model calls and five
  reserved attempts were recorded (including the interrupted attempt and the
  scripted end probe). The CLI and separate `ols verify` both exited zero.

Run archives/workspaces and raw output remain outside version control.

## Limits and next milestone

Next: **S006e — Resource Enforcement and Sampling**.

This is process-tier recovery for Builder-written tools, not container
isolation. Physical reboot/power loss, Linux execution, long unattended runs and
uninterruptible host-I/O timing remain unverified. Active accounting records
observed time and durable reservations, not an inferred exact crash instant;
unused reservation time may be charged. Partial observation/artifact writes or
unverifiable legacy ownership are refused rather than repaired by inference.
A healthy identity probe does not guarantee inference readiness. Startup scans
are explicit and sequential; no boot service or parallel scheduler is installed.
