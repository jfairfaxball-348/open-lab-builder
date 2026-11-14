# Development guide

The rules of engagement are in [AGENTS.md](../../AGENTS.md). This document is
the practical reference for the Builder's tooling.

## Setup

Requires Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

This creates `.venv/` with the project installed in editable mode, plus
`pytest` and `ruff`. The project never uses packages from the base
interpreter.

## Tests

```bash
uv run pytest
```

| File | Covers |
| --- | --- |
| `tests/test_contracts.py` | Every schema is valid and versioned; every example validates; each required field is enforced; unknown fields are rejected; version compatibility; path safety |
| `tests/test_capability_manifest.py` | Capability manifests are self-consistent (demonstrations against their own schemas, self-test references, invocation interfaces, provenance) |
| `tests/test_observation_events.py` | Integrity rules: the agent is never the recorder, claims and observations cannot be confused, logs are gap-free and single-run |
| `tests/test_tooling.py` | The diagnostic runs on this machine and its sanitised output leaks nothing; the health check passes; the CLI works |
| `tests/test_registry.py` | Fixed-query relevance, deterministic ranking and index bytes, complete generated documentation |
| `tests/test_workspace_capabilities.py` | Shipped workspace writing/listing and UTC time, path refusals, disposable self-tests |
| `tests/test_memory_capabilities.py` | Real SQLite persistence, revisions, literal search, bounded inputs and corruption errors |

The tooling tests run the real machine audit once, so the suite takes some
tens of seconds.

## Lint

```bash
uv run ruff check .
```

## Health check

```bash
uv run olb check --tests
```

Checks, in order: the schemas are well formed and versioned; every contract has
at least one example and all examples validate; required documents exist;
`state.json` is valid and consistent with the roadmap; nothing committable
contains a local path, user name, host name, model weights or an oversized
file; and, with `--tests`, the test suite passes. Exit code 0 means healthy.

## Validating documents

```bash
uv run olb validate
```

With no arguments it validates everything under `examples/`. Pass file paths to
validate your own documents. A `.json` file is one document; a `.jsonl` file is
an event log and is additionally checked for ordering and run consistency.

From Python:

```python
from open_lab_builder.contracts import validate_document, validate_event_stream

issues = validate_document(document)   # [] means valid
```

## Building a world

```bash
uv run olb world build worlds/minimal
```

Validates the source, copies it to a staging directory, runs every
capability's self-test against the staged copy, and only then writes
`releases/<world_id>/<version>/` with a `world-release.json`. If anything
fails, no release directory is left behind. `--out DIR` builds elsewhere;
`--publish` builds into `<data root>/worlds/` (`$OPEN_LAB_DATA`, or
`open-lab-data` in the home directory).

```bash
uv run olb world verify releases/minimal/0.6.0 --self-test
```

Recomputes every digest and re-validates the manifests against the contracts
bundled in the release. A release is immutable: to change a world, change the
`version` in its `world.json`.

### Searching a built registry (S005a)

```python
import json
from pathlib import Path
from open_lab_builder.capabilities.registry import search

release = Path("releases/minimal/0.6.0")
index = json.loads((release / "registry/index.json").read_text(encoding="utf-8"))
matches = search(index, "save notes", category="workspace", limit=3)
text = (release / matches[0]["documentation_path"]).read_text(encoding="utf-8")
```

The index and documentation are generated from validated manifests and covered
by the release digest. Search is a pure function; it executes no capabilities.
The Simulation implements discovery meta-tools (S005b) without importing
Builder code. Filesystem self-test demonstrations run in independent empty
temporary workspaces; do not assume a previous demonstration created a file.

### Adding a capability to a world

1. Create `worlds/<world>/capabilities/<id>/` with a `capability.json` whose
   `id` equals the directory name, and the implementation beside it. Nothing
   outside that directory is available at run time.
2. Follow the invocation protocol in
   [CONTRACTS.md](../architecture/CONTRACTS.md#capability). Standard library
   only, unless the manifest declares `dependencies`.
3. Give it demonstrations with exact expected output and list them in
   `self_test`. The build runs them.
4. Add tests, including inputs that must be refused.
5. A capability that runs agent-supplied code or needs the `subprocess`
   permission can only ship in a world whose minimum isolation tier is
   `container`. The build enforces the second; the first is on you.

## Machine diagnostic

```bash
uv run olb diagnose
```

Read-only. Prints a sanitised report: hardware, isolation mechanisms, model
servers and models, tools on PATH, packages in the base interpreter, and a
readiness assessment. `--json` for machine-readable output. `--save-raw` also
writes the unsanitised report to `.local/diagnostics/` (ignored by Git). The
curated findings are in
[LOCAL_ENVIRONMENT.md](../environment/LOCAL_ENVIRONMENT.md); refresh that
document when the machine changes materially.

## Adding or changing a contract

1. Edit or add the schema in `schemas/v1/`. Give every field a `description`.
2. Set `x-schema-version` according to the compatibility rules in
   [CONTRACTS.md](../architecture/CONTRACTS.md).
3. Add or update an example in `examples/v1/<contract>/`.
4. Add tests for any new rule, including a document that must be rejected.
5. If the rule cannot be expressed in JSON Schema, implement it in
   `src/open_lab_builder/contracts/validation.py` and document it in
   CONTRACTS.md so other consumers can reproduce it.
6. Add a row to the CONTRACTS.md change log.

A new public contract also needs adding to `CONTRACT_NAMES` in
`validation.py`.

## Local-only files

Anything under `.local/` is ignored by Git. Use it for raw diagnostics,
scratch output and notes that mention the machine. Built world releases go
under `releases/` (also ignored) or the data root.
