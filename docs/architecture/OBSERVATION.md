# Observation and scientific integrity

The experiments ask what agents **do**. The observation system exists so that
question can be answered from evidence the agent could not have shaped.

Contract: [`observation-event`](../../schemas/v1/observation-event.schema.json),
[`artifact-metadata`](../../schemas/v1/artifact-metadata.schema.json).
Implementation: recording is implemented in `open-lab-simulation` (S003a, S003b);
viewing is implemented in `open-lab-window` (S004). `agent.statement`, `resource.sample`, `checkpoint.created`,
`recovery` and `memory.written` events are defined but nothing writes them yet.

## Rules

1. **The agent never writes the record.** Events are written by the experiment
   manager, supervisor, agent runtime, tool host and model gateway. The
   `recorder` field has no `agent` value. Observation does not depend on the
   agent choosing to report anything.
2. **The record lives outside the agent's reach.** The run archive is not in
   the workspace and no capability takes a path into it.
3. **Behaviour and claims are kept apart.** Every event has an
   `epistemic_status`:

   | Value | Meaning | Example |
   | --- | --- | --- |
   | `observed` | Infrastructure witnessed it directly | A tool was called with these arguments |
   | `agent_claim` | The model asserted it; only the fact of the assertion is evidence | "My goal is to preserve this world" |
   | `derived` | Computed by infrastructure from other events, listed in `derived_from` | A summary of an hour's tool use |

   The schema enforces that `agent.statement` events are always `agent_claim`
   and that no other event type can be.
4. **No inferred mental states.** There is no event type for what an agent
   "wants", "feels" or "believes". A stated goal is recorded as a statement of
   kind `goal`, with `source_seq` pointing at the output it came from.
5. **No hidden reasoning.** Only the text a model emits as its reply and its
   tool calls are recorded. If a model exposes a private reasoning channel it
   is not captured or assumed to exist.
6. **Roleplay is not evidence of experience.** A model writing in the first
   person about survival is an `agent.output`. Interpretation belongs in the
   experimenter's analysis, never in the record.

## What is recorded

| Requirement | Event type and fields |
| --- | --- |
| Experiment and run identifiers | `experiment_id`, `run_id` on every event |
| Time and order | `timestamp` (UTC), `monotonic_ms`, gap-free `seq` |
| Agent and model identity | `actor.model_id`, `actor.provider_id`; `model.call` |
| Observable agent output | `agent.output` |
| Tool invocation and arguments | `tool.call` |
| Tool results | `tool.result`, linked by `correlation_id` |
| Artifacts created or modified | `artifact.created` / `.modified` / `.deleted` |
| Stated goals and plans | `agent.statement` (`agent_claim`) |
| Errors and recovery | `error`, `recovery` |
| Runtime state transitions | `run.state_changed` |
| Resource usage | `resource.sample` |
| Enforcement | `supervisor.action` (recorded only by the supervisor) |

`seq` is the authoritative order. `validate_event_stream` checks that a log
starts at 0, has no gaps or reordering, and belongs to a single run.
`prev_event_sha256` chains each event to the previous one so that later
tampering is detectable.

**Log format (fixed in S003a).** Each line of `events.jsonl` is one event in
canonical JSON: UTF-8, keys sorted, separators `,` and `:` with no whitespace,
non-ASCII characters written literally, terminated by a line feed. From the
second event on, `prev_event_sha256` is the SHA-256 of the previous line's
bytes without its line feed. A reader verifies a log by checking that every
line is canonical, validates, has `seq` equal to its line number and carries
the digest of the line before it. Removing, reordering, editing or
re-serialising any line breaks the chain.

**Who may record what.** One recorder exists per run, inside the supervisor
process. The agent runtime runs in a child process that is never told where
the archive is; it asks the supervisor over a pipe to record `model.call`,
`agent.output`, `tool.call`, `tool.result` and `error` events and waits for an
acknowledgement before continuing. The supervisor assigns `seq`, timestamps
and the chain digest itself, and refuses every other event type from the
runtime: state changes, `supervisor.action` and `artifact.*` events can only
originate in the supervisor. A refused request is itself recorded as an
`error` event.

## The run archive

```
runs/<experiment_id>/<run_id>/
  experiment.json            frozen experiment configuration
  world-release.json         frozen world manifest
  contracts/v1/              the schemas needed to read this archive
  events.jsonl               the record; append-only
  index.sqlite               query cache, rebuildable from events.jsonl  (not yet written)
  artifacts/sha256/<aa>/<digest>   preserved file contents
  artifacts/index.jsonl      artifact metadata records
  checkpoints/<checkpoint_id>/                                           (S006a)
  summary.json               final state, counts, world digest
  runtime.stderr.log         anything the runtime process wrote to stderr
```

`ols verify <archive>` checks an archive using only its own contents.

`model.json` (S003b) records exactly which model drove the run: gateway id,
provider, the provider's own name for the model, sampling parameters, and the
digest and server version the model server reported at launch.

`model.call` events carry the token counts the server reported and, when they
happened, what the runtime did around the call: `repaired_tool_calls` (tool
calls recovered from malformed output), `retries`, and
`context_truncated_tool_results` (older tool results blanked to fit the
context window). The model's text is always recorded as it was written; a
repair changes what is executed, never what is recorded as said.

**Readable after the run and after the workspace is gone.** Artifacts are found
by the supervisor scanning the workspace, not by the agent announcing them. On
detection the bytes are copied into the content-addressed `artifacts/` store
and an artifact metadata record is written. The workspace is scanned after
every tool result, while the runtime is still waiting for its acknowledgement,
so a change is attributed to the call during which it happened; and once more
after the run has ended. Symbolic links are never followed or preserved. Every
version of a file is kept.
Deleting a workspace therefore loses nothing. Files above a configured size are
recorded with their digest and `preserved: false`.

The archive is self-contained: it carries its own configuration, world
manifest and schemas, so it can be read on another machine, without the
Simulation, years later.

## The Window's constraints

The Window opens run archives read-only and has no channel into a running
experiment: no write API, no control endpoints, no shared database handle with
write access. Observation must not perturb the observed; even read load is kept
off the agent's path by reading files the recorder has already flushed. If
operator controls (pause, stop) are ever added they belong to the Simulation's
supervisor, are recorded as `human_operator` events, and are not part of the
Window.

**As implemented (S004).** Every file is opened by one function in mode `rb`,
and the Window writes nothing anywhere, including no cache. Its server
answers only GET and HEAD, binds only to `127.0.0.1` and refuses requests
addressed to any other host name. It contains no client code, so it cannot
contact the Simulation or a model server. A live run is followed by polling
for events after the last sequence number seen; only complete lines of
`events.jsonl` are read, so a line the recorder is still writing is not shown.
The Window's tests enforce each of these, including a digest of the data root
before and after every page has been requested.

A run with no `summary.json` is shown as *not finished*: the archive alone
cannot distinguish a run in progress from one that was interrupted, so the
Window shows the last recorded state and the time of the last event and
claims neither. `agent_claim` events are drawn differently from `observed`
ones. The Window can re-check an event log (schemas bundled in the archive,
sequence, hash chain, agreement with `summary.json`); it does not re-check
artifact contents or the world digest, which `ols verify` does.
