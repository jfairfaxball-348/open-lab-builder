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
- Eleven real capabilities in [`worlds/minimal/`](worlds/minimal/): `text.stats`,
  `math.evaluate` (exact restricted arithmetic), `workspace.write`,
  `workspace.list`, `time.now`, `memory.write`, `memory.search`, `memory.list`
  supervisor-mediated `models.ask` (minimal 0.7.0), and `stats.describe` /
  `stats.regress` (minimal 0.8.0).
- S005a: world 0.4.0 includes a deterministic registry index, pure-Python ranked
  keyword search and documentation generated from every manifest section.
- `olb world build` — validates a world source, runs every capability's
  self-test and writes an immutable, digest-stamped release.
- `olb world verify` — checks a release against its manifest and digests.
- `olb validate` — validates contract documents and event logs.
- `olb diagnose` — read-only, sanitised audit of the local machine.
- `olb check` — project health check.
- Architecture, decision records, and a multi-session roadmap.

In the sibling `open-lab-simulation` repository, S003a, S003b, S003c and S005b are
also complete: `ols run` launches a supervised, fully recorded run driven by a
scripted stand-in or by one small local model (`llama3.2:3b` through Ollama). A reply without a tool call no longer ends a run: the
runtime answers with a fixed, recorded continuation message (S003c). Three
more candidate models were measured and compared
([orchestrator candidates](docs/experiments/2026-11-14-orchestrator-candidates.md)).
The model now sees only four discovery meta-tools: search, describe,
demonstrate and invoke. Its generic system preamble is recorded with
observation-event 1.2.0, bundled in minimal world 0.5.0. A bounded real-model
search → describe → invoke check passed with recorded argument repairs;
[results and limits](docs/experiments/2026-11-14-discovery-meta-tools.md).
S006a adds SQLite memory, complete-step checkpoints and `ols resume`. A scripted
pause/resume restores the same files and memory as uninterrupted execution,
preserves the event chain, rejects corrupt snapshots and excludes paused time
from the budget. Minimal world 0.6.0 includes the memory capabilities and
checkpoint-metadata 1.0.1; [validation and limits](docs/experiments/2026-11-14-memory-checkpoints.md).

S006b adds bounded graceful deadline checkpointing: one fixed grace allowance
for the in-flight step and snapshot, followed by supervisor termination before
another step starts. Hard stop remains available; see
[deadline validation](docs/experiments/2026-11-14-graceful-deadlines.md).

S006d adds opt-in bounded runtime restarts, `ols recover` startup scanning,
OS-serialized writer ownership with process birth identities, conserved budgets
and asynchronous model-health probes. The supervisor retains the existing log
and restores a verified checkpoint. Live/unverifiable writers and damaged logs
are refused. See [recovery validation](docs/experiments/2026-11-14-supervisor-recovery.md).
No OS startup task is installed; physical reboot/power-loss and Linux remain
unverified.

S006e adds Windows Job Object RAM/process/CPU caps, suspended startup,
supervisor workspace quota admission and periodic resource samples (including
available host NVIDIA VRAM when measurable). Unsupported limits are refused.
Workspace quotas are checked by the supervisor and may overshoot during a
write; they are not OS filesystem quotas. See
[resource validation](docs/experiments/2026-11-14-resource-enforcement.md).

S006c adds the container tier for Windows hosts: each capability call of a
`minimum_tier: container` world runs in a fresh rootless Podman container in
WSL 2 with no network, no Linux capabilities, a read-only root, the world
read-only and the workspace as the only host mount, under memory/CPU/process
ceilings; the supervisor removes the run's containers whenever it stops. No
shipped capability runs agent-supplied code yet. See
[container validation](docs/experiments/2026-11-14-container-isolation.md).

In the sibling `open-lab-window` repository, S004 is complete: `olw serve`
gives a read-only browser view of the run archives (run list, frozen
configuration, timeline with type filters, tool call and result pairs,
artifact previews, live tail of a run in progress).

S007a adds an independent pinned local model catalog, Ollama and loopback
chat-compatible routing, and frozen provenance. Two installed orchestrators ran
against the same unchanged world; see [gateway validation](docs/experiments/2026-11-14-local-gateway.md).

S007c adds versioned immediate-continuation and quiet-until-deadline policies,
checkpointed idle state and exact pre-request model input records. Native
pause/resume preserved quiet idling without another model call; see
[runtime policy validation](docs/experiments/2026-11-14-runtime-policies.md).
Both policies are experimental treatments, not assertions of neutrality.

**Hosted comparison programme (S014).** The owner has started a programme
comparing hosted models in the unchanged world. S014a assessed the official
routes and fixed the architecture ([ADR-0016](docs/decisions/ADR-0016-hosted-provider-broker.md),
[provider assessment](docs/architecture/HOSTED_PROVIDERS.md)): Google Gemma and
ChatGPT plan usage are eligible; the owner excluded Anthropic. The broker
(S014b) and two adapters exist. Gemma (S014c) invoked capabilities but hit
intermittent provider errors on multi-step turns; the owner scrapped it. ChatGPT plan usage (S014d)
completed a live tool-use round trip on `gpt-6.1-sol`
([integration report](docs/experiments/2026-11-15-chatgpt-integration.md)).
The S014g compatibility suite then admitted ChatGPT plan usage
([report](docs/experiments/2026-11-15-hosted-compatibility.md)). These are
integration checks, not behavioural evidence.

