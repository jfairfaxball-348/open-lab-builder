# Examples

One or more valid documents for every contract in `schemas/v1/`, laid out as
`examples/v1/<contract>/`. They are validated by the test suite and by
`olb check`, so they cannot drift from the schemas.

These are **illustrative documents, not a working world**. The capabilities,
model and run they describe do not exist yet:

- `capability/` describes two tools planned for S002. Their entrypoints are not
  implemented.
- `model-provider/` names a candidate model that has not been downloaded.
- `world-release/` is a `draft` with placeholder digests.
- `observation-event/run-excerpt.jsonl`, `artifact-metadata/` and
  `checkpoint-metadata/` show what a run's records will look like. No such run
  has happened.

Validate them with `uv run olb validate`.
