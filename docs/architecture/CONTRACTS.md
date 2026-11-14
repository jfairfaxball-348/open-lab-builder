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
arbitrary capability code on the process tier; container isolation is S006c.

### Model provider

Separates the gateway-facing model `id` from the provider's own name
(`provider_ref`), so an experiment can name `orchestrator-small` and the world
decides what serves it. `footprint.measured` distinguishes estimates from
measurements on the target machine; `status` distinguishes validated models
from ones that are merely present or not downloaded at all.

### Experiment configuration

Holds everything needed to reproduce a launch: prompt, world and digest, model
and sampling parameters, limits, permissions, checkpointing and termination.
A premise in `initial_prompt` grants nothing; only `permissions` and `limits`
do. `research_question` is never shown to the agent.

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
See ADR-0010. Automatic crash/reboot and stale-lock recovery remain S006d.
Stopped runs must have a valid summary for manual resume.

## Change log

| Date | Contract | Version | Change |
| --- | --- | --- | --- |
| 2026-11-14 | (supervisor protocol) | — | S006b implements bounded checkpoint_then_stop using existing fields and event extensions; ADR-0010 defines grace and termination. No schema change |
| 2026-11-14 | checkpoint-metadata | 1.0.1 | Clarifies that last_event_seq is the snapshot boundary; resume appends after the existing tail and records rollback/replay. Structure and constraints unchanged. S006a protocol, agent-owned memory and world 0.6.0 documented in ADR-0009 |
| 2026-11-14 | observation-event | 1.2.0 | Adds environment.message kind preamble for the generic discovery system message; minimal world 0.5.0 bundles it. Four meta-tool protocol specified (S005b) |
| 2026-11-14 | (release layout / protocol) | — | Generated registry format 1.0.0 and full documentation; disposable self-test workspaces; minimal world 0.4.0 adds workspace.write, workspace.list and time.now. No schema change (S005a) |
| 2026-11-13 | all | 1.0.0 | Initial versions (S001) |
| 2026-11-13 | (protocol) | — | Invocation protocol gains the `OPEN_LAB_WORKSPACE` variable, the empty child environment and the `denied` outcome; event-log canonical form and hash chain defined in OBSERVATION.md. No schema change (S003a) |
| 2026-11-14 | observation-event | 1.1.0 | New event type `environment.message` (payload `kind`, `text`, optional `after_seq`; recorder `agent_runtime` only): text the infrastructure gives the model as a conversation turn (S003c) |
| 2026-11-14 | experiment-config | 1.1.0 | New optional `continuation.message`, with its default text in the schema: what the runtime says when the model replies without a tool call (decision OD-5, S003c) |
| 2026-11-13 | capability | 1.0.1 | Descriptions of `invocation.entrypoint` and `invocation.command` now state where the module is found, the working directory, the meaning of `python` and how an error is reported. No structural change (S002) |
