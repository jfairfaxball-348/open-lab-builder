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

**S001 (foundation) and S002 (minimal world packaging) are complete.** What
exists and works:

- Seven versioned JSON Schema contracts with validated examples.
- Two real capabilities in [`worlds/minimal/`](worlds/minimal/): `text.stats`
  and `math.evaluate` (exact arithmetic on a restricted grammar; no `eval`).
- `olb world build` — validates a world source, runs every capability's
  self-test and writes an immutable, digest-stamped release.
- `olb world verify` — checks a release against its manifest and digests.
- `olb validate` — validates contract documents and event logs.
- `olb diagnose` — read-only, sanitised audit of the local machine.
- `olb check` — project health check.
- Architecture, decision records, and a multi-session roadmap.

In the sibling `open-lab-simulation` repository, S003a, S003b and S003c are
also complete: `ols run` launches a supervised, fully recorded run driven by a
scripted stand-in or by one small local model (`llama3.2:3b` through Ollama). A reply without a tool call no longer ends a run: the
runtime answers with a fixed, recorded continuation message (S003c). Three
more candidate models were measured and compared
([orchestrator candidates](docs/experiments/2026-11-14-orchestrator-candidates.md)).

In the sibling `open-lab-window` repository, S004 is complete: `olw serve`
gives a read-only browser view of the run archives (run list, frozen
configuration, timeline with type filters, tool call and result pairs,
artifact previews, live tail of a run in progress).

What does **not** exist yet: capability search, the full model gateway,
memory, checkpoints, container isolation and run comparison. No experiment has
been run: the runs so far are engineering checks, recorded in
[docs/experiments/](docs/experiments/). Run `uv run olb
state` for the next milestone.

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
uv run olb world build worlds/minimal
```

```bash
uv run olb world verify releases/minimal/0.2.0 --self-test
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
worlds/minimal/          World source: world.json, capabilities/<id>/, models/
src/open_lab_builder/
  contracts/             Schema loading and document validation
  capabilities/          Build-time capability invoker (self-tests only)
  worlds/                World release build and verification
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
