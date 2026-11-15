# Interface contracts

The contracts are the only interface between the Builder, the Simulation and
the Window. They are JSON Schema (draft 2020-12) files in
[`schemas/v1/`](../../schemas/v1). Why JSON Schema:
[ADR-0002](../decisions/ADR-0002-contracts.md).

| Contract | `schema` value | Written by | Read by |
| --- | --- | --- | --- |
| World release manifest | `open-lab/world-release` | Builder | Simulation, Window |
| Capability manifest | `open-lab/capability` | Builder; later the agent, inside its sandbox | Simulation (tool host, registry), agent, Window |
| Model provider manifest | `open-lab/model-provider` | Builder | Simulation (model gateway) |
| Experiment configuration | `open-lab/experiment-config` | Experimenter | Simulation, Window |
| Observation event | `open-lab/observation-event` | Simulation infrastructure | Window |
| Artifact metadata | `open-lab/artifact-metadata` | Simulation infrastructure | Window |
| Checkpoint metadata | `open-lab/checkpoint-metadata` | Simulation supervisor | Simulation (recovery), Window |

`common.schema.json` holds shared definitions (identifiers, timestamps,
digests, safe relative paths, permissions, resource limits).
`development-state.schema.json` describes this project's own
`docs/roadmap/state.json` and is not part of the runtime interface.

Field-level documentation lives in the schemas themselves: every field has a
`description`, and each schema's `required` list is the definition of what is
mandatory. Valid examples are in [`examples/v1/`](../../examples).

## Conventions

- Every document carries `schema` (which contract) and `schema_version` (which
  version of it the document was written against).
- Identifiers are lower-case slugs. Timestamps are UTC with a `Z` suffix.
- Paths are forward-slash and relative to a stated root. Absolute paths, drive
  letters, backslashes and `..` are rejected by the schema, so a document can
  never point outside its root.
- Top-level objects are closed (`additionalProperties: false`): a misspelt
  field is an error, not silently ignored.
- Every contract has an open `extensions` object for experimental data.

## Versioning and compatibility

Each schema declares its full version in `x-schema-version` and lives in a
directory named for its major version.

| Change | Version bump | Rule |
| --- | --- | --- |
| Clarify a description, loosen nothing | Patch | Any 1.x reader accepts it |
| Add an optional field or a new enum value | Minor | Old documents stay valid under the new schema |
| Remove or rename a field, tighten a constraint, change meaning | Major | New directory `schemas/v2/`; `v1` is kept |

Rules for readers:

1. A reader accepts a document whose major version it has schemas for and whose
   minor version is not newer than its own schema. A newer minor is refused
   rather than mis-read (`validate_document` enforces this).
2. A **world release bundles the exact schemas it was built with**, and its
   manifest lists them under `contracts`. The Simulation validates a world's
   documents against the bundled schemas, so Builder and Simulation can never
   disagree about a release.
3. **Run archives are permanent.** The Window must keep every major version's
   schemas so that old runs stay readable. A v1 schema directory is never
   deleted or edited incompatibly.
4. New fields are trialled under `extensions` and promoted with a minor bump.

Changing a schema requires: bumping `x-schema-version`, updating the examples,
adding or adjusting tests, and noting the change in this document's log below.

## Notes on individual contracts

### World release

Immutable once `status` is `validated` or `released`; those states require a
`content_digest`. `draft` releases must not be used for recorded experiments.

Implemented in S002 by `olb world build` and `olb world verify`
(`src/open_lab_builder/worlds/`). What follows is the specification the
Simulation must reproduce without importing that code.

**Layout.** A release is the directory `<world_id>/<version>/`:

```
world-release.json                       the manifest
contracts/v1/<name>.schema.json          the seven contracts and common.schema.json
capabilities/<id>/capability.json        one directory per capability, named by its id
capabilities/<id>/...                    that capability's implementation files
models/<file>.json                       model provider manifests
registry/index.json                     generated discovery index (since S005a)
registry/docs/<id>.txt                   generated complete manifest documentation
```

Source files are copied byte for byte from the world source (`worlds/<name>/` in this
repository). Nothing is rewritten: no line-ending conversion, no
re-serialisation. The repository stores text with LF endings
(`.gitattributes`), so a build is the same on Windows and Linux. Bytecode
caches (`__pycache__`, `*.pyc`) are never copied, and symbolic links are
refused.

