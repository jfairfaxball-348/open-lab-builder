# Architecture

Status: established in S001. Implemented so far: the contracts, the builder
tooling, the world release manager (S002), the generated registry, documentation
and five simple capabilities (S005a), and in
`open-lab-simulation` the experiment manager, a minimal supervisor, the
recorder, the tool host and the agent loop (S003a), driven either by a
scripted stand-in or by one local model through Ollama's chat-completions
endpoint (S003b), now through four discovery meta-tools (S005b), with durable
memory/checkpoints (S006a), graceful deadlines (S006b) and opt-in bounded
recovery (S006d) and process resources/sampling (S006e). Other sections describe later designs. Each section says
which milestone delivers it.

Related: [CONTRACTS.md](CONTRACTS.md) · [OBSERVATION.md](OBSERVATION.md) ·
[SAFETY_AND_ISOLATION.md](SAFETY_AND_ISOLATION.md) ·
[decision records](../decisions/README.md)

## 1. Three repositories, three roles

| | Builder | Simulation | Window |
| --- | --- | --- | --- |
| Verb | engineers | inhabits | observes |
| Owns | Contracts, capability sources, model manifests, world releases, architecture, roadmap | Experiment manager, agent runtime, tool host, model gateway, memory, supervisor, event recorder | Read-only API and browser UI |
| Writes | World releases | Run archives, workspaces | Nothing |
| Reads | The machine (diagnostics) | World releases | Run archives |
| Must never | Take part in a run | Be writable by the agent | Send anything into a run |

The repositories share **no code**. They share:

1. **Contracts** — JSON Schemas in this repository's `schemas/`, copied into
   every world release so that a release is self-describing.
2. **A data root** — a directory outside all three checkouts, located by the
   `OPEN_LAB_DATA` environment variable (default: `open-lab-data` in the home
   directory).

```
$OPEN_LAB_DATA/
  worlds/<world_id>/<version>/         world releases   (Builder writes; read-only afterwards)
  runs/<experiment_id>/<run_id>/       run archives     (Simulation infrastructure writes; never the agent)
  workspaces/<run_id>/                 agent workspaces (the only place an agent can write; disposable)
```

```mermaid
flowchart LR
    subgraph B["open-lab-builder"]
        contracts["Contracts<br/>(schemas/)"]
        capsrc["Capability sources<br/>+ model manifests"]
        wrm["World release manager"]
        diag["Diagnostics"]
    end

    subgraph D["Data root (outside every repository)"]
        worlds[("worlds/<br/>immutable releases")]
        runs[("runs/<br/>append-only archives")]
        ws[("workspaces/<br/>agent-writable")]
    end

    subgraph S["open-lab-simulation"]
        em["Experiment manager"]
        sup["Runtime supervisor"]
        rt["Agent runtime"]
        th["Tool host +<br/>capability registry"]
        gw["Model gateway"]
        mem["Memory subsystem"]
        obs["Observation recorder"]
    end

    subgraph W["open-lab-window"]
        api["Read-only API"]
        ui["Browser UI"]
    end

    models["Local model servers<br/>(Ollama, ...)"]

    contracts --> wrm
    capsrc --> wrm
    wrm -- "build, validate, version" --> worlds
    worlds -- "instantiate" --> em
    em --> sup
    sup -- "starts, limits, stops" --> rt
    rt --> th
    rt --> gw
    rt --> mem
    th --> ws
    gw --> models
    em --> obs
    sup --> obs
    rt --> obs
    th --> obs
    gw --> obs
    obs -- "append" --> runs
    runs -- "read only" --> api
    api --> ui
```

## 2. Subsystems

### World release manager — Builder (S002, implemented)

