# S006c engineering check: container capability tier

Date: 2026-11-14. Engineering checks with scripted models only; no model was
called. The human repaired WSL 2, installed Ubuntu and Podman (ADR-0014) and
authorised one image pull in this session: `docker.io/library/python:3.12-slim`,
pinned as digest `sha256:05a994d2344eb364cc186910f4fc8786a38215f39f00d0acc25bff33a08f4177`
(about 124 MB unpacked). Nothing else was downloaded or installed and no system
setting was changed.

## Backend facts observed

Podman 5.7.0, rootless, cgroups v2 with `cpu`, `memory`, `pids` delegated
(systemd user session), `crun`, `overlay`, `netavark`; WSL 3.0.5. Container
start through `wsl.exe` measured about 0.5 s without stdin and 0.3–2 s per
capability call. `wsl.exe --` passes arguments through a shell (backslashes
lost); `--exec` does not. Killing `wsl.exe` left a running container in place.
Links made in a container on the Windows workspace appear as WSL reparse points
(`0xa000001d`) that Windows cannot open and Python does not report as links.

## Delivered scope

See ADR-0015. Simulation commit `bc51964`: `container.py` backend, tool-host
sandbox, launch gating/probe, supervisor sweep on every stop path,
`isolation.json`, and reparse-point-aware workspace walks.

## Automated validation

Simulation `uv run ruff check .` passed. `OPEN_LAB_REQUIRE_CONTAINER=1 uv run
pytest`: 237 tests passed in 200 s (214 existing, 23 new). Afterwards no
container with the run label remained.

The 23 container tests:

- Without a backend: the command vector denies network, capabilities,
  privilege gain, pulls and writable root and pins the image; workspace mount
  follows the filesystem permission; limit defaults and unusable values;
  container worlds refused when the probe fails (no archive created) or when a
  capability needs network; `subprocess` permission only on the container tier.
- On the actual backend (fixed escape snippets executed by a test capability
  standing in for agent code): the repositories, their parent, a run archive,
  the test data root and the user's home are absent inside, `/mnt` and `/home`
  are empty and the only host mounts are `/world` and `/workspace`; only `lo`
  exists and connections to internet, loopback model port and WSL/host
  addresses and DNS all fail; uid non-zero, all capability sets zero,
  `NoNewPrivs` 1, `setuid(0)` and `mount` refused; writes succeed only in
  `/workspace` and `/tmp`; a written script and a PE file cannot be executed
  from either; the environment contains no host variables; cgroup files show
  the configured memory/swap/pids/CPU ceilings; process spawning stops below
  the pids ceiling; allocation past memory is killed (exit 137) and the
  container is gone; two busy processes stay within the CPU quota; `/tmp`
  stops at 64 MB (ENOSPC); a timed-out call returns `timeout` and leaves no
  container; a detached descendant ends with the call; links made inside are
  recognised and not followed by the scanner, quota or checkpoint snapshot.
- Whole supervised runs: a container-tier world runs `text.stats`,
  `math.evaluate` (subprocess interface), `memory.write`/`memory.search`
  (SQLite on the mounted workspace), `workspace.write` and a test capability,
  completes, verifies, records `isolation.json` and leaves no container; a
  deadline during a long call terminates the run, records the container
  cleanup and leaves none; a quota stop of a containerised writer leaves none
  and the file stops growing.

**Negative control.** Removing `--network=none`, `--read-only`,
`--cap-drop=ALL` and the `noexec` mount option made the command, network,
privilege/write and exec tests fail; the protections were restored before the
final run.

## What this does not establish

No shipped capability executes agent-supplied code; that is S008d. No
behavioural run occurred. Linux hosts, world-declared images, GPU and any
container network are untested (S006f). Kernel/WSL escapes beyond these
fixtures, and side channels, are out of scope. Aggregate limits are the
runtime job plus one container, not a single combined ceiling.