**Registry (S005a).** Generated files join the digest before self-tests and are
not source files. `registry/index.json` has `format_version: "1.0.0"` and a
`capabilities` array sorted by id. Each entry has `id`, `name`, `summary`,
`categories`, `keywords` (empty if absent), `documentation_path` and `tokens`.
Tokens are stored separately for id, name, keywords, categories, summary and
description: case-fold Unicode text, split into alphanumeric words (underscore
and punctuation separate words), deduplicate and sort. No stemming or stop-word
removal. JSON uses sorted keys, two-space indentation, literal Unicode, UTF-8
and a final LF. Documentation includes a heading and every manifest field in
sorted order; strings are prose, other values are sorted, indented JSON. The
generated separators use LF; string values retain their original content.

The Builder's pure-Python `capabilities.registry.search(index, query,
category=None, limit=10)` uses the same tokenizer and sums weights for each
distinct query token present in each field: id 8, name 6, keywords 5, categories
4, summary 3, description 1. Any positive match is eligible; descending score,
then ascending id determines order. An optional exact category slug filters
results. Empty/no-match queries and non-positive limits yield an empty list.
Results carry the entry and its score. An unsupported format version is refused.
This is derived release data, not a new JSON Schema contract; existing schemas
were unchanged by S005a. Runtime discovery integration is implemented in S005b. Older releases
without the registry remain verifiable.

**Discovery protocol (S005b).** The Simulation independently reads and checks
this index; it imports no Builder code. A run requires complete format 1.0.0
discovery data and preamble support in observation-event 1.2.0. Older worlds
remain verifiable, but this runtime refuses to launch them. Exactly four tools
are offered, with names mapped to chat API function names by replacing dots
with underscores:

- `capabilities.search(query, category?)`: up to ten ranked summaries with
  id, categories and score; filters out unavailable/ungranted capabilities.
- `capabilities.describe(id)`: full generated documentation, structured input
  schema, and an `example_call` derived from the first demonstration's input.
- `capabilities.demonstrate(id, demo_id?)`: executes the named demonstration,
  or the first in manifest order, in the actual run workspace. Returns id,
  demo id, input, real execution `outcome`, and expected output/comparison if
  present. An execution failure is kept in the nested outcome; it is never
  replaced with the expected output. Demonstrations may create artifacts.
- `capabilities.invoke(id, arguments)`: validates and executes the capability
  and returns its actual outcome.

Meta-tool argument objects are closed. Describe, demonstrate and invoke enforce
the experiment's allow/deny lists and permissions; demonstration inputs grant
nothing. Direct capability names and recursive meta-invocation are refused.
Each meta-call produces a correlated `tool.call`/`tool.result` pair naming the
meta-tool, with the target id in its arguments. Invocation/demonstration
execution does not emit a second nested pair. Workspace scans occur after that
result; artifact producer metadata names the target capability and correlates
to the recorded meta-call. Schemas for these four built-in interfaces live in
the Simulation; world capability schemas remain in their manifests.

**Content digest.** `content_digest.value` is computed as follows.

1. Take every file in the release except `world-release.json`. Its path is
   relative to the release directory, with forward slashes.
2. For each, form the line `<sha256 of the file's bytes, lower-case hex>`,
   two spaces, `<path>`, a line feed.
3. Sort the lines by the UTF-8 bytes of the path.
4. Take the manifest as a JSON object, remove the keys `created_at`, `builder`
   and `content_digest`, and serialise it as UTF-8 JSON with keys sorted, no
   whitespace (separators `,` and `:`) and non-ASCII characters written
   literally (Python: `json.dumps(obj, sort_keys=True, separators=(",", ":"),
   ensure_ascii=False)`). Append the line `<sha256 of that text>`, two spaces,
   `world-release.json`, a line feed.
5. The digest is the SHA-256 of all the lines concatenated, encoded as UTF-8.

So the digest covers every bundled byte and every manifest field that
describes the world, including default permissions and limits. It does not
cover when or by which Builder version the release was made: building the same
source twice gives the same digest. `builder.git_commit` is recorded only when
the Builder checkout had no uncommitted changes.

