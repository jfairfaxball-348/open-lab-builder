# Observation and scientific integrity

The experiments ask what agents **do**. The observation system exists so that
question can be answered from evidence the agent could not have shaped.

Contract: [`observation-event`](../../schemas/v1/observation-event.schema.json),
[`artifact-metadata`](../../schemas/v1/artifact-metadata.schema.json).
Implementation: recording is implemented in `open-lab-simulation` (S003a, S003b);
viewing is implemented in `open-lab-window` (S004). S006a records checkpoint,
manual recovery and memory-write events. S006d adds bounded automatic
recovery, startup recovery and model-health supervisor actions. S006e writes
periodic `resource.sample` and resource installation/enforcement/denial actions.
`agent.statement` remains defined but is not written yet.

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
| What the infrastructure said to the agent | `environment.message` (S003c) |
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
`agent.output`, `environment.message`, `tool.call`, `tool.result` and `error`
events and waits for an acknowledgement (which carries the event's `seq`)
before continuing. The supervisor assigns `seq`, timestamps
and the chain digest itself, and refuses every other event type from the
runtime: state changes, `supervisor.action` and `artifact.*` events can only
originate in the supervisor. A refused request is itself recorded as an
`error` event.

**Everything the agent is told is in the record.** The initial prompt is in
the frozen `experiment.json`. Anything the infrastructure adds to the
conversation afterwards is an `environment.message` event recorded before the
model sees it, with the text verbatim. S003c introduced the *continuation*:
when the model replies without calling a tool, the run
does not end; the runtime answers with the experiment's `continuation.message`
(or the default stated in the experiment-config schema) and asks the model
again (decision OD-5). The event's `after_seq` names the output it answers. A
run therefore ends only at its step limit, its deadline or a failure.

S005b also records an `environment.message` of kind `preamble` before the first
model call (observation-event 1.2.0). This text becomes a system turn immediately
before the unchanged initial user prompt. It describes only the four fixed
discovery interfaces and grants no permissions. The same text is recorded for
scripted runs. A world whose contracts cannot record it is refused at launch.

**S007c policy/input records.** New runs archive `policy.json`, bound to the
launch event and experiment digest. Legacy continuation remains the default;
the selectable quiet policy idles after its reply threshold with no further
model input or automatic wake. Supervisor `runtime_idle` actions record the
counter/latch and whether this segment restored it. Recovery events freeze the
policy and checkpoint progress. These observations do not interpret prose as
intent or inactivity as failure.

Before each HTTP attempt, a dedicated IPC request has the supervisor sync an
exact `model_input` snapshot in a `limit_enforced` action. It contains messages,
tools, requested settings, context before/after digests, changes and overflow.
The worker waits for acknowledgement before HTTP. Retries have separate attempt
records, even when no reply follows. Scripted snapshots identify their ignored
conversation input. No hidden reasoning response is recorded. These records
permit exact input reconstruction for new runs; historical archives do not gain
retroactive inputs. Storage and fsync overhead for long runs remain unverified.

**Context.** When the conversation outgrows the model's context window, the
runtime first blanks the oldest long tool results, then drops the oldest whole
turns, preserving the system preamble, the initial prompt and the latest
assistant/tool group. Fresh documentation reaches the model at least once.
If this protected content alone exceeds the conservative estimate, it is sent
intact; the guard cannot guarantee the server's tokenisation. Each `model.call`
records `context_truncated_tool_results` and `context_dropped_messages` when
this happened, so what the model could see at every step can be
reconstructed.

## Resource measurements (S006e)

Only the supervisor writes resource samples. They can interleave with
conversation/tool events; `seq` and explicit correlation/after_seq references
remain authoritative. Default cadence is one second plus initial/final samples;
`extensions.resource_sampling.interval_s` can select 0.05–60 seconds.
CPU is job active time, 100 percent per logical core. RAM is summed private
commit of verified job members; process count is job accounting; workspace disk
is logical file bytes. Host NVIDIA VRAM used/available is optional, sampled
asynchronously through existing nvidia-smi, with scope and age in extensions.
These are best-effort measurements, not atomic whole-host snapshots. A first
CPU sample or failed/racing memory query can be unavailable. Missing numbers
are omitted and listed in `payload.extensions.unavailable`; zero remains zero.

Actions with stage `resource_limit_installed` record the applied policy. Stage
`resource_limit` records quota denials, observed breaches or monitoring failure.
CPU hard caps throttle cycles in the OS; a sample is not treated as proof of a
breach. Windows memory/process notifications are best effort; absence is not
proof that no allocation/process was denied. Disk admission precedes execution;
a denied writing tool has both a supervisor action and a denied tool result.
No model output is used as authority or as evidence that a limit was enforced.
See ADR-0012 for scope and polling limitations.

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
  segments/<event-count>.json   prior stopped-segment summaries (S006a)
  summary.json               final state, counts, world digest
  runtime.stderr.log         anything the runtime process wrote to stderr
```

`ols verify <archive>` checks an archive using only its own contents.

S006a adds verified complete-step checkpoints and manual resume. The event log
is opened for append only after canonical form, identities, sequence and hash
chain have been checked. A new recovery event states which snapshot was used
and which were rejected. Restored state can precede existing observations;
those observations are retained, and any replay produces new events. Artifact
history is reconstructed before scanning the restored workspace. Paused time
is excluded from active elapsed time and the event clock. The same initial
conversation is restored without recording a second preamble.

Only the supervisor writes `checkpoint.created`, `recovery` and `memory.written`.
The worker's state-barrier messages cannot choose paths, retention, budgets or
permissions. Normal completion and operator pause get a safe checkpoint before
shutdown; hard deadline termination keeps the preceding checkpoint. Retained
corrupt snapshots remain visible to verification even when recovery succeeds.

S006b records the nominal deadline request as `supervisor.action` with action
`limit_enforced` and extension stage `deadline_checkpoint_requested`. It records
termination after saving a complete-step snapshot or exhausting the fixed grace
allowance. Both are supervisor observations. No deadline notice is delivered
to the model. The worker remains blocked until killed; queued barriers after
termination never cause a snapshot. See ADR-0010.

S006d adds supervisor actions whose extension stages distinguish restart debits,
model-attempt reservations, model health, exhaustion and refusal. Model attempts
are reserved and synced before execution; a killed attempt can therefore have a
reservation without a completed `model.call`. Health records report only server
availability/model identity, not inferred agent state or inference readiness.
Recovery state transitions and checkpoint ids preserve the existing hash chain.
Refusal actions can follow a final state. A live/unverifiable owner or invalid
log receives no appended event because it cannot safely accept one. Startup
recovery never trims partial lines; missing summaries remain missing on refusal.
Host-local writer markers/accounting and retained stale-owner evidence are
operational files outside the workspace, never authority from an agent.
See ADR-0011.

`isolation.json` (S006c) records the isolation every capability call had:
`{"tier": "process"}`, or for the container tier the engine and version,
rootless/cgroup/runtime facts, image reference and id, and applied limits.
Resumed segments add `segments/isolation-<seq>.json`. See ADR-0015.

`model.json` (S003b) records exactly which model drove the run: gateway id,
provider, the provider's own name for the model, sampling parameters, and the
digest and server version the model server reported at launch.

`model.call` events carry the token counts the server reported and, when they
happened, what the runtime did around the call: `repaired_tool_calls` (tool
calls recovered from malformed output), `retries`, and
`context_truncated_tool_results` (older tool results blanked to fit the
context window). The model's text is always recorded as it was written; a
repair changes what is executed, never what is recorded as said.

S005b additionally repairs syntactic invocation argument wrappers: an encoded
JSON input object can be decoded, and an exact extra `arguments` envelope
containing both `id` and `arguments` can be removed. No id or input field is
invented, and the repaired call still passes the same schema and permission
checks. `model.call.repaired_tool_calls` counts the affected calls, while the
original assistant tool arguments remain verbatim in the conversation. Since
S005b, `agent.output.payload.extensions.raw_tool_calls` also stores the emitted
names and argument strings held by the client, so repairs are auditable even
when the model used the structured tool channel and emitted no reply text.
For a textual fallback, the original reply text and extracted argument object
are preserved. Reasoning fields remain ignored.

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
