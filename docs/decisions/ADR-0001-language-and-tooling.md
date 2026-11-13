# ADR-0001: Python 3.12 with uv and minimal dependencies

Status: Accepted (S001)

## Context

The platform glues together model servers, scientific libraries and
command-line tools, and will be developed over many sessions by coding agents.
The development machine already has Python 3.12 and uv. Its base interpreter
has many globally installed packages of unknown provenance.

## Decision

- Python 3.12+ is the language of the Builder and the Simulation.
- `uv` manages a per-repository virtual environment with a committed lock file.
  Nothing relies on the base interpreter's packages.
- The Builder's only runtime dependency is `jsonschema`. The CLI uses
  `argparse`; diagnostics use the standard library.
- `pytest` for tests and `ruff` for linting.
- A dependency is added only when a milestone needs it, and is recorded in the
  milestone's notes.

## Alternatives

- **TypeScript/Node** — good for the Window, but the model and scientific
  ecosystem the capabilities wrap is Python-first.
- **Rust or Go core** — stronger isolation primitives, much slower iteration;
  no present need.
- **Pydantic models as the contract source** — convenient in Python, but makes
  the contracts a Python artefact. See ADR-0002.
- **Typer/Click/Rich for the CLI** — unnecessary for four subcommands.

## Consequences

- Any contributor or agent reproduces the environment with `uv sync`.
- The Window may use a different language; it shares contracts, not code.
- Windows is the primary platform today, so code must not assume POSIX; the
  design must still work on Linux, where the container tier will run.