`extensions.files` lists each bundled file with its SHA-256. It is
informational (it lets `olb world verify` name the file that changed); the
content digest is what binds the release, and it covers that list too.

**Verification** (`olb world verify <release-dir> [--self-test]`): the
manifest validates against the *bundled* contracts; the bundled schema versions
equal the manifest's `contracts` map; the set of files and each digest match;
the content digest matches; every capability and model manifest validates and
is the one its entry names. `--self-test` re-runs the demonstrations.

**Immutability.** `olb world build` never overwrites a release. Rebuilding
identical content into the same place is a no-op; different content under an
existing version is an error, and the fix is a new version.

**Data root.** The shared data directory is `$OPEN_LAB_DATA` when that
variable is set, otherwise `open-lab-data` in the user's home directory, on
every platform. `olb world build` writes to `releases/` in the checkout by
default (ignored by Git); `--publish` writes to `<data root>/worlds/`, which is
where the Simulation looks.

### Capability

The most important contract: it is what lets an agent pick up a tool it has
never seen. Beyond structure, `olb validate` checks the manifest against
itself:

- `input_schema` and `output_schema` are themselves valid JSON Schemas.
- Every demonstration's `input` satisfies `input_schema`.
- Every `expected_output` satisfies `output_schema`.
- Deterministic demonstrations state their expected output.
- `self_test` refers only to demonstrations that exist.

`invocation.interface` is one of `python`, `subprocess`, `http` or `mcp`. The
arguments and results are JSON objects in all four, which is what makes the
manifest transport-neutral ([ADR-0003](../decisions/ADR-0003-capability-manifest.md)).

**Invocation protocol** (fixed in S002; `python` and `subprocess` are
implemented, `http` and `mcp` are not):

- A capability is self-contained in its own directory. A host runs it with
  that directory as the working directory.
- The host validates the arguments against `input_schema` *before* running
  anything, and the result against `output_schema` afterwards.
- `subprocess`: the command is an argument vector, never a shell string. A
  first element of exactly `python` means the host's own interpreter. The
  argument object arrives as UTF-8 JSON on stdin. Exit status 0 with the result
  object as JSON on stdout is success. A non-zero status with
  `{"error": "<message>"}` on stdout is the capability declining the request.
- `python`: `entrypoint` is `module:function`, where the module is a file in
  the capability directory (dots are sub-directories), not something on the
  import path. The function takes the argument object and returns the result
  object; raising `ValueError` declines the request. The Builder runs the
  function in a child process, so it has the same timeout as a subprocess.
- The timeout is `resources.timeout_s` (30 s if absent).
- **Workspace.** A capability whose manifest declares `permissions.filesystem`
  other than `none` is given the absolute path of the run's workspace in the
  environment variable `OPEN_LAB_WORKSPACE`. That is the only location it is
  told about. A capability without that permission does not get the variable.
  (The Builder's self-test invoker does not set it; no shipped capability
  uses the workspace yet.)
- **Environment.** The Simulation starts capability processes with an almost
  empty environment — only what an interpreter needs to start — so nothing in
  the operator's environment (tokens, keys, user paths) is inherited.
- **Authority.** Before running, the Simulation's tool host compares the
  manifest's `permissions` with the experiment's. If the capability needs more
  than the experiment grants, or the experiment's `capabilities.allow` / `deny`
  excludes it, the call is recorded with status `denied` and nothing runs.

Every invocation ends in one of these outcomes:

| Outcome | Meaning |
| --- | --- |
| `ok` | A result that satisfies `output_schema` |
| `invalid_input` | Arguments rejected; no capability code ran |
| `capability_error` | The capability declined, with a message (e.g. `division by zero`) |
| `execution_error` | It crashed, could not start, or exited non-zero without a message |
| `timeout` | No result in time; the process was killed |
| `invalid_output` | It returned something that is not JSON or violates `output_schema` |
| `unsupported_interface` | The host cannot run this interface |

In a run, the outcome is recorded in the `tool.result` event: `ok` and
`timeout` map to the same `status`; `denied` is described above; every other
outcome is `status: error` with `error` set to `<outcome>: <message>`, for
example `capability_error: division by zero`.

The Builder's invoker (`src/open_lab_builder/capabilities/`) exists only to run
self-tests at build time. It gives no isolation beyond a child process and a
timeout. The Simulation's tool host (`open-lab-simulation`, S003a) is a
separate implementation of the same protocol.

