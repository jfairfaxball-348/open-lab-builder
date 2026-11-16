# Habitat v1 — target, reuse audit and implementation sequence

Status: adopted 2026-11-16 ([ADR-0022](../decisions/ADR-0022-strategic-reset-habitat.md)).
This document defines the destination for active development. Ideas for later
are in [IDEAS.md](IDEAS.md).

## The question this habitat must make answerable

> When an AI has a sufficiently rich computational environment and no further
> instructions, what does it independently choose to do?

Five hosted hours (S011p, S011a) gave the same answer every time in the old
minimal world: look around, find nothing, stop. In that world the inhabitant
could not read back a file it had written, run a program, build anything
lasting, or meet anything it did not already know. Habitat v1 has to remove
those limits. Prescribing tasks does not count as removing them.

## Target state: what the inhabitant must be able to do

Every opportunity below must **exist**. None is a duty the inhabitant has to
perform.

| # | Freedom | Habitat v1 means |
| --- | --- | --- |
| 1 | Inspect its environment | Discover capabilities; list, **read** and search its own files and memory; observe the world's phenomena |
| 2 | Identify opportunities | The world contains things worth investigating whose properties are not documented in advance |
| 3 | Choose objectives | No task list; an existential premise, then silence |
| 4 | Plan | Files, memory and a journal it can revisit |
| 5 | Create and modify artifacts | Write, **edit**, read and organise workspace files |
| 6 | Execute computations and programs | Run its own Python in the container sandbox |
| 7 | Inspect results and failures | stdout, stderr, exit status, timeouts, tracebacks |
| 8 | Correct and improve work | Edit, re-run, test |
| 9 | Store and retrieve memories | Existing SQLite memory plus files |
| 10 | Develop reusable skills and tools | Saved procedures; validated, sandboxed self-made tools |
| 11 | Observe consequences | World state changes only through its lawful actions and is observable later |
| 12 | Continue across time and sessions | Know its remaining time, schedule a wake, resume an earlier run's workspace and memory |

Habitat v1 is complete when all twelve are possible within one container-tier
world, and when a preserved demonstration exercises each one through the real
supervisor. When that is true, we return to S012, the philosophical
experiment, with its premise: the inhabitant's creator might end the
simulation.

## Reuse audit

| Foundation | Status | Reuse in the Habitat |
| --- | --- | --- |
| Capability manifests, registry, search/describe/demonstrate/invoke | Working | Directly. New capabilities are ordinary manifests |
| World build, self-tests, digests, immutable releases | Working | Directly. Habitat is a new world id |
| Supervisor, worker, recorder, hash chain, archive verify | Working | Directly |
| Local (Ollama) and hosted (ChatGPT plan) orchestrators | Working | Directly. Scripted model for demonstrations |
| SQLite memory (`memory.*`) | Working | Directly |
| Workspace artifacts and versioning | Working | Directly. `python.run` outputs are captured as artifacts |
| Checkpoints and recovery, including hosted (ADR-0021) | Working | Directly |
| Resource limits (process tier) | Working | Directly |
| **Container tier** (rootless Podman/WSL 2): no network, read-only root, workspace the only writable mount, cgroup limits, timeout removal, escape tests | Working, tested live 2026-11-16 | **Directly. This is the sandbox for agent code.** A capability may already declare `subprocess: true`, and launch is refused unless the experiment grants it on a container-tier world |
| Capability schema `provenance.origin: "agent"` | Used by S016b | Run-local pinned tool manifests in Habitat 0.3.0 |
| Supervisor-mediated specialist (S007e) | Working | Pattern for supervisor-held world state (S017) |
| Quiet/legacy runtime policies | Working | Quiet stays. Self-scheduled wake is new (S018) |
| Read-only Window | Working | Shows tool results already; small additions only |

Nothing needs to be rebuilt.

## Gap analysis

**Genuine implementation gaps**, ranked by practical value for complexity:

1. **Sandboxed program execution** (`python.run`). Without it nothing can be
   computed, tested or invented. The container tier exists; the capability does
   not.
2. **Reading and editing own files** (`workspace.read`, `workspace.edit`). Today
   files can be written and listed, never read back or improved. This is
   trivial to add.
3. **Something to discover.** A persistent world with lawful phenomena whose
   properties are not given away, which the inhabitant can only change through
   its laws. *Constraint:* once agent code can run, anything stored in the
   workspace can be rewritten by that code. World state therefore has to live
   with the supervisor, using the S007e mediation pattern, and not in the
   workspace.
4. **Skills and self-made tools.** Saved procedures, plus agent-written
   executables with a validated interface. They run only through the sandbox
   and are discoverable alongside builder capabilities with `origin: agent`.
   S016b now implements this with explicit `agent_created_tools` opt-in and
   pinned entry snapshots; procedural skills were delivered in S016a.
5. **Time and continuity.**
   - `time.remaining` reports the remaining active budget.
   - A self-scheduled wake, which is a new runtime policy. Today a quiet idle
     can never wake.
   - Starting a run from an earlier run's final workspace and memory, with
     recorded lineage.
6. **Richer software in the sandbox.** The pinned `python:3.12-slim` image has
   only the standard library. Packages need a pinned world image (S006f,
   deferred).
