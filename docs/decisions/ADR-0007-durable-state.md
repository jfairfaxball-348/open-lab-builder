# ADR-0007: Append-only JSONL as the record, SQLite for indexes and memory

Status: Accepted (S001). Implemented in S003a and S006a.

## Context

A run needs a permanent, tamper-resistant record; fast queries for the Window;
durable agent memory; and checkpoints that allow exact resumption after a
crash, possibly days into an experiment.

## Decision

- **The event log is the source of truth**: one JSON object per line in
  `events.jsonl`, appended and flushed by a single recorder process, never
  rewritten. Sequence numbers are gap-free; events may be hash-chained.
- **SQLite is a derived index** beside the log (`index.sqlite`), rebuildable
  from the log at any time. The Window queries it read-only.
- **Agent memory is a per-run SQLite database** in the supervisor's area,
  reached by the agent only through memory capabilities.
- **Artifacts are stored content-addressed** by SHA-256 in the run archive.
- **Checkpoints** are directories holding the conversation state, a consistent
  copy of the memory database and a workspace snapshot, indexed by a checkpoint
  metadata record that names the last event sequence it reflects.
- SQLite is the standard-library `sqlite3` (3.49 on the development machine),
  in WAL mode for the index.

## Alternatives

- **SQLite as the only store.** Simpler querying, but a binary file is harder
  to inspect, diff, hash-chain and recover after corruption than a text log,
  and a single writer bug could rewrite history.
- **Event log only.** The Window would have to scan gigabytes for multi-day
  runs.
- **Postgres or another server database.** Operational weight with no benefit
  for single-machine, single-writer runs.
- **Vector database for memory.** Possibly useful later; an embedding index can
  be added to the memory capability without changing this decision.

## Consequences

- Two representations must be kept consistent; the rule is that the index is
  disposable and the log wins.
- One recorder process serialises writes from several components, so it is a
  single point of failure. That is intended: if recording stops, the run stops.
- Multi-day runs produce large logs; rotation into numbered segments is a
  compatible later extension.