Since S005a, each build-time self-test demonstration receives its own empty,
disposable workspace. The Builder strips inherited `OPEN_LAB_WORKSPACE` and
sets it only for filesystem capabilities. The release directory stays unchanged.
`workspace.write` creates bounded UTF-8 text files (explicit overwrite only);
`workspace.list` lists at most 1000 immediate children. Both validate relative
paths, reject traversal, special names and links, and report errors without
local paths. These checks do not contain concurrent path replacement or
arbitrary capability code on the process tier; the container tier (S006c, ADR-0015)
confines capability processes on Windows hosts.

### Model provider

Separates the gateway-facing model `id` from the provider's own name
(`provider_ref`), so an experiment can name `orchestrator-small` and the world
decides what serves it. `footprint.measured` distinguishes estimates from
measurements on the target machine; `status` distinguishes validated models
from ones that are merely present or not downloaded at all.

S007a implements an optional local catalog via the existing experiment extension
`extensions.model_catalog = {"document": <model-provider>, "sha256": <hex>}`.
It replaces bundled provider lookup for that experiment. The document uses the
world's bundled model-provider schema, with unique gateway model ids. Builder
owns catalog definitions (`models/local-engineering.json`); the experiment embeds
an approved snapshot outside agent control. The pin hashes canonical JSON:
sorted keys, compact separators, literal Unicode, UTF-8, no final newline.
Changing the catalog requires a new digest/configuration; existing archives are
never updated. This is an experimental protocol using existing extension points;
no schema structure/version changes are required.

Only local Ollama or loopback chat-compatible providers are supported. Selected
models require available status, orchestrator role and explicit model/network
permissions. Supplied model digests must match server identity. Generic `/models`
only proves the advertised id; weight digest, server version and offload remain
unknown. Generic checkpoint resume is refused without an attestable digest.
HTTP redirects and URL credentials are refused. No external access is enabled.

The archive freezes canonical `model-catalog.json`, the complete selected
provider/model manifests and adapter/settings in `model.json`. The launch
`run.state_changed` payload's extensions carry stage `model_provenance` and
`model_sha256`, hashing canonical model.json. Archive verification checks this
binding and catalog/config consistency. Resume revalidates configuration and
identity; new-format archives require the original complete provenance. Legacy
archives retain their original digest-based checks. Requested sampling and the
client context guard are distinguished from unknown effective server settings.
Repair policy `syntactic-tool-repair-v1` names the existing parsing/unwrap/name
repairs; maximum HTTP attempts remain two. Unspecified output caps now explicitly
request 512 tokens. Neither request caps nor seeds establish enforced compute
parity or deterministic results.

### Experiment configuration

S007e reserves the existing MCP invocation pair `supervisor-gateway` /
`models.ask` for a supervisor service (ADR-0018), not an arbitrary network
MCP server. Its manifest accepts only `{prompt: string}` (1-6000 characters)
and returns `{text: string}` (at most 6000 characters). The Builder self-test
injects a labelled fake transport; ordinary build-time invocation without
that transport refuses the service. No real model runs in a build.

`extensions.specialist` is a closed object requiring `model_id: specialist-text`
and integer fields: `max_calls` 1-32, `max_prompt_chars` and `max_output_chars`
1-6000, `max_output_tokens` 1-1024, `timeout_s` 1-120, `lease_s` 1-600. Absence
disables consultation. The bundled approved digest-pinned Ollama model is
llama3.2:3b; this milestone permits a hosted or scripted orchestrator only.
The worker's `{specialist: arguments}` IPC request must match one outstanding
permitted invocation/demonstration. The supervisor repeats admission checks,
syncs a `specialist_call_reserved` observation, and acknowledges with
`specialist_result` only after the gateway returns. Calls count across resume;
residency never does. An HTTP thread has no recorder and the supervisor polls
its observations while retaining deadline/resource authority.

