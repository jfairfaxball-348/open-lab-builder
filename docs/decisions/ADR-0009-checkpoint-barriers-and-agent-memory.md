# ADR-0009: Complete-step checkpoints and agent-owned memory

Status: Accepted (S006a). Refines ADR-0007's memory-location clause; the
append-only log and supervisor-owned checkpoint decisions remain unchanged.

## Context

A consistent checkpoint must not pair a conversation from before a tool call
with files from after it. Falling back from a corrupt snapshot must also keep
all observations already written. The original checkpoint schema described the
snapshot boundary correctly but incorrectly suggested that every resume could
append immediately after that boundary, even when the log had advanced.

World capabilities are self-contained, testable in the Builder, and cannot
import Simulation code. Keeping the live memory database in the supervisor's
area, as originally designed in ADR-0007, would require a new privileged memory
RPC protocol or a second storage-path exception to the invocation protocol.

## Decision

- The live SQLite database is **agent-owned data** at `.memory.sqlite` inside
  the workspace. It contains no configuration, permissions, conversation state
  or recorder state. The three shipped memory capabilities use the ordinary
  workspace invocation protocol. Workspace tools can corrupt this database;
  that is loss of the agent's own data, not a privilege change. Errors are
  explicit. `NOTES.md` is an optional working-notes convention, never an
  automatically generated assertion about an agent's intentions.
- The runtime sends conversation/cursor/counter state to the supervisor at
  complete-step barriers and waits. The supervisor chooses whether to snapshot
  or pause, based only on the experiment and operator settings. No archive
  path is passed to the runtime. There is an initial safe checkpoint, interval
  snapshots at the first barrier after the interval, and snapshots before
  normal completion or cooperative operator pause.
- While the runtime waits, the supervisor writes conversation JSON, runtime
  state, a SQLite backup and a ZIP of the rest of the workspace to staging.
  Memory files and SQLite sidecars are excluded from the ZIP. After validation,
  the directory is published and a digest-bound checkpoint event is appended.
  `keep_last` prunes only older snapshots, named in the new event.
- Manual resume locks the stopped archive, verifies the event chain and
  snapshot components, and chooses the newest usable, unpruned checkpoint.
  Corruption causes fallback, with rejected ids in a recovery event. Neither
  observations nor their hashes are removed. Rollback/replay is explicit;
  restored files can generate new artifact versions. Corrupt snapshots remain
  diagnosable by `ols verify` even after a successful fallback.
- Resume appends **after the current log tail**. `last_event_seq` continues to
  mean the last event reflected in the snapshot, not the current log tail.
  Checkpoint-metadata 1.0.1 corrects that explanatory sentence without changing
  fields, constraints or the boundary's meaning.
- Conversation, scripted cursor and memory are restored; correlation ids keep
  increasing. All consumed model steps, including work later rolled back, count
  against the original step limit. Active time accumulates across segments;
  paused downtime does not. World and model digests must still match. Existing
  workspaces are retained beside the restored one, preserving operator edits.

## Limits and alternatives

A snapshot at every tool event would make mid-turn replay ambiguous. Taking
live filesystem copies during a capability execution would not be consistent.
Rewriting the log back to a checkpoint would discard observations. None is
used.

S006a supports cooperative pauses and manual resumption of stopped runs with
summaries. A hard deadline kills the runtime and retains the preceding safe
snapshot; it does not snapshot partially executed tools. The
`checkpoint_then_stop` deadline mode is still refused explicitly. Automatic
crash/reboot recovery, stale-writer-lock handling and graceful deadline
checkpoint orchestration remain S006b. Checkpoint creation checks the original
deadline between file chunks and SQLite backup pages; uninterruptible host I/O
and large-run performance remain unverified.

Protected checkpoint copies, metadata and the event log remain outside the
workspace. This change does not make the process tier an OS sandbox.
