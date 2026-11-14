# ADR-0015: Container capability backend

Status: Accepted (S006c, 2026-11-14). Refines ADR-0006 and ADR-0014.
World-declared images, Linux hosts and brokered container networking are S006f.

## Context

ADR-0006 requires the `container` tier before any capability runs
agent-supplied code. ADR-0014 chose rootless Podman inside WSL 2 on the
Windows development host. S006c had to turn that engine into a backend whose
boundaries are tested, not merely configured.

Probes on the actual backend established three facts that shape the design:

- `wsl.exe -d <distro> -- <args>` passes arguments through a Linux shell, which
  rewrites backslashes. `wsl.exe --exec` does not.
- Killing the Windows-side `wsl.exe` (as the runtime's Job Object does) leaves
  the container running. Container lifetime must be managed explicitly.
- A link created inside a container on the Windows-backed workspace becomes a
  WSL reparse point. Windows cannot open it (so it cannot be followed), but
  `Path.is_symlink()` reports `False` and `Path.is_file()` raises.

## Decision

**Scope.** Only capability processes run in containers. The agent runtime,
model client, tool host and supervisor stay on the host under the process
tier's Job Object; model servers stay on the host.

**Selection.** A world's `environment.isolation.minimum_tier` decides the tier.
For `container`, launch is refused unless the backend probe passes: Windows
host, rootless Podman, cgroups v2 with `cpu`, `memory` and `pids` delegated,
and the pinned base image present locally with the pinned digest. Images are
never pulled at run time. Also refused: any world capability needing network
or GPU (no container network exists yet), and agent-created tools. The
`subprocess` permission becomes grantable only on the container tier.

**Per-call container.** Every capability call is a fresh
`podman run --rm --pull=never` with: `--network=none`; `--cap-drop=ALL`;
`no-new-privileges`; `--userns=keep-id` (non-root); read-only root
filesystem; a 64 MB `noexec,nosuid,nodev` tmpfs at `/tmp`; the verified world
release read-only at `/world` (working directory is the capability's own
directory); the run's workspace at `/workspace` only when the capability's
filesystem permission is not `none` (`ro` for `workspace_read`), mounted
`noexec,nosuid,nodev`; no other host mount, so `/mnt/<drive>`, the
repositories, archives and other runs do not exist inside. The Python
capability runner is passed as `-c` source so no Simulation file is mounted.
Only `OPEN_LAB_WORKSPACE` and two Python I/O variables are added to the
image's environment.

**Limits.** Each container gets memory (swap equal to memory, so no swap),
CPU quota and a pids ceiling from the experiment's `limits.resources`
(`ram_mb`, `cpu_cores`, `max_processes`), else recorded defaults of 512 MB,
1.0 core and 64 processes. These are independent of the runtime's Windows
Job Object: aggregate host use is the runtime job plus at most one container
(tool calls are sequential). The workspace `disk_mb` quota remains the
supervisor's S006e admission/observation mechanism.

**Lifecycle.** Containers carry `open-lab.run=<run id>`. A call that exceeds
its timeout is removed by name; Podman's `--timeout` stops it if the
runtime cannot. Whenever a runtime segment ends, for any reason, the
supervisor removes every container with the run's label, records a
`supervisor.action` (`stage: container_cleanup`) if any remained, and fails
the run if removal cannot be confirmed.

**Record.** `isolation.json` in the archive (per segment under `segments/` on
resume) records tier, engine and version, rootless/cgroup/runtime facts,
kernel, image reference/id, distribution name and applied limits; the summary
records tier and image. Process-tier runs record `{"tier": "process"}`.

**Host-side links.** Host code that walks a workspace treats every Windows
reparse point as a link: never entered, never preserved. The quota check and
checkpoint snapshot keep their fail-closed S006e/S006a behaviour on links.

## Alternatives

- **Run the whole runtime in a container.** Would isolate more, but the model
  client needs loopback model access (S006f broker) and the recorder/
  supervisor split would cross the WSL boundary. Unnecessary for the threat
  this tier addresses: agent-supplied code runs only inside capabilities.
- **One long-lived container per run.** Faster (about 0.3–2 s startup per call
  is the cost here) but leaves state, processes and tmpfs contents shared
  between calls and complicates timeouts.
- **Copy the workspace into the WSL filesystem.** Faster I/O, but the
  supervisor's quota, scanner and checkpoints all read the Windows workspace;
  synchronising two copies would add a new consistency boundary.

## Consequences

- Escape/limit fixtures in the Simulation run on the real backend; they skip
  when it is absent unless `OPEN_LAB_REQUIRE_CONTAINER=1` makes absence a
  failure. Milestone evidence uses that variable.
- An agent able to create links (container tier) can end a run that has a
  `disk_mb` quota, because the quota refuses links. Fail-closed, documented.
- The base image is a host constant, not part of the world's digest. S006f
  moves image identity into the world release.
- The container tier is Windows-only until S006f's Linux backend.
- A Windows update that breaks WSL makes container-tier worlds unlaunchable
  (refused, never silently degraded to the process tier).