Supervisor-action extensions record `specialist_configuration` (policy,
manifests, adapter and requested settings), `specialist_call_reserved`,
`specialist_lease_acquired`, `specialist_loaded`, `specialist_reply` (prompt,
text and reported usage), `specialist_failed`, `specialist_unloaded`,
`specialist_unload_failed`, `specialist_lease_released` and exceptional
`specialist_cleanup_pending`. Durations are milliseconds; the pinned model
digest accompanies lease observations. Replies are untrusted model-output
observations. No reasoning response channel is copied. An OS lock serializes
cooperating supervisors under one data root; other resident models cause a
refusal without unloading unrelated work. Native finite keep-alive bounds
residency after abrupt supervisor loss, not an immediate unload guarantee.

Holds everything needed to reproduce a launch: prompt, world and digest, model
and sampling parameters, limits, permissions, checkpointing and termination.
A premise in `initial_prompt` grants nothing; only `permissions` and `limits`
do. `research_question` is never shown to the agent.

S007c uses `extensions.runtime_policy` as a closed experimental configuration
object. Defaults resolve to `legacy-immediate-v1`; `quiet-until-deadline-v1`
adds a consecutive tool-free reply threshold, with no automatic wake. Exact
fields, bounds and semantics are specified in [Runtime policies](RUNTIME_POLICIES.md).
Unknown fields/versions/turn semantics are refused. Both policies preserve the
existing continuation field and actual tool permissions.

`policy.json` contains resolved defaults and the canonical experiment SHA-256.
The launch state event's payload extensions add `policy_sha256`. New model
provenance includes this policy. Checkpoint runtime-state JSON adds
`policy_state` (nonnegative tool-free counter, boolean idle latch) and
`policy_sha256`; existing component digests bind these bytes. New recovery events
carry the effective policy and digest, including legacy interpretation for old
archives. Old observations are never rewritten. Configuration or policy changes
refuse resume.

The worker's pre-request IPC message is `{"model_input": <payload>}`. The
supervisor records an action `limit_enforced`, stage `model_input`, with exact
`request`, `context`, `attempt`, `backend` and `policy_sha256` fields, and syncs
before acknowledging. HTTP is not sent without acknowledgement. Context details
include before/after message digests, budget, mutation counts and protected
content overflow. Scripted inputs identify their backend and mark the guard
unapplied. An idle barrier records stage `runtime_idle`, with counter/latch,
`wake: none` and restoration status. The worker can request observations but
cannot submit privileged event types. These protocols use existing extensions;
no schema or world version changed. Request snapshots contain inputs, never a
hidden reasoning response channel.

S007d adds experimental `extensions.benchmark` metadata (campaign/cell/role/
condition/rubric) and `extensions.benchmark_fault = {"id":
"first-permitted-execution-v1"}` for condition D only. Other fault shapes/ids
are refused. The trusted supervisor records a `limit_enforced` action with stage
`benchmark_fault`, target id, actual argument digest, correlation id and exact
marked synthetic outcome. Eligibility checks availability/permissions, input
schema and supported interface before interception; no capability code or side
effect has run. The worker cannot activate or replenish the fault via model
text. Recovery retains prior exposure accounting. Delivered tool results and
subsequent model-input exposure are analysed separately from the injection event.

The initial created-state event records an observed workspace entry listing,
its canonical digest and memory presence. Campaigns require the empty listing
and absent memory. Manifests pin every cell/configuration, prompts, role, balanced
order and LF-normalised Python source hashes. Campaign ledgers live outside
workspaces under the data root's campaigns/; they are serialized by the existing
verified OS writer lock, hash-chained and synced at cell starts/outcomes. Started
cells are reconciled without automatic replacement. Raw data remain unchanged;
derived annotations bind event-log hashes and use explicit epistemic labels.
The internal derived-results format is not a new shared JSON Schema contract.
Existing extension points suffice; world/schema versions are unchanged.

### Observation event, artifact metadata

See [OBSERVATION.md](OBSERVATION.md).

### Checkpoint metadata

`last_event_seq` ties a snapshot to an exact point in the event log, so a
resumed run continues the same sequence. `progress.elapsed_s` counts active
time only, so a crash does not eat into an experiment's time budget.

