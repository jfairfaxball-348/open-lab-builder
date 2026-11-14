# Examples

One or more valid documents for every contract in `schemas/v1/`, laid out as
`examples/v1/<contract>/`. They are validated by the test suite and by
`olb check`, so they cannot drift from the schemas.

What is real and what is only illustrative:

- `capability/` holds copies of the manifests of the two working capabilities
  in [`worlds/minimal/`](../worlds/minimal/). A test keeps them identical.
- `world-release/minimal-world.json` is a hand-written `draft` with placeholder
  digests, showing the shape of a manifest. A real one is produced by
  `uv run olb world build worlds/minimal`.
- `model-provider/` is a copy of the minimal world's provider manifest, with footprint
  figures measured on the development machine.
- `experiment-config/`, `observation-event/run-excerpt.jsonl`,
  `artifact-metadata/` and `checkpoint-metadata/` show what an experiment and
  its records will look like. No run has happened.

Validate them with `uv run olb validate`.
