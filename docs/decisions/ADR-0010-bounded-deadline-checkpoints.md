# ADR-0010: Bounded graceful deadline checkpoints

Status: Accepted (S006b). Supersedes ADR-0009's temporary refusal of
`checkpoint_then_stop`; the complete-step protocol is unchanged.

## Context

A checkpoint taken during a capability execution can mix conversation and
filesystem states. Waiting indefinitely for a barrier would give an agent
control over termination. The existing experiment contract already provides
`checkpoint_then_stop` and `grace_period_s`, but leaves scheduling details to
the supervisor implementation.

## Decision

- This mode requires checkpointing. The original active-time budget determines
  the nominal deadline. At that point the supervisor records a
  `supervisor.action` with action `limit_enforced` and extension stage
  `deadline_checkpoint_requested`. It does not ask the model for permission.
- A configured `grace_period_s` is one fixed additional allowance after that
  deadline for finishing the in-flight step and writing its snapshot. Omitted
  grace means zero. No new step starts after a deadline barrier. This allowance
  is not a fresh experiment budget and is never renewed by manual resume.
- The worker remains blocked at the complete-step barrier while the supervisor
  saves the snapshot. The supervisor kills the process tree before sending an
  acknowledgement, records `supervisor.action: terminated`, and ends the run
  as `terminated` with reason `deadline`. A deadline snapshot uses the existing
  `pre_shutdown` metadata reason. If an interval/final snapshot itself crosses
  the nominal deadline, that consistent snapshot is used and the worker is
  stopped without starting another step.
- At grace expiry the supervisor kills the tree. Queued observations are still
  recorded, in order; queued state barriers are not snapshotted after killing.
  A timed-out snapshot leaves the preceding published snapshot intact. Neither
  a hung model nor a hung capability can renew the allowance.
- Hard-stop behaviour is unchanged and does not use grace. Active elapsed time
  includes grace; exhausted original budgets still refuse manual resume.
- Existing event enums and payload extensions express these observations; no
  schema, world-release or fixture change is needed.

## Alternatives and limits

Killing first and snapshotting the resulting workspace would not preserve a
complete step. An unbounded cooperative shutdown would surrender supervisor
authority. Neither is used.

This remains a process-tier implementation for Builder-written capabilities,
not an OS sandbox. The supervisor's checkpoint deadline checks run between file
chunks and SQLite backup pages. Uninterruptible host I/O, large-run performance
and Linux behaviour remain unverified; this is not a hard real-time guarantee.
The generic continuation may be recorded while an in-flight step finishes;
there is no model-facing deadline notice in this milestone.

The former S006b scope is split: automatic runtime/interrupted-run recovery,
stale-lock handling and model health checks are S006d; resource limits and
sampling are S006e. Those remain designed, not implemented.