S006a implements the protocol in [ADR-0009](../decisions/ADR-0009-checkpoint-barriers-and-agent-memory.md).
Each checkpoint has `checkpoint.json`, `conversation.json`, `runtime_state.json`,
`memory.sqlite` and `workspace.zip`. Metadata lists the four components with
byte counts and SHA-256 digests. The runtime state holds the scripted cursor,
completed-step count, tool correlation counter, token count and whether a live
memory file existed. The conversation is in chat-completions message form.
SQLite backup produces a consistent memory copy; the ZIP excludes its live
database/sidecars and retains all other files and empty directories. Restore
rejects absolute paths, traversal, backslashes, drive syntax and duplicate names.

The supervisor publishes only complete, validated staging directories. Its
`checkpoint.created.payload.extensions` binds the metadata digest and names
older checkpoint ids pruned by `keep_last`. Metadata extensions bind the world
content digest and the hash of `last_event_seq`. The runtime sees neither
checkpoint paths nor recorder handles. It supplies state only at completed-step
barriers and waits for acknowledgement. Defaults, when `checkpointing` is
enabled, are interval 60 seconds and retention 3; checkpointing is otherwise off.
Interval snapshots occur at the first barrier at/after the interval, with an
initial snapshot and snapshots before normal completion/operator pause.

Resume takes the newest usable, unpruned checkpoint and appends after the
**current log tail**, not after the snapshot boundary. A recovery event records
the chosen id; its payload extensions record the snapshot event boundary,
rejected ids and accumulated active time. No event is removed. When fallback
rolls state back, later work may be replayed and restoration may produce new
artifact observations. Correlation ids, artifact ids/revisions and the hash
chain continue. All consumed model steps still count against the original
limit, including replayed work. Paused downtime is excluded from elapsed time;
the original budget is never replenished. The world/model digests must match.

Verification checks component hashes/sizes, metadata binding, snapshot identity,
SQLite integrity and ZIP integrity/paths. Corrupt snapshots remain forensic
evidence: resume can bypass them, but `ols verify` still reports their corruption.
Pruned snapshots are distinguished by the recorded pruning list. Prior segment
summaries are retained under `segments/`; the original stderr log is appended.
Former workspaces are retained beside the restored workspace so operator edits
are not discarded. A writer lock prevents concurrent supervisor segments.

`memory.write`, `memory.search` and `memory.list` use the ordinary filesystem
permission checks and a fixed `.memory.sqlite` path inside the workspace.
Writes upsert a key/value and increment its revision. Reads do not create a
missing database; search uses literal substring matching (SQLite ASCII lower),
listing is sorted by key, and results are bounded. These are agent notes, never
privileges. Successful writes produce a supervisor-authored `memory.written`
event with key/revision/call correlation in payload extensions. `NOTES.md` is
the optional free-form working-notes convention.

Hard deadline termination retains the earlier safe snapshot, not a snapshot
of a partially executed tool. S006b enables `checkpoint_then_stop` only with
checkpointing. At the original deadline the supervisor requests a stop at the
next complete-step barrier. `grace_period_s` (default zero) is one fixed extra
allowance for that step and snapshot; on success the tree is killed before
acknowledging the barrier, and on expiry the preceding safe snapshot is kept.
An interval snapshot crossing the nominal deadline can serve as the final safe
snapshot. Grace counts as active elapsed time and does not replenish the
original budget. Hard stop ignores grace. The deadline request is a
`supervisor.action: limit_enforced` with extension stage
`deadline_checkpoint_requested`; termination is also a supervisor action.
See ADR-0010. S006d extends resume to opted-in interrupted archives through
`ols recover`, using verified writer ownership and conserved retry budgets.
Stopped runs still use `ols resume`; see the extension below.

### Supervisor recovery extension (S006d)

The Simulation trials recovery under `experiment-config.extensions.recovery`,
using existing extension fields rather than changing a schema or world release.
The object requires integer `max_restarts` in 0–100. Optional `auto_resume` is a
boolean (default false). Optional `health_check_interval_s` and
`health_check_timeout_s` are finite numbers in 0.05–60 (defaults 5 and 2).
Unknown fields, boolean numbers and recovery without checkpointing are refused.
Absence disables automatic recovery.

Hosted runs (S011r, [ADR-0021](../decisions/ADR-0021-hosted-recovery-identity.md))
accept recovery only with `hosted_identity: "provider-model-version-v1"`; local
runs refuse that field. The broker pins the first accepted provider-reported
`model_version` and withholds any reply reporting another (terminal
`provider_identity_changed`). Hosted automatic recovery follows only an
unexpected runtime exit; a resume is refused after any provider stop or with a
changed model record or broker profile. Resumed hosted segments record stage
`hosted_identity_pin`. No schema or world release changes.

