# ADR-0014: Rootless Podman in WSL 2 as the container mechanism

Status: Accepted (2026-11-14, human-approved). Resolves OD-1; refines ADR-0006.
No container backend is implemented yet; that is S006c.

## Context

ADR-0006 defined the `container` isolation tier and preferred rootless Podman
inside a repaired WSL 2, deferring the choice until WSL worked and could be
tested. Through S006e, `wsl.exe` failed ("class not registered") or timed out
and no container engine was installed (KI-1).

On 2026-11-14 the human repaired WSL themselves (re-registered Windows
Installer, then updated WSL to 3.0.5), installed an Ubuntu distribution on
WSL 2 and installed Podman from the distribution's packages. No agent made
these system changes.

## Decision

The `container` tier uses **rootless Podman inside the WSL 2 Ubuntu
distribution**, driven by the Simulation supervisor. Docker Desktop and the
other ADR-0006 alternatives are not pursued.

Read-only checks run from the Builder session after installation found:

| Item | Observed |
| --- | --- |
| WSL | 3.0.5, distribution on version 2, `wsl --status` responds |
| Podman | 5.7.0, rootless |
| cgroups | v2 |
| OCI runtime / storage / network backend | `crun` / `overlay` / `netavark` |
| Smoke test | `hello-world` image ran with `--network=none` |

## What this does not establish

This is a working engine, not evidence of isolation. Configuration alone
proves nothing: S006c must still demonstrate, on this backend, that host
files, the repositories and run archives are unreachable, that networking is
denied by default, and that memory/CPU/process/disk limits and supervisor
shutdown with descendant cleanup hold. Until S006c passes, nothing may run on
the container tier.

## Consequences

- The human gate on S006c is removed. B-ISOLATION remains as an engineering
  blocker for S008d, S009 and S011–S012 until S006c is complete.
- Podman warned that `/` inside the distribution is a private, not shared,
  mount. Rootless bind-mount propagation must be checked in S006c; making `/`
  shared would be a system change needing the human.
- Workspace mounts cross the Windows/WSL boundary (`/mnt/<drive>` 9P paths),
  which is slow and has different permission semantics. S006c decides whether
  workspaces are copied into the WSL filesystem or bind-mounted, and tests it.
- Container images come from public registries only as the human authorises;
  S006c builds a world-derived image rather than pulling arbitrary ones.
- WSL 2 reserves memory from the 16 GB host; S006c measures what remains for
  model servers that stay on the host.
- The host runs a pre-release Windows build (KI-4); a WSL regression after a
  Windows update is possible and would re-block the tier.
