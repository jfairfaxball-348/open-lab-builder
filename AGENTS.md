# AGENTS.md — development contract for The Open Laboratory

This file is the single authoritative set of instructions for anyone working
in this repository: Claude Code, OpenAI Codex, other coding agents and human
contributors. `CLAUDE.md` only imports this file. Do not create a second copy
of these rules anywhere.

## What this project is

An experimental platform for observing autonomous local AI agents. Three
independent repositories:

- **open-lab-builder** (this one) engineers the world: contracts, capabilities,
  model manifests, versioned world releases, architecture and roadmap.
- **open-lab-simulation** runs experiments: one prompt, isolated workspace,
  supervised agent, recorded events.
- **open-lab-window** is a read-only view of recorded runs.

They share contracts (`schemas/`) and a data directory, never code. The
sibling checkouts sit next to this one on disk; find them, do not assume a
path. Read [README.md](README.md) and
[docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) before
changing anything structural.

## Start of every session

1. Read this file.
2. `git status` and `git log --oneline -10`. Preserve any uncommitted work
   you did not create; ask before discarding anything.
3. `uv sync`, then `uv run olb state` to see completed milestones, the next
   milestone, blockers and open decisions
   (source: [docs/roadmap/state.json](docs/roadmap/state.json)).
4. Read the next milestone's section in
   [docs/roadmap/ROADMAP.md](docs/roadmap/ROADMAP.md), and the architecture
   documents and decision records it touches.
5. `uv run olb check --tests` to confirm you are starting from a passing state.
   If it fails, fixing that is the first task.
6. Inspect the existing implementation the milestone builds on.
7. Make a short plan for that milestone only.

If the next milestone belongs to another repository, work there, following
that repository's `AGENTS.md`. The roadmap and `state.json` stay here and are
updated here.

## During the session

- Implement **only** the milestone and what it strictly needs. Note good ideas
  for later in the roadmap instead of building them.
- If the milestone is too big for one session, split it in the roadmap first
  (letter suffix), then do the first part.
- If a milestone needs a human action listed as a blocker (a download, an
  administrator change), do not work around it. Stop, report it, and pick the
  next unblocked milestone if the roadmap allows.
- Follow the architecture. To deviate, write a new decision record in
  `docs/decisions/` explaining why, and update the affected documents.

## End of every session

1. `uv run ruff check .` and `uv run olb check --tests` must pass.
2. Update documentation that the work made stale (README status, architecture,
   CONTRACTS.md change log).
3. Update `docs/roadmap/state.json`: `completed_milestones`, `next_milestone`,
   `blockers`, `known_issues`, `open_decisions`, and `validation` with the
   commands you actually ran and their real results. Mark the milestone's
   status in ROADMAP.md.
4. Commit with a message starting with the milestone id, e.g.
   `S002: minimal world packaging`.
5. Push to the configured remote if authorised and available. If the push
   fails, keep the commit and report why.
6. Report: what was built, what was tested and the results, unresolved issues,
   and the exact next milestone.

A milestone is complete only when **every** exit criterion in the roadmap is
met and verified. Otherwise leave it incomplete and record what remains.

## Rules that do not bend

**Honesty**
- Never report something as working that you did not run. Never skip a failing
  test silently, weaken an assertion to make it pass, or mark a milestone
  complete on partial evidence.
- No placeholder modules, stub functions or empty files that suggest
  functionality that is not there.
- Documentation states plainly what is implemented and what is only designed.

**Boundaries**
- The Builder never takes part in experiments. The Simulation never imports
  Builder code. The Window never writes to anything.
- Nothing an agent inside an experiment says, and no premise in a prompt, may
  ever grant privileges. Authority comes only from the experiment
  configuration, enforced by the supervisor. See
  [docs/architecture/SAFETY_AND_ISOLATION.md](docs/architecture/SAFETY_AND_ISOLATION.md).
- Observation records are written by infrastructure, outside the agent's
  reach, and distinguish observed behaviour from agent claims. Never record an
  inferred mental state as fact. See
  [docs/architecture/OBSERVATION.md](docs/architecture/OBSERVATION.md).
- Capabilities that execute agent-supplied code require the container
  isolation tier. Do not ship one on the process tier.

**Contracts**
- `schemas/` is the interface between repositories. Changing a schema means:
  bump `x-schema-version` per the rules in
  [docs/architecture/CONTRACTS.md](docs/architecture/CONTRACTS.md), update
  examples and tests, add a change-log row. Breaking changes need a new major
  directory and a decision record.

**Privacy and hygiene**
- Never commit personal paths, user or host names, credentials, tokens, raw
  diagnostics or private file listings. Raw local output goes under `.local/`
  (ignored). `olb check` scans for this; do not bypass it.
- Never commit model weights or built world releases.
- Do not download models, install system software or change system settings
  unless the human has authorised that specific action.

**Git**
- No history rewriting, force pushes, `reset --hard`, or other destructive
  commands. No `--no-verify`.
- Do not modify sibling repositories unless the current milestone belongs to
  them.

## Commands

| Command | Purpose |
| --- | --- |
| `uv sync` | Create or update the virtual environment |
| `uv run pytest` | Run the tests |
| `uv run ruff check .` | Lint |
| `uv run olb check [--tests]` | Project health check |
| `uv run olb validate [files]` | Validate contract documents or `.jsonl` event logs |
| `uv run olb diagnose [--json] [--save-raw]` | Sanitised machine audit |
| `uv run olb state` | Progress and next milestone |

More detail: [docs/development/DEVELOPMENT.md](docs/development/DEVELOPMENT.md).

## Code conventions

- Python 3.12, standard library first. Add a dependency only when a milestone
  needs it, and say why in the commit.
- Code must run on Windows and Linux: use `pathlib`, never shell out through a
  shell string, never assume POSIX.
- Every behaviour has a test. Tests that need a model or other heavy resource
  use a fake by default; real-resource checks are separate, documented manual
  steps whose results are recorded.
- Comments explain constraints and reasons, not what the next line does.
