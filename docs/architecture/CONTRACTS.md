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
```

Files are copied byte for byte from the world source (`worlds/<name>/` in this
repository). Nothing is rewritten: no line-ending conversion, no
re-serialisation. The repository stores text with LF endings
(`.gitattributes`), so a build is the same on Windows and Linux. Bytecode
caches (`__pycache__`, `*.pyc`) are never copied, and symbolic links are
refused.

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

## Change log

| Date | Contract | Version | Change |
| --- | --- | --- | --- |
| 2026-11-13 | all | 1.0.0 | Initial versions (S001) |
| 2026-11-13 | (protocol) | — | Invocation protocol gains the `OPEN_LAB_WORKSPACE` variable, the empty child environment and the `denied` outcome; event-log canonical form and hash chain defined in OBSERVATION.md. No schema change (S003a) |
| 2026-11-14 | observation-event | 1.1.0 | New event type `environment.message` (payload `kind`, `text`, optional `after_seq`; recorder `agent_runtime` only): text the infrastructure gives the model as a conversation turn (S003c) |
| 2026-11-14 | experiment-config | 1.1.0 | New optional `continuation.message`, with its default text in the schema: what the runtime says when the model replies without a tool call (decision OD-5, S003c) |
| 2026-11-13 | capability | 1.0.1 | Descriptions of `invocation.entrypoint` and `invocation.command` now state where the module is found, the working directory, the meaning of `python` and how an error is reported. No structural change (S002) |