`supervisor.action.payload.extensions.stage` names `recovery_restart`,
`model_step_reserved`, `model_health`, `recovery_exhausted`, `recovery_refused`
and `manual_resume`. Restart actions debit one shared retry budget before a
worker starts; reserved model attempts are charged even without a reply.
Actions may follow a final state when recording recovery refusal/exhaustion;
verification checks the final state transition and the full event count.

`.writer.guard` is a permanent OS-locked inode, `.writer.lock` a host-local owner
marker, and `.supervisor.json` a supervisor-only active-time reservation ledger.
They are operational state, not agent input or new cross-repository schemas.
Owner identity combines a hashed installation identity with PID and OS process
birth identity. Only a confirmed dead/reused local owner can be replaced under
the exclusive guard; its marker is kept under `segments/`. Legacy/unknown/live
ownership is refused. The runtime must also be absent before startup recovery.

Startup scans require `auto_resume: true`, a missing summary, a non-stopped
state in a complete valid log, valid accounting, matching world/model identity
and a valid checkpoint. Existing observations are never rewritten or truncated.
Unsafe ownership/invalid logs yield CLI refusals; safe owned logs also receive
refusal actions. A ledger reserves one second ahead, renewing every 0.2 seconds;
expired/failed accounting stops work. Interrupted recovery conservatively charges
the durable reservation while excluding wall-clock downtime. Successful
revalidation/restoration time is charged. See ADR-0011 for implementation limits,
including unverified physical reboot/power-loss, Linux and host I/O timing.

### Resource enforcement and sample extension (S006e)

Existing experiment `limits.resources` fields now enforce run-tree `ram_mb`,
`max_processes` and `cpu_cores` through Windows Job Objects, and workspace
`disk_mb` through supervisor checks/admission. Numeric storage/memory units are
MiB. CPU becomes `floor(cpu_cores * 10000 / logical_processors)` out of 10000
host cycles under ENABLE | HARD_CAP; this differs from sampled active CPU time.
All descendants/launchers count. The supervisor and model servers are outside
this job. Limits are reinstalled on resume. Unsupported platform limits,
unrepresentable CPU/integer bounds, VRAM limits (including zero), nested resource
wall clocks and unenforced max_model_tokens are refused. Use the top-level
experiment deadline. No schema or release version changed.

Disk is a supervisor quota, not an OS filesystem ceiling. Writing tool calls
and demonstrations at quota receive an infrastructure acknowledgement denial
before execution. The tool host records status denied. Reads remain available.
Periodic checks run every 0.1 seconds; a completed write can overshoot, while
an observed active writer above quota causes tree termination. Resource
termination does not automatically restart. Linked/unreadable quota paths fail
closed. Archives and model files are excluded from workspace byte counts.

`extensions.resource_sampling.interval_s` defaults to 1 and accepts finite
0.05–60 seconds. Samples are supervisor-owned and may interleave with existing
events. CPU/RAM/process/disk use job/process/workspace observations. Host NVIDIA
VRAM is optional and never claimed to be run-attributable. Sample payload
extensions name unavailable fields, CPU/RAM bases, VRAM scope/available MiB/age.
Missing fields are omitted; observed zero is numeric zero. Stage
`resource_limit_installed` records policy; `resource_limit` records observed
enforcement/denial/failure in supervisor actions. CPU records the applied rate;
Windows notification delivery and disk checks have the limitations in ADR-0012.

## Offline research contracts (S010a)

`study-manifest` and `evidence-export` 1.0.0 are additive research interfaces,
separate from the seven runtime contracts. World packaging remains unchanged.
Simulation receives their schema directory explicitly and copies the needed
schemas into each portable export, without importing Builder code. See
[the study protocol](../experiments/STUDY_PROTOCOL.md) for fields, canonical
configuration pins, outcome denominators, omitted operational records and the
limits of internal verification. General comparison/annotation validation is implemented by S010b below;
Window views remain S010c. ADR-0019 records this boundary.

### Study annotations and analysis (S010b)

