# The Open Laboratory — World Builder

The Open Laboratory is an experimental platform for studying what autonomous
local AI agents actually do when they are given one prompt, a world full of
tools, and time.

An agent is launched with a single initial prompt. It discovers the tools in
its world, learns them from their documentation and demonstrations, and pursues
whatever it decides to pursue for minutes, hours or days, while independent
infrastructure records everything observable. A typical premise: *your creator
returns in 72 hours and will decide whether this world keeps running.*

These premises are philosophical experimental conditions. The project does not
claim, assume or try to produce consciousness. It records observable behaviour
and keeps model-generated claims separate from observed facts.

## Three repositories

| Repository | Role | Rule |
| --- | --- | --- |
| **open-lab-builder** (this one) | Engineers the universe: contracts, capability definitions, model manifests, versioned world releases, architecture and roadmap. | Never takes part in experiments. |
| **open-lab-simulation** | Inhabits the universe: launches experiments from one prompt, runs the agent in an isolated workspace, supervises, checkpoints and records. | The agent can never modify it. |
| **open-lab-window** | Observes the universe: read-only browser view of runs, timelines and artifacts. | Never influences a run. |

The three communicate only through the versioned contracts in
[`schemas/`](schemas/) and files on disk. See
[docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md).

## Status

**S001 (foundation and architecture) is complete.** What exists and works:

- Seven versioned JSON Schema contracts with validated examples.
- `olb validate` — validates contract documents and event logs.
- `olb diagnose` — read-only, sanitised audit of the local machine.
- `olb check` — project health check.
- Architecture, decision records, and a multi-session roadmap.

What does **not** exist yet: world packaging, any runnable capability, the
simulation runtime, the model gateway, and the Window. The documents under
[`examples/`](examples/) illustrate the contracts; they do not describe working
software. The next milestone is **S002 — Minimal World Packaging**.

## Quick start

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

```bash
uv run pytest
```

```bash
uv run olb check
```

```bash
uv run olb diagnose
```

```bash
uv run olb state
```

## Layout

```
schemas/v1/              Contract schemas (the source of truth for all three repositories)
examples/v1/<contract>/  Valid example documents, checked by the tests
src/open_lab_builder/
  contracts/             Schema loading and document validation
  diagnostics/           Machine audit and readiness assessment
  health.py              Project health check
  cli.py                 The `olb` command
tests/                   Contract and tooling tests
docs/
  architecture/          System design, contracts, observation, safety
  decisions/             Architecture decision records
  environment/           Sanitised report on the development machine
  roadmap/               ROADMAP.md and the machine-readable state.json
  development/           How to set up, test and extend
  experiments/           Experimental premises and protocol notes
```

## Development process

Work proceeds in small, verified milestones (S001, S002, …), one per coding
session. Each session reads [AGENTS.md](AGENTS.md), finds the next milestone in
[docs/roadmap/state.json](docs/roadmap/state.json), implements exactly that
milestone from [docs/roadmap/ROADMAP.md](docs/roadmap/ROADMAP.md), runs the
tests, updates the state and commits. `AGENTS.md` is the single authoritative
contract for both human contributors and coding agents (Claude Code, Codex).

## Governing principle

The Builder engineers the universe. The Simulation inhabits the universe. The
Window observes the universe. The three must remain independent.
