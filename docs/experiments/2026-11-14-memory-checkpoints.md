# S006a memory and checkpoint engineering validation

Date: 2026-11-14. All runs here are scripted engineering checks. No real model
was called, downloaded or changed. OD-2 remains deferred.

## Delivered scope

Minimal world **0.6.0** adds `memory.write`, `memory.search` and `memory.list`
to the previous five capabilities. They use standard-library SQLite, bounded
JSON arguments and parameterised SQL; no dependency was added. The live memory
is agent-owned `.memory.sqlite` workspace data. `NOTES.md` is the optional
working-notes convention. The memory-location decision and the consistency
protocol are in [ADR-0009](../decisions/ADR-0009-checkpoint-barriers-and-agent-memory.md).

The supervisor checkpoints at complete-step barriers while the runtime waits:
initial state, intervals when due, and before normal completion/operator pause.
A snapshot contains conversation JSON, runtime cursor/counters, a consistent
SQLite backup and a ZIP of the remaining workspace. Metadata and components
are digest-bound; staging is published only after validation. Configured
retention is recorded in checkpoint events. Checkpoint-metadata **1.0.1**
clarifies that its event sequence is the snapshot boundary; resume appends
after the existing event-log tail and records rollback/replay.

`ols resume <archive>` verifies the stopped archive, selects the newest valid
unpruned snapshot, restores files/memory/conversation and appends to the same
run. Corrupt snapshots are rejected with recorded fallback. No prior event is
deleted. Correlation ids, artifact history, consumed steps and active time
continue; downtime is excluded and limits cannot be replenished. Former
workspaces, segment summaries and stderr are retained. Writer locks prevent
concurrent segments; changed model/world digests are refused.

## World release

```text
uv run olb world build worlds/minimal
uv run olb world verify releases/minimal/0.6.0 --self-test
uv run olb world build worlds/minimal --publish
```

Build, capability self-tests, verification and publication passed. Local and
published content digests match:

```text
1ccc407cc300e7622bcca348ff22c5982bff5cf3a10559ee741304350e960da5
```

The Simulation fixture was copied from the built release, never edited by
hand. Existing experiment configurations select 0.6.0. No weights, raw archives
or personal paths are committed.

## CLI pause/resume acceptance

The committed `experiments/scripted-memory-checkpoint.json` writes memory and
working notes, recalls the memory, revises both, and writes a final result.

```text
uv run ols run experiments/scripted-memory-checkpoint.json --pause-after-steps 2
uv run ols verify <archive>
uv run ols resume <archive>
uv run ols verify <archive>
uv run ols run experiments/scripted-memory-checkpoint.json
```

The first paused/resumed run, `run-20261114t101754z-4732b4`, verified before and
after resume and completed with **46 events**, consuming **1.563 seconds** of
active time. A second pause/resume check, `run-20261114t102559z-6ec3af`, also
completed with **46 events** and verified. Its wall time was **213.468 seconds**,
but accumulated active time was **1.531 seconds**: the pause was excluded.

The uninterrupted comparison, `run-20261114t101845z-72daf9`, completed with
**38 events** and **1.093 seconds** of active time. All resumed workspaces had
the same ordinary file bytes as this reference (`NOTES.md` and `result.txt`).
SQLite queries returned the same logical memory state and revision:
`("plan", "revised", 2)`. Database page-header bytes need not be identical after
SQLite backup; the comparison is of stored records. Checkpoint metadata
validated against the bundled 1.0.1 schema.

These three real infrastructure archives remain under the local data root and
pass the current archive verifier. The second resume also exercised reading
the local prototype's earlier event-extension spelling; newly written protocol
extensions are grouped under payload `extensions`.

## Automated acceptance and failure cases

The tests compare uninterrupted execution with a paused/resumed scripted run,
including files, memory revisions, conversation cursor, event sequence/hash
chain and unique call ids. They corrupt the latest snapshot, verify that
corruption is reported, resume from the preceding snapshot and confirm the
same final contents without erasing observations. The corrupt copy remains
forensics, so full archive verification continues to report it; the event log
and preserved artifacts remain valid.

Additional coverage includes interval/pre-shutdown snapshots, retention,
SQLite corruption and literal search, schema bounds and SQL-like text as data,
partial-log refusal, competing writer locks, no-checkpoint/completed-run
refusal, exhausted step/time budgets, downtime exclusion, checkpoint-timeout
cleanup and recorded deadline enforcement, ZIP traversal/backslash rejection,
cleanup boundaries, operator-edit backups, stderr preservation, and a
simulated operator interrupt. Fake-model-server tests verify that the saved
conversation reaches the next request and that a changed model digest is
refused before restoration. Final command results are in
[`state.json`](../roadmap/state.json).

## Remaining limits

S006a covers cooperative operator pause and manual resume of stopped runs with
summaries. Hard deadlines kill the runtime and retain the preceding safe
snapshot, without trying to capture a partially executed tool. Automatic crash
or reboot recovery, stale-lock handling and `checkpoint_then_stop` orchestration
remain **S006b**; that deadline mode is explicitly refused. Native console-signal
delivery, uninterruptible host I/O, large/long runs, real-model memory use and
Linux execution remain unverified. The process tier is still not an OS sandbox.