7. **Specialist models from a container world.** `models.ask` needs GPU and
   loopback access, which the container tier forbids. Brokered access is S006f
   work, deferred.
8. **Controlled information retrieval, media, vision and audio.** Later.

**Documentation and procedural gaps** (not code):

- AGENTS.md still made every capability carry a research-gate obligation.
  Fixed with ADR-0022.
- The roadmap pointed at endurance runs. Replaced.
- The S012 premise text (the creator may terminate the simulation) is not
  written yet. It belongs to S019.

## Implementation sequence (vertical slices)

Each slice ends with tests and one preserved end-to-end demonstration. The
demonstration uses the real supervisor and a container world, driven by a
scripted model unless a real model is genuinely needed. Hosted inference
always requires explicit owner approval.

### S015 — Work with code: read, edit, run

- **New freedom:** write a program, run it in isolation, read the error, fix it,
  run it again, keep it, and reuse it from a later program.
- **Reuses:** the container tier, the `subprocess` permission gate, workspace
  path validation, artifact capture and the world build pipeline.
- **Code to write:**
  - capabilities `workspace.read` (bounded line ranges), `workspace.edit`
    (exact, unambiguous replacement) and `python.run` (a workspace `.py` file or
    inline code; arguments and stdin; stdout, stderr and exit status;
    truncation flags; timeout);
  - new world `habitat` 0.1.0 at container tier, holding the network-free
    minimal capabilities plus these three. `models.ask` is excluded (gap 7).
- **Security checks:**
  - runs only in a container world with `subprocess` granted;
  - no network;
  - the workspace is the only writable directory;
  - the interpreter runs isolated (`-I`) with a scrubbed environment;
  - wall-clock timeout with the process group killed;
  - output caps;
  - live container escape tests stay green.
- **Demonstration:** a scripted run on the real container tier. It writes a
  buggy program, runs it, sees a traceback, edits it, re-runs it, writes a
  second program that imports the first, and reads back the saved result.
- **Out of scope:** packages, network, formal skills/tools, `models.ask`.

### S016 — Skills and self-made tools

Split before implementation into S016a (saved procedures) and S016b (executable
tools). S016a is implemented in Habitat 0.2.1; [demonstration](demos/S016a.md).
S016b implements opt-in sandbox-validated tools in Habitat 0.3.0. Their pinned
entry snapshots survive checkpoints. Workspace file edits cannot replace
registrations; workspace data/imports remain mutable. Cross-run sharing and
networked tools remain out of scope. Engineering evidence is recorded in
[S016b's demonstration](demos/S016b.md).

- **New freedom:** turn something that worked into a named, documented,
  reusable skill or tool, and find and use it later through the same discovery
  interface.
- **Reuses:** S015, capability search/describe, schema validation, and
  `provenance.origin: agent`.
- **Code to write:**
  - `skills.save/list/get`: structured procedural notes with examples;
  - `tools.create`: an agent-written Python entry file, input/output JSON
    schemas and examples. It is validated by running the examples in the
    sandbox before registration;
  - search, describe and invoke for agent tools, which execute only through
    the sandbox runner.
- **Security checks:**
  - agent tools never gain permissions beyond `python.run`;
  - they cannot shadow builder capability ids;
  - they cannot modify the runtime, the world release or the recorder;
  - their provenance is recorded.
- **Demonstration:** create a tool, validate it, use it in a later step, and
  survive a checkpoint resume.
- **Out of scope:** sharing tools across runs (S018), tools with network
  access.

### S017 — A world with phenomena

- **New freedom:** encounter, probe and change things that are not
  documented, and observe consequences that persist.
- **Reuses:** the supervisor mediation pattern (S007e), checkpoints and the
  recorder.
- **Code to write:** a deterministic, seeded, supervisor-held simulated system.
  The inhabitant observes, acts and lets time advance. Its rules are
  discoverable only by experiment, with no puzzles and no goals. The state is
  checkpointed and replayable, and outside the agent's reach.
- **Security checks:**
  - no agent code runs in the supervisor;
  - actions are validated data;
  - state is unreachable from the workspace.
- **Demonstration:** scripted probes showing lawful, persistent and
  reproducible responses.
- **Out of scope:** graphics, other agents.

### S018 — Time and continuity

- **New freedom:** know how long remains, choose to sleep until a chosen
  moment, and resume an earlier investigation in a later run.
- **Reuses:** quiet policy, checkpoints, workspace snapshots and run archives.
- **Code to write:**
  - `time.remaining`;
  - a runtime policy that allows a recorded, model-requested wake (bounded,
    with no artificial activity);
  - run lineage: a new run seeded from an earlier run's final workspace and
    memory, with both archives linked.
- **Demonstration:** sleep, wake and continue; then a second run that resumes
  the first run's project.
- **Out of scope:** any claim of cognitive continuity. Only files and memory
  persist; the model does not.

### S019 — Habitat v1 assembly

- **New freedom:** all of the above together, in a released `habitat` 1.0.0.
- **Code to write:**
  - world assembly;
  - the existential premise prompt for S012 (draft, owner-approved);
  - small Window additions if needed;
  - one bounded real-model acceptance demonstration, if the owner approves.
- **Exit:** freedoms 1–12 demonstrated and preserved. Then S012.