The registered campaign s014i-001 then ran 24 cells on ChatGPT plan usage:
**INCONCLUSIVE** under the registered rules, with the open-ended arm qualifying on
all three seeds ([report](docs/experiments/2026-11-15-hosted-comparison.md)).
S014l fixed the event-log reader defect behind its one invalid record
([report](docs/experiments/2026-11-15-event-log-reader-fix.md)); the result
itself is unchanged. S014m versioned the rubric
([v1.1](docs/experiments/S007d-RUBRIC-v1.1.md)) and registered a confirmatory
replication, [s014i-002](docs/experiments/registrations/S014i-002.md). The owner
then accepted S014i-001 as a GO under rubric v1.1 (A 5/6, C 6/6) instead of
running it, and decided that new capabilities are tested one at a time rather
than by full baseline repeats
([ADR-0017](docs/decisions/ADR-0017-owner-accepted-go-and-capability-testing.md)). This is an owner-accepted post-hoc
GO, not a registered one.

S007e adds local llama3.2:3b consultation under one supervisor-owned GPU lease
beside hosted orchestration. Configuration bounds prompts, replies, calls and
lease lifetime; the supervisor records and reserves each consultation, keeps
monitoring during inference and unloads at segment exit/expiry. See
[ADR-0018](docs/decisions/ADR-0018-supervisor-specialist-consultation.md) and the
[frozen capability check](docs/experiments/registrations/S007e-001.md).
World 0.6.0 remains unchanged and runnable. The guided check discovered,
consulted and used the answer; the unguided check closed with partial coverage
after a plan-quota stop (C1 no consultation, C2 censored, C3 unstarted).
[Results and limits](docs/experiments/2026-11-15-specialist-consultation.md).
S008c's separate four-run capability check is now complete; its own allowance
was used without reruns. Next: **S010 — Experimental Protocol and Comparative Observation**.

S008c's engineering is implemented: bounded population statistics/inclusive
quartiles and ordinary least-squares regression with Pearson r, using only the
standard library and no additional permissions. Numeric tests and a scripted
supervisor archive pass. All four hosted check archives verify: both tools
were used in the guided run; regression was used with result-linked artifacts
in 2/3 unguided C runs, while description was not invoked in any C run.
This completes the approved statistics part without a new autonomy GO.
[Capability report](docs/experiments/2026-11-15-statistics-capability-check.md),
[engineering checkpoint](docs/experiments/2026-11-15-statistics-capabilities.md).

What does **not** exist yet: a registered (prospective) GO,
container isolation on Linux or with network access, and run comparison. The first
registered short baseline is complete; earlier engineering checks are recorded in
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
uv run olb world verify releases/minimal/0.8.0 --self-test
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

**S013 strategic realignment is complete as planning.** Existing engineering and
the three-repository architecture are preserved. S007a local gateway is complete.
S007d-001 is complete with **NO_GO**: all 24 cells verified, but no complete
guided control or qualifying unguided run. S007h also returned NO_GO. Subsequent
hosted work led to the owner-accepted post-hoc GO in ADR-0017 and per-capability
checks; S007e is closed with the partial coverage stated above. S008c's approved
statistics part is complete with its full four-run capability report. Next is S010.
A valid negative
report remains a completed research result, not a capability claim. Hosted models
are optional and separately authorised; real isolation remains mandatory for
agent-authored execution and unattended certification.

See the [research audit/plan](docs/architecture/AUTONOMY_AND_EXPERIMENTAL_READINESS.md),
[benchmark/validity specification](docs/experiments/README.md) and
[dependency-aware roadmap](docs/roadmap/ROADMAP.md). The [registered baseline report](docs/experiments/2026-11-14-autonomy-baseline.md)
and [derived results](docs/experiments/results/S007d-001.json) retain negative
and partial findings. ChatGPT plan usage is implemented; long-duration campaigns
and other unapproved hosted routes remain future work.
S006e's historical validation is preserved in
[its immutable snapshot](docs/roadmap/validation/S006e.json).

Work proceeds in small, verified milestones (S001, S002, …), one per coding
session. Each session reads [AGENTS.md](AGENTS.md), finds the next milestone in
[docs/roadmap/state.json](docs/roadmap/state.json), implements exactly that
milestone from [docs/roadmap/ROADMAP.md](docs/roadmap/ROADMAP.md), runs the
tests, updates the state and commits. `AGENTS.md` is the single authoritative
contract for both human contributors and coding agents (Claude Code, Codex).

## Governing principle

The Builder engineers the universe. The Simulation inhabits the universe. The
Window observes the universe. The three must remain independent.

## Licence

Apache License 2.0; see [LICENSE](LICENSE).
