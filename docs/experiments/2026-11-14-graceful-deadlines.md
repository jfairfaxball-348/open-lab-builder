# S006b engineering check: graceful deadlines

Date: 2026-11-14. This is runtime engineering acceptance, not an experiment
about agent behaviour. No real model was called.

## Scope

The former Independent Supervisor and Recovery milestone was split before
implementation: S006b is graceful deadline checkpointing; S006d is automatic
runtime/interrupted-run recovery and stale locks; S006e is resource enforcement
and sampling. Completing S006b does not complete the original combined scope.

ADR-0010 defines the fixed grace allowance. No schemas, capability manifests,
world sources, built releases or copied fixtures changed.

## Automated validation

Baseline: Builder `uv sync`, `uv run olb state`, `uv run olb check --tests`
passed all health checks and 305 tests. Simulation `uv sync` and `uv run pytest`
passed 147 tests.

Simulation `uv run ruff check .` passed; final `uv run pytest` passed 159
tests, including 12 new deadline tests. Source committed and pushed as
`ce102f9`.
Builder `uv run ruff check .` passed; `uv run olb check --tests` passed all
six health checks and 305 tests. Privacy checks passed in both repositories.

The new deadline tests use real worker and capability processes with a scripted
model. They check consistent memory, files, conversation and cursor at the
saved step; no next step; busy model and capability termination at grace expiry;
zero/omitted grace; hard stop ignoring grace; snapshot timeout preserving the
previous snapshot; original budgets after pause/resume; normal early completion;
and a snapshot crossing the nominal deadline without releasing the worker.
Initial snapshot timeout also records the deadline request even when no safe
snapshot has yet been published. A queued-barrier regression test checks that post-kill draining never snapshots
a state whose workspace may have changed. Existing tests continue to cover
refusal without checkpointing, original step budgets, hash chains and snapshot
integrity/cleanup. No failing assertion was removed or weakened.

## Shipped CLI example

Command: `uv run ols run experiments/scripted-graceful-deadline.json`.
The configuration uses minimal world 0.6.0, a two-second active-time budget,
three-second grace and a delayed first step that writes memory and NOTES.md.
Its second scripted reply must never start.

Run: `run-20261114t104818z-7d6fec`. Result: terminated for deadline in 2.703
active seconds, 19 events, one model step, two successful tool calls, two
checkpoints and two supervisor actions. The final checkpoint is
`pre_shutdown`, step count 1, with memory and working notes preserved. The
supervisor recorded the deadline request and termination. The following step
was absent. `ols verify` reported the archive intact. Archives and workspaces
remain outside version control.

## Remaining limits and exact next milestone

Next: **S006d — Runtime and Interrupted-Run Recovery**. Automatic crash/reboot
recovery, stale-lock ownership checks and model health supervision are not
implemented. Resource limits/sampling remain S006e; deadline notices are still
refused. Container isolation remains blocked by the existing human WSL/engine
actions. Checkpoint checks are cooperative between I/O chunks; uninterruptible
host I/O and large-run timing bounds are unverified. All execution in this
session was on Windows; Linux behaviour remains unverified.
