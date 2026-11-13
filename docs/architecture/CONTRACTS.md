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