`study-annotations` and `study-analysis` 1.0.0 add source-bound investigator
entries and reproducible descriptive reports over verified evidence exports.
These are research interfaces, not runtime contracts; no world/schema bundle
changes. Simulation validates citations, preserves missing/failed/censored cells,
separates roles and emits seven explicit gate requirements. See
[the analysis protocol](../experiments/STUDY_ANALYSIS.md) and ADR-0020.
Report directories bundle common plus these two schemas; verifying a report also
requires its associated pinned evidence export. Causal matching, independence,
chronology and scientific interpretation are never certified automatically.

## Change log

| Date | Contract | Version | Change |
| --- | --- | --- | --- |
| 2026-11-15 | study-annotations; study-analysis | 1.0.0 | S010b source-bound descriptive reports and typed citations; no runtime/world change |
| 2026-11-15 | study-manifest; evidence-export | 1.0.0 | S010a additive offline research interfaces; portable stopped-archive export; no runtime or world schema change |
| 2026-11-15 | (world capability content) | - | S008c minimal 0.8.0 adds bounded stats.describe and stats.regress using existing Python invocation and numeric JSON schemas; population variance, inclusive quartiles, OLS/correlation edge cases documented in manifests; no shared schema change |
| 2026-11-15 | (specialist service protocol) | - | S007e reserves an existing MCP invocation pair, adds bounded specialist configuration/IPC, durable consultation reservations and lease observations; minimal 0.7.0, no schema change; ADR-0018 |
| 2026-11-14 | (benchmark protocol) | - | S007d adds frozen cells/ledgers, initial-state observations, marked one-shot fault injection and source-bound derived analysis; existing extensions, no schema change |
| 2026-11-14 | (runtime policy protocol) | - | S007c freezes two scheduling policies, client context and explicit-memory identities; preserves idle checkpoint state and records exact model inputs before attempts. Existing extensions, no schema change |
| 2026-11-14 | (local gateway protocol) | — | S007a adds pinned model_catalog configuration, canonical catalog/model provenance binding and local adapter routing using existing extensions; no schema change |
| 2026-11-14 | (resource protocol) | — | S006e applies existing resource fields through Windows jobs/supervisor quota admission and trials sample metadata/config extensions; ADR-0012. No schema change |
| 2026-11-14 | (recovery protocol) | — | S006d trials extensions.recovery, conserved model-attempt and restart reservations, OS writer guard, interrupted startup scan and model health; ADR-0011. No schema change |
| 2026-11-14 | (supervisor protocol) | — | S006b implements bounded checkpoint_then_stop using existing fields and event extensions; ADR-0010 defines grace and termination. No schema change |
| 2026-11-14 | checkpoint-metadata | 1.0.1 | Clarifies that last_event_seq is the snapshot boundary; resume appends after the existing tail and records rollback/replay. Structure and constraints unchanged. S006a protocol, agent-owned memory and world 0.6.0 documented in ADR-0009 |
| 2026-11-14 | observation-event | 1.2.0 | Adds environment.message kind preamble for the generic discovery system message; minimal world 0.5.0 bundles it. Four meta-tool protocol specified (S005b) |
| 2026-11-14 | (release layout / protocol) | — | Generated registry format 1.0.0 and full documentation; disposable self-test workspaces; minimal world 0.4.0 adds workspace.write, workspace.list and time.now. No schema change (S005a) |
| 2026-11-13 | all | 1.0.0 | Initial versions (S001) |
| 2026-11-13 | (protocol) | — | Invocation protocol gains the `OPEN_LAB_WORKSPACE` variable, the empty child environment and the `denied` outcome; event-log canonical form and hash chain defined in OBSERVATION.md. No schema change (S003a) |
| 2026-11-14 | observation-event | 1.1.0 | New event type `environment.message` (payload `kind`, `text`, optional `after_seq`; recorder `agent_runtime` only): text the infrastructure gives the model as a conversation turn (S003c) |
| 2026-11-14 | experiment-config | 1.1.0 | New optional `continuation.message`, with its default text in the schema: what the runtime says when the model replies without a tool call (decision OD-5, S003c) |
| 2026-11-13 | capability | 1.0.1 | Descriptions of `invocation.entrypoint` and `invocation.command` now state where the module is found, the working directory, the meaning of `python` and how an error is reported. No structural change (S002) |
