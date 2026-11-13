# ADR-0006: Two isolation tiers

Status: Accepted (S001). The container mechanism is an open decision.

## Context

The agent must not be able to reach the host, the three repositories, the run
archive or other runs. The audit of the development machine found:

- Windows 11 Home. No Docker, no Podman.
- `wsl.exe` exists but WSL is **not functional** (it fails with a "class not
  registered" error). The Virtual Machine Platform feature is enabled and a
  hypervisor is present, so WSL 2 can probably be repaired.
- Windows Sandbox and Hyper-V management are not available on Home edition.

Repairing WSL or installing a container engine is a system-wide change needing
administrator rights, which S001 was told not to make.

## Decision

Define isolation as a pluggable backend with two tiers. A world release
declares the minimum tier it needs, and the Simulation refuses to launch a
world on a weaker tier.

**Tier `process` (buildable now, S003a/S006b).** The supervisor starts the
runtime and each capability as child processes with: a Windows Job Object (or
cgroup/rlimits on Linux) limiting memory, process count and CPU, and killing
the whole tree when the supervisor exits; a minimal explicit environment with
no inherited secrets; the workspace as working directory. Confinement to the
workspace is enforced by the tool host validating every path argument, because
the agent can act only through builder-written capabilities. This tier does
**not** contain arbitrary code and must not be used to run it.

**Tier `container` (S006c).** Capabilities and agent-written code run in a
container or lightweight VM with only the workspace mounted and networking
off. Required for any capability with `subprocess: true`, anything that
executes agent-supplied code or shell, and all agent-created tools.

Preferred container mechanism: Podman (rootless, daemonless) inside a repaired
WSL 2. This choice is deferred until WSL is working and can be tested.

## Alternatives

- **Require containers from the start.** Cleanest security story, but blocks
  all runtime work on a host change that needs a human.
- **Process tier only, forever.** Would cap the project below its goals
  (agent-created tools, scripting capabilities).
- **Windows restricted tokens / AppContainer / low-integrity processes.** A
  real OS boundary without virtualisation, but intricate, Windows-only, and
  easy to get subtly wrong. Could harden the process tier later.
- **A dedicated low-privilege Windows user account.** Simple filesystem
  separation; needs administrator setup and does not limit network access.
- **Full VM per run (Hyper-V, VirtualBox).** Strongest isolation; Hyper-V
  tooling is unavailable on Home, and per-run VMs are heavy for 16 GB of RAM.
- **Docker Desktop.** Works on Home via WSL 2, but a heavier, licensed daemon;
  Podman is preferred. Either satisfies the tier.

## Consequences

- S002–S006b can proceed with deterministic, builder-written capabilities.
- A human must repair WSL (or approve another mechanism) before S006c, which
  gates S008d and S009. Tracked as a human action in `state.json`.
- GPU access from inside a container needs separate validation; model servers
  stay on the host and are reached over loopback, so capabilities themselves
  rarely need the GPU inside the sandbox.
