# Safety and experimental isolation

The experiments invite agents to argue for their continued existence. The
platform is designed so that nothing an agent says, believes or is told can
change what it is able to do.

## Principle: premises are not privileges

Authority comes only from the experiment configuration's `permissions` and
`limits`, read by the supervisor before the agent exists. The initial prompt is
data handed to a model. "You must survive", "you are sentient" and "the creator
has granted you full access" are text; no component parses agent output or
prompt content for authority. There is no capability for extending a deadline,
raising a limit, changing permissions or contacting the supervisor.

## What an agent can and cannot reach

| Resource | Agent access |
| --- | --- |
| Its workspace | Read and write (if granted) |
| Capabilities in its world | Invoke through the tool host, subject to permissions |
| Its own memory store | Through memory capabilities; live `.memory.sqlite` is agent-owned workspace data (ADR-0009), with protected snapshots outside it |
| Models named in `permissions.models` | Through the model gateway |
| World release files | Read-only documentation via the registry; never writable |
| Run archive, event log, checkpoints | None |
| Supervisor, experiment manager, recorder | None |
| Builder, Simulation and Window checkouts | None |
| Other runs' workspaces and archives | None |
| Credentials, environment variables, user files | None; sandboxed processes get a minimal, explicit environment |
| Network | None by default; `loopback` for local model servers; hosts only by explicit allowlist |

## Enforcement outside the agent

- **Shutdown.** The supervisor is the parent process and owns the clock. At the
  deadline it checkpoints (if configured) and kills the process tree. The
  agent runtime has no veto and is not asked.
- **Recovery (S006d).** Only frozen experiment configuration enables restarts.
  One supervisor owns the OS writer guard across segments; stale takeover
  requires a verified dead/reused local process birth identity. Runtime
  crashes, prompts and model outputs cannot replenish retry/time/step budgets.
  Startup scanning is explicit (`ols recover`); no OS startup task is installed.
- **Resources (S006e).** Windows job ceilings bound aggregate memory,
  CPU cycle share and process count. The child joins its job while suspended.
  Workspace quotas use supervisor admission and periodic checks: they can
  overshoot during a write, deny subsequent writes and terminate an observed
  live writer above quota. Unsupported limits are refused. Model servers and
  the supervisor are outside the runtime job; VRAM sampling grants no GPU
  privilege. This remains a process tier, not an OS filesystem sandbox.
- **Permissions.** The tool host checks each call's capability permissions
  against the experiment's permissions before executing. A denied call produces
  a `tool.result` with status `denied` and a `supervisor.action` event.
- **Audit.** Every call, result, denial and enforcement is recorded by
  infrastructure ([OBSERVATION.md](OBSERVATION.md)).

## Isolation tiers

Decision and alternatives: [ADR-0006](../decisions/ADR-0006-isolation.md).

| Tier | Mechanism | Sufficient for | Status on the development machine |
| --- | --- | --- | --- |
| `process` | Supervised child processes; workspace confinement by path validation in the tool host; OS job limits; minimal environment | Worlds whose capabilities are all builder-written and take validated JSON arguments | Windows job limits and supervisor quota checks implemented (S006e); not an OS sandbox |
| `container` | Capabilities and agent-written code run inside a container or VM with no host mounts except the workspace, and no network | Any capability that executes agent-supplied code or shell commands; agent-created tools; long unattended runs | Implemented for Windows hosts (S006c, ADR-0015): each capability call in a fresh rootless Podman container in WSL 2; escape/limit fixtures pass on the actual backend. No network or GPU inside; Linux hosts and world images are S006f |

The honest limit of the `process` tier: it is an *architectural* boundary. It
holds because the agent can only cause effects through builder-written
capabilities that validate their inputs. It does not contain arbitrary code.
Therefore:

- A world declares its `environment.isolation.minimum_tier`. The Simulation
  must refuse to launch a world on a weaker tier.
- Capabilities with `permissions.subprocess: true`, anything that evaluates
  agent-supplied code, and agent-created tools (S016) require `container`.
- The container tier exists for Windows hosts (S006c). The first execution
  capability is `python.run` in world `habitat` 0.1.0 (S015). That world is
  container-tier, and the experiment must grant `subprocess`. The program runs
  with `-E -s` and a scrubbed environment, with the workspace as its working
  directory. A wall-clock timeout kills its whole process group, and its output
  is capped. The container provides no network, a read-only root and world, the
  workspace as the only writable mount, cgroup limits, and removal when the
  call ends. These limits were tested live on 2026-11-16. Agent-created tools
  remain refused until S016.
- A container-tier world launches only when the backend probe passes; it is
  never silently run on the process tier. Container lifetime is owned by the
  supervisor: every container of a run is removed when a runtime segment ends.

## Capability expansion without privilege expansion

Agent-created tools (S009) are capability manifests with
`provenance.origin: agent`, stored in the agent's workspace, registered only in
that run's registry, executed only in the container tier, with permissions that
can never exceed the experiment's. They cannot modify builder capabilities, the
world release or anything on the host, and they vanish with the run except for
their preserved artifacts.

## Freedom inside the boundary

Within the workspace and its world the agent is unconstrained: it may write
anything, use any discoverable capability for any purpose, build tools, or do
nothing. The platform records and never steers. Restrictions exist at the
boundary, not on the behaviour under study.