`olb world build` and `olb world verify`. The exact layout, digest algorithm
and invocation protocol are specified in
[CONTRACTS.md](CONTRACTS.md#world-release). Turns capability sources and model manifests into an immutable directory:

```
<world_id>/<version>/
  world-release.json        manifest (contract: world-release)
  contracts/v1/*.schema.json   the exact contract versions this world speaks
  capabilities/<id>/capability.json + implementation files
  models/<provider>.json
```

Build steps: validate every manifest, run every capability self-test, compute
per-file SHA-256 digests and an overall `content_digest`, set `status` to
`validated`. A release is never edited; a change is a new version. Failure
modes: a self-test fails (no release is produced), or a digest mismatch at
launch (the Simulation refuses to start).

### Capability registry — Builder defines, Simulation serves (S002, S005)

A capability is one directory with a `capability.json` manifest
([contract](CONTRACTS.md#capability)). The registry is the set of manifests in
a world release plus, later, tools the agent creates inside its own sandbox.

Implemented in S005a: build-time `registry/index.json`, full generated
`registry/docs/<id>.txt`, and pure-Python weighted keyword search in the Builder
(format and ranking in CONTRACTS.md). Minimal world 0.4.0 contains five
capabilities, including workspace text writing/listing and UTC time. The
Simulation serves the four meta-tools below (S005b); these are the only tools
presented to the model. Its generic system preamble names no world capability.
Search uses the bundled index, describe reads the generated documentation and
includes the input schema and a manifest-derived example call, demonstrate
executes a shipped example, and invoke validates and runs the actual tool.
Allow/deny lists and permissions apply to discovery as well as execution.

The agent's initial prompt does **not** list the tools. The runtime exposes
four fixed meta-tools, and everything else is discovered through them:

| Meta-tool | Purpose |
| --- | --- |
| `capabilities.search(query, category?)` | Ranked summaries from names, summaries, categories and keywords |
| `capabilities.describe(id)` | Full documentation, schemas, limitations, failure modes |
| `capabilities.demonstrate(id, demo_id?)` | Run a shipped demonstration and show input and real output |
| `capabilities.invoke(id, arguments)` | Validated call through the tool host |

This keeps the prompt constant as the world grows and makes discovery itself
observable behaviour. See [ADR-0003](../decisions/ADR-0003-capability-manifest.md).

### Model gateway — Simulation (S003b minimal, S007 full)

Implemented so far (S003b): a single chat model client with tool calling,
tool-call repair, one retry, a context-length guard, and the model's identity
recorded in the archive. Only the four discovery meta-tools are offered (S005b).
Not implemented: multiple models, loading and
unloading, memory scheduling.

One internal interface for every model, whatever serves it. Request and
response use the OpenAI chat-completions shape, which Ollama, llama.cpp's
server and LM Studio all expose. Provider adapters translate anything else.
The gateway also owns **memory scheduling**: it knows each model's footprint
from the model-provider manifest and loads specialist models one at a time,
unloading the previous one first (see
[LOCAL_ENVIRONMENT.md](../environment/LOCAL_ENVIRONMENT.md#resource-strategy)).
Every call is recorded as a `model.call` event by the gateway, not the agent.
Failure modes: server down (retry, then `error` event and supervisor decision),
out-of-memory on load (unload others, retry once, then fail the tool call).

### Agent runtime — Simulation (S003)

A small, explicit loop — no agent framework ([ADR-0004](../decisions/ADR-0004-orchestration.md)):

```
state = load_or_create(conversation, memory)
loop:
    reply = gateway.chat(orchestrator_model, state.messages, tools=meta_tools)
    record agent.output
    for each tool call in reply: result = tool_host.invoke(...)   # records tool.call / tool.result
    append results to state; persist state
    if supervisor says stop: break
```

The runtime holds no authority. It cannot extend its deadline, change its
permissions or write to the run archive except through the recorder.

### Memory subsystem — Simulation (S006a)

Implemented in S006a, with the detailed protocol in
[ADR-0009](../decisions/ADR-0009-checkpoint-barriers-and-agent-memory.md).
Per-run and durable, in three parts: the **conversation state** needed to
resume the loop; an **agent memory store** (SQLite, exposed to the agent as
capabilities such as `memory.write` / `memory.search`); and the **workspace**
file tree. All three are snapshotted together as a checkpoint
([contract](CONTRACTS.md#checkpoint-metadata)) stored in the run archive, out of
the agent's reach.

Live agent memory is `.memory.sqlite` in the workspace, exposed through
`memory.write`, `memory.search` and `memory.list`. `NOTES.md` is the working-notes
convention. This refines ADR-0007's originally planned supervisor-area memory:
the live database is entirely agent-owned data; protected checkpoint copies
remain in the archive. No authority is read from memory.

The runtime blocks at complete-step barriers while the supervisor takes an
initial snapshot, interval snapshots when due, and pre-shutdown snapshots for
normal completion/cooperative operator pause. `ols resume <archive>` restores a
verified checkpoint and appends a recovery segment to the same event log.
Corrupt snapshots are rejected in favour of earlier valid ones. Existing
observations survive rollback; step/time budgets are not reset. Hard deadline
termination retains the previous safe snapshot. S006b implements
`checkpoint_then_stop` with a fixed additional grace allowance (default zero),
a complete-step snapshot and supervisor termination before acknowledging the
barrier. See [ADR-0010](../decisions/ADR-0010-bounded-deadline-checkpoints.md).
S006d adds opt-in bounded worker restarts and interrupted-run startup scanning,
with verified writer ownership, original budgets and model-health probes. See
[ADR-0011](../decisions/ADR-0011-bounded-supervisor-recovery.md). Resource
enforcement and sampling are implemented in S006e (ADR-0012).

### Runtime supervisor — Simulation (S003a/S006b/S006d/S006e)

Implemented: the CLI supervisor is a separate OS process and the parent of
the runtime; it owns the recorder, deadlines and process-tree termination.
Graceful deadlines are implemented in S006b. S006d implements bounded recovery,
stale-lock verification and model-health probes. `ols recover` is the explicit
startup scan for opted-in interrupted runs; it installs no OS startup task.
S006e implements aggregate Windows job memory/process-count/CPU ceilings,
supervisor workspace quota checks and periodic resource samples. The child
joins the configured job while suspended, before its launcher can spawn.
CPU controls govern cycles; samples measure active time. Disk quota checks can
overshoot during a write; they deny subsequent writing calls and terminate
observed in-flight overshoots. VRAM limits and unsupported platform limits are
refused. Available VRAM is an optional host-level observation. See
[ADR-0012](../decisions/ADR-0012-process-resources-and-sampling.md).
The supervisor does not read the agent's output to decide
anything: a limit is a limit regardless of what the agent says.

```mermaid
stateDiagram-v2
    [*] --> created
    created --> starting
    starting --> running
    running --> paused: operator or limit
    paused --> running
    running --> recovering: runtime crash
    recovering --> running: resumed from checkpoint
    recovering --> failed: unrecoverable
    running --> stopping: deadline or operator
    stopping --> completed: agent loop ended by itself
    stopping --> terminated: stopped by supervisor
    running --> completed
    completed --> [*]
    terminated --> [*]
    failed --> [*]
```

### Observation subsystem — Simulation writes, Window reads (S003a, S004)

Privileged components append [observation events](OBSERVATION.md) to
`events.jsonl` in the run archive. The agent has no handle on this file. A
SQLite index beside it is a rebuildable cache for queries (designed; nothing
writes it yet). Details and the integrity rules are in
[OBSERVATION.md](OBSERVATION.md).

The Window (S004) serves a read-only browser view of the archives: run list,
frozen configuration, paginated timeline, tool call and result pairs,
artifact previews and a live tail. It reads the files directly and keeps only
line offsets in memory; it does not need the SQLite index.

### Experiment manager — Simulation (S003a)

Takes an [experiment configuration](CONTRACTS.md#experiment-config), resolves
and verifies the world release, creates a new `run_id`, a fresh empty
workspace and a run archive containing frozen copies of the configuration and
the world manifest, then hands over to the supervisor. Two runs never share a
workspace or an archive.

## 3. One agent step

```mermaid
sequenceDiagram
    participant Sup as Supervisor
    participant RT as Agent runtime
    participant GW as Model gateway
    participant M as Model server
    participant TH as Tool host
    participant WS as Workspace
    participant Rec as Recorder (run archive)

    Sup->>RT: continue (limits ok)
    RT->>GW: chat(messages, meta-tools)
    GW->>M: completion request
    M-->>GW: text + tool call
    GW->>Rec: model.call
    GW-->>RT: reply
    RT->>Rec: agent.output
    RT->>TH: invoke(capability, arguments)
    TH->>Rec: tool.call
    TH->>TH: validate arguments, check permissions
    TH->>WS: run capability in sandbox
    WS-->>TH: result
    TH->>Rec: tool.result
    TH-->>RT: result
    Sup->>WS: scan for file changes
    Sup->>Rec: artifact.created (+ copy bytes into archive)
    RT->>RT: persist conversation state
```

## 4. Trust boundaries

```mermaid
flowchart TB
    subgraph host["Host (privileged, never agent-writable)"]
        repos["Three source checkouts"]
        supervisor["Supervisor, recorder, experiment manager"]
        archive[("Run archives")]
        releases[("World releases")]
        creds["Credentials, user files"]
    end
    subgraph mediated["Mediated zone (runs agent-chosen calls, not agent-written code)"]
        runtime["Agent runtime"]
        toolhost["Tool host"]
        gateway["Model gateway"]
    end
    subgraph sandbox["Sandbox (agent-writable)"]
        workspace[("Workspace")]
        agenttools["Agent-created tools (S009)"]
    end
    supervisor -- "controls" --> mediated
    mediated -- "validated calls only" --> sandbox
    releases -. "read only" .-> mediated
    mediated -- "events" --> archive
```

The agent is a model emitting text. Its only effects on the world are tool
calls that the tool host chooses to execute. The strength of the sandbox
around those executions is the isolation tier
([ADR-0006](../decisions/ADR-0006-isolation.md)).

## 5. Failure modes

| Failure | Detected by | Response |
| --- | --- | --- |
| Model server crash or hang | Gateway timeout | Retry with backoff; `error` event; after N failures supervisor pauses the run |
| GPU out of memory | Gateway load error | Unload other models, retry once, fail the call |
| Runtime process crash | Supervisor (child exit) | `recovery` event; restart from last checkpoint |
| Host reboot or power loss | Supervisor on next start | Run marked `recovering`; resume from last checkpoint; downtime excluded from elapsed time |
| Capability hangs | Tool host timeout | Kill the sandboxed process; `tool.result` with `timeout` |
| Agent fills the disk | Supervisor quota check | `supervisor.action: limit_enforced`; writes denied |
| Event log write fails | Recorder | Run is stopped: an unobserved run has no experimental value |
| World digest mismatch | Experiment manager | Launch refused |
| Deadline reached | Supervisor clock | Checkpoint (if configured), then kill; never negotiable |

## 6. Technology choices

Summarised here; reasoning and alternatives are in the
[decision records](../decisions/README.md).

| Concern | Choice |
| --- | --- |
| Language | Python 3.12, `uv`, minimal dependencies |
| Contracts | JSON Schema draft 2020-12, semantic versioning |
| Capability interface | Transport-neutral manifest; MCP is one projection |
| Orchestration | Small custom loop over chat-completions tool calling |
| Model serving | Ollama first, behind a provider-neutral gateway |
| Isolation | Two tiers: supervised process now, container before agent-written code |
| Durable state | Append-only JSONL as the record; SQLite for indexes and memory |
| Inter-component communication | Files under the data root; read-only local HTTP for the Window |
| Window front end | Standard-library HTTP server, JSON API, static HTML and JavaScript with no build step (ADR-0008) |
