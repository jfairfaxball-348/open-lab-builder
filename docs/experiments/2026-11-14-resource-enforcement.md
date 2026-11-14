# S006e engineering check: resource enforcement and sampling

Date: 2026-11-14. Engineering checks with scripted/fake models only. No model,
driver, container engine or system software was downloaded or installed. No
system setting, OS startup task, real reboot or Linux environment was changed.

## Delivered scope

Aggregate Windows Job Object RAM/process-count/CPU ceilings; suspended startup
before job assignment/child creation; supervisor workspace quota admission and
in-flight checks; periodic supervisor resource samples including available host
NVIDIA VRAM when measurable. Unsupported limits are explicitly refused. Limits
are reinstalled on resume. Existing schemas, world source and copied fixture
are unchanged; no dependency added. ADR-0012 defines the exact semantics.

The split S006b/S006d/S006e supervisor scope is now implemented and tested within
the documented process-tier limits. This does not deliver container isolation.

## Automated validation

Baseline Builder `uv sync`, `uv run olb state`, `uv run olb check --tests`:
305 tests and all six health checks passed. Baseline Simulation `uv sync` and
`uv run pytest`: 188 tests passed in 123.15 seconds.

Final Simulation `uv run ruff check .; uv run pytest`: lint passed; 214 tests
passed in 140.28 seconds, including 26 resource tests. A focused run of resource
and continuation tests passed 27 tests. Builder `uv run ruff check .; uv run olb check --tests` passed: 305 tests
in 64.61 seconds and all six health checks. Privacy and whitespace checks
passed in both repositories. Simulation committed and pushed as `830379c`.

Native tests cover a fixed allocating capability denied by the aggregate memory
ceiling then killed/recorded; a capability launch blocked by process count;
CPU hard-cap configuration and measured throttling; suspended creation before
successful job assignment and thread resume; writing tool/demonstration denial
at quota while reads remain available; live writer overshoot termination;
no automatic recovery after resource termination; reinstallation after checkpoint
resume; backend setup failure; fail-closed quota monitoring; unsupported and
overflowing limits; invalid cadence; unavailable and measured-zero GPU values;
GPU query absence/timeout; periodic samples and supervisor-only event ownership.
All native faults use fixed test-only capability code, never agent-supplied code.

The first full run found the existing continuation test's exact global event
sequence did not allow new periodic resource samples. It was updated to retain
the exact conversation/enforcement sequence, add supervisor/observed telemetry
checks, and require that only resource samples can interleave between a reply
and its explicitly linked continuation. No conversation assertion was removed
and no failing test was skipped. Initial quota fixtures also exceeded the
shipped tool's input-text maximum; they were replaced by a fixed test-only
one-MiB writer so the quota path is actually exercised.

## Independent native checks

- Shipped CLI example `experiments/scripted-resources.json`:
  `run-20261114t115404z-96a2a1` completed in 0.922 active seconds, 27 events,
  five resource samples, three successful tools. All four configured limits
  were installed. CLI and separate `ols verify` exited zero.
- Shipped capabilities with a local-only quota configuration:
  `run-20261114t115011z-113b13` completed in 0.969 active seconds, 49 events,
  five samples. Five writes succeeded, the sixth was denied, then workspace
  listing succeeded. Its independent CLI verification passed. The completed
  fifth write left 1.1444 MiB, demonstrating the documented polling/admission
  overshoot instead of pretending an OS byte quota exists.
- The quota archive's final sample recorded GPU used 0 MiB and available 4096
  MiB, with aggregate host scope and measurement age. Missing GPU measurements
  are tested separately and never represented by numeric zero.
- Independent kernel query confirmed CPU control flags 5 (ENABLE | HARD_CAP)
  and rate 125/10000 for nominal 0.2 cores on 16 logical processors. A two-second
  busy-loop measurement reported 30.46875 percent active CPU. This proves
  throttling on this machine, not an exact 20-percent active-time bound: CPU
  cycle caps and short-window active-time accounting are distinct measures.

Raw command output, quota configuration and sanitized numeric evidence remain
ignored under Simulation `.local/s006e/`. Run archives/workspaces remain outside
version control. No generated large configuration or raw diagnostic is committed.

## Remaining limits and exact next milestone

Next: **S007a — Model Gateway**. A read-only `wsl.exe --status` check timed out
after ten seconds, and neither Podman nor Docker is available. The human-gated
S006c container milestone remains blocked; no repair or workaround was attempted.

Disk quota checks can overshoot while a capability writes. They deny future
writing calls and kill an observed live writer above quota; they do not limit
archive/model storage. CPU caps constrain cycles through the Windows scheduler,
not an exact short-window CPU-time theorem. Windows memory/process notifications
are best effort; OS ceilings remain in effect without guaranteeing a complete
notification record. VRAM limits and non-Windows CPU/RAM/process limits are
refused. GPU data describes the host, not run-attributable memory. Physical
reboot/power loss, Linux execution and uninterruptible/large-run host-I/O timing
remain unverified. The supervisor/model server are outside the runtime job.
