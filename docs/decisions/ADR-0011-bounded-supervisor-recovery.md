# ADR-0011: Bounded supervisor and interrupted-run recovery

Status: Accepted (S006d). Extends ADR-0009 manual resume and ADR-0010 deadlines.

## Context

The supervisor must outlive runtime crashes without changing the experiment's
limits. A PID alone does not prove that a writer is alive: it can be reused,
or belong to a different machine. An interrupted model call also consumes work
even when no reply event was recorded. Recovery must not erase that evidence
or silently turn an interrupted archive into a new experiment.

## Decision

- Recovery is explicitly configured under the experiment's existing
  `extensions.recovery`. No configuration is read from prompts, tools or agent
  memory. Checkpointing is required. `max_restarts` is required (integer 0–100);
  `auto_resume` defaults false; health interval/timeout default 5/2 seconds and
  each accepts finite numbers from 0.05 to 60. Unknown fields and booleans where
  numbers are expected are refused before launch. This is an extension trial,
  not a change to the schemas or world release.
- One long-lived supervisor holds the writer guard across worker segments. On
  unexpected worker exit or model failure it kills/closes the previous tree,
  verifies the archive and world/model identities, restores a valid checkpoint,
  and starts a recovery segment. A synced supervisor action with extension stage
  `recovery_restart` debits the retry budget before a new worker can start.
  All segments and startup scans count the same recorded debits. Failed
  revalidation is a refusal, not an unbounded retry loop. A manual restart of a
  failed opted-in run also debits this budget; cooperative pause/resume does not.
- Before each model attempt, the worker waits for the supervisor to record and
  sync `supervisor.action` stage `model_step_reserved`. Accounting uses the
  greater of reserved attempts and completed `model.call` events. Interrupted
  attempts and a scripted end-of-input probe may consume a reservation without
  a completed-call event. No reservation grants more time or steps.
- A supervisor-only `.supervisor.json` ledger is atomically replaced after file
  fsync, reserving one second ahead of observed active time, renewed every 0.2
  seconds. The supervisor checks lease expiry before allowing more work and
  stops on accounting failure. Interrupted recovery uses the greatest of this
  durable reservation, checkpoint progress and event time. Downtime is not
  reconstructed from wall-clock timestamps. The unused part of a reservation
  can be charged conservatively. Normal stopped segments use actual elapsed
  time; successful revalidation/restoration time is also charged. Original
  time/step budgets and deadline grace are never replenished.
- The permanent `.writer.guard` inode carries an OS exclusive lock. It is never
  unlinked to avoid POSIX inode-replacement races. The separate marker records
  a hashed installation identity, PID and OS process creation identity
  (Windows FILETIME; Linux boot id and process start ticks). A matching live
  owner, foreign/legacy/malformed marker or inability to inspect is refused.
  Only a verified dead/reused owner may have its marker retained in `segments/`
  and replaced while the guard is held. No process is killed by PID for takeover.
- `ols recover` is the startup entrypoint. It scans only missing-summary,
  explicitly opted-in archives. It requires a complete valid event log, valid
  accounting, unchanged world/model digests and a usable checkpoint. A known
  stopped/completed state is refused for review rather than replayed. The old
  runtime must be absent; on Linux an extant process group also causes refusal.
  No OS startup registration or machine configuration is installed.
- Event logs remain append-only. Corrupt snapshots may be bypassed but remain
  visible to verification. Partial event lines, inconsistent artifact records
  and invalid accounting cause refusal; nothing is trimmed or repaired by
  inference. Refusal/exhaustion actions are recorded when the supervisor owns
  a valid log. Live/unverifiable ownership and invalid logs are reported by the
  CLI without attempting an unsafe archive write. A missing summary remains
  missing on refusal; it is not forged into a completed archive.
- Model health probes are read-only loopback `/api/tags` requests that check the
  original digest. They run off the deadline thread, one pending probe per
  segment, with a supervisor timeout. Health observations use supervisor action
  stage `model_health`. Failure kills the tree and uses the same bounded retry
  path. A missing/changed model can cause immediate revalidation refusal.

## Limits and alternatives

A stale PID marker alone is not a lock. Rewriting an event tail to make resume
work would destroy observations. Treating an absent reply as free computation
would grant extra steps. None is used.

The process tier remains an architectural boundary for Builder-written tools.
Resource limits/sampling remain S006e. Linux implementation, physical host
reboot, power-loss durability and long-run performance have not been exercised.
OS scheduling, host suspension, uninterruptible I/O and directory-entry power
loss are not covered by a hard real-time or exact crash-instant accounting
guarantee. The ledger records durable reservations, not an inferred death time.
A healthy identity probe does not guarantee inference readiness. Startup scans
run opted-in archives sequentially; parallel run scheduling is outside S006d.
