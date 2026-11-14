# ADR-0012: Process-tier resource enforcement and sampling

Status: Accepted (S006e). Completes the split S006b/S006d/S006e supervisor scope;
extends ADR-0006 and ADR-0011 without adding container isolation.

## Context

Limits must be enforced outside the runtime, and observations must distinguish
unavailable measurements from measured zero. On Windows a venv redirector can
spawn another Python process: assigning a live redirector to a job is too late
to guarantee that child is included. Model servers run outside the runtime tree,
so the supervisor cannot honestly claim to cap their VRAM through that job.

## Decision

- Experiment `limits.resources` supports aggregate Windows job `ram_mb`,
  `max_processes`, `cpu_cores`, and supervisor workspace `disk_mb`. MiB means
  1024 squared bytes. Shared schemas and release 0.6.0 are unchanged. No new
  dependency or system software is installed.
- A child is created with CREATE_SUSPENDED, assigned to the configured Job
  Object, then its primary thread is resumed through documented thread APIs.
  Kill-on-job-close remains enabled. Descendant launchers/capabilities inherit
  the job; a launch/setup failure stops before agent work rather than falling
  back to an unbounded process. Resources are reinstalled on every segment.
- RAM uses the job-wide committed-memory limit; process count is the active
  process ceiling including launchers. CPU uses ENABLE | HARD_CAP with rate
  `floor(cpu_cores * 10000 / logical_processors)`. Rates outside 1–10000,
  integer overflows, and CPU caps on hosts above 64 logical processors are
  refused. CPU control governs cycles; sampled active CPU time is not an exact
  short-window equivalence to that nominal core budget. Applied rates are
  recorded. CPU throttling itself is an OS action, not inferred from output.
- Job completion-port memory/process-count notifications cause tree termination
  and `supervisor.action`. Notification delivery is best effort under Windows;
  absence of a notification is not evidence of absence of a denied allocation
  or process launch. The configured OS ceilings remain effective independently.
  Limit installation is always recorded. Enforcement terminations are not
  automatically retried by S006d.
- Workspace disk admission is decided by the supervisor before acknowledging a
  writing `tool.call`, including demonstrations. A denial is returned through
  the infrastructure acknowledgement; the tool host records a denied result
  and executes nothing. No prompt or capability argument can change it.
  At quota the segment latches denial of all writing capabilities while reads
  remain available. Checks count all regular logical workspace file bytes,
  including SQLite data/sidecars, without following links.
- The supervisor checks disk every 0.1 seconds independently of the sample
  interval. A live writer above quota causes tree termination. A completed
  write can overshoot before checking; future writing calls are then denied.
  This is explicitly a supervisor quota, not an OS filesystem byte ceiling.
  It excludes the archive, model files and other host storage. Unreadable or
  linked workspaces stop unchecked work. This is not arbitrary-code containment.
- Supervisor resource samples are written initially, periodically and before
  closing the stopped job. Default interval is one second; optional
  `extensions.resource_sampling.interval_s` accepts finite 0.05–60 seconds.
  CPU comes from aggregate job user/kernel time deltas (100 percent per logical
  core), process count from job accounting, RAM from summed current private
  commit of processes still verified as members of this job, disk from logical
  workspace bytes. Memory query races omit RAM rather than inventing zero.
- Optional GPU sampling uses existing `nvidia-smi` off the deadline thread,
  bounded to two seconds, refreshed about every five seconds. Numeric
  `vram_mb` is aggregate host NVIDIA used memory, with available MiB, scope and
  age in extensions. Cached observations older than ten seconds are omitted.
  Unavailable fields are omitted and named in `extensions.unavailable`;
  measured zero remains zero. No resource event originates in the worker.
- VRAM limits, nested resource wall-clock limits and the previously ignored
  `max_model_tokens` are explicitly refused. The top-level deadline remains
  authoritative. Non-Windows CPU/RAM/process-count requests are refused; normal
  process-tier execution can still report unavailable metrics. Per-capability
  resource metadata is not a second set of run-wide Job Object ceilings.

## Evidence and limits

Native Windows tests cover memory denial/termination, process-count denial,
CPU cap acceptance/throttling, suspended startup ordering, disk admission and
in-flight overflow, resume, setup/measurement failures and samples. Synthetic
GPU tests distinguish unavailable from observed zero. Real CLI archives verify.
No real model, physical reboot, Linux OS or container check was performed.
Host scheduling, uninterruptible filesystem I/O, polling overshoot and missed
best-effort notifications are not upgraded into hard real-time guarantees.

Windows API semantics: [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects),
[aggregate memory/process limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information),
[CPU rate hard caps](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_cpu_rate_control_information),
[notification delivery](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port).
