# Architecture decision records

One file per significant decision: context, decision, alternatives, consequences.
A decision is changed by adding a new record that supersedes the old one, not
by rewriting history.

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](ADR-0001-language-and-tooling.md) | Python 3.12 with uv and minimal dependencies | Accepted |
| [0002](ADR-0002-contracts.md) | JSON Schema contracts as the only cross-repository interface | Accepted |
| [0003](ADR-0003-capability-manifest.md) | Transport-neutral capability manifest; discovery through meta-tools; MCP as a projection | Accepted |
| [0004](ADR-0004-orchestration.md) | Small custom agent loop instead of an agent framework | Accepted |
| [0005](ADR-0005-model-gateway.md) | Provider-neutral model gateway; Ollama first; sequential model loading | Accepted |
| [0006](ADR-0006-isolation.md) | Two isolation tiers: supervised process now, container before agent-written code | Accepted; container mechanism decided in ADR-0014 |
| [0007](ADR-0007-durable-state.md) | Append-only JSONL event log as the record; SQLite for indexes and memory | Accepted |
| [0008](ADR-0008-component-communication.md) | Components communicate through files under a data root; Window is read-only | Accepted; front-end stack decided in S004 |
| [0009](ADR-0009-checkpoint-barriers-and-agent-memory.md) | Complete-step checkpoints, append-only rollback/resume and agent-owned live memory | Accepted; refines ADR-0007 memory location |
| [0010](ADR-0010-bounded-deadline-checkpoints.md) | Fixed deadline grace, complete-step snapshot and supervisor termination | Accepted; supersedes ADR-0009 deadline-mode refusal |
| [0011](ADR-0011-bounded-supervisor-recovery.md) | Opt-in bounded restarts, startup recovery, verified writer ownership and model health | Accepted; extends ADR-0009/0010 |
| [0012](ADR-0012-process-resources-and-sampling.md) | Windows job ceilings, supervisor quota admission and truthful periodic samples | Accepted; completes split supervisor scope |
| [0013](ADR-0013-autonomy-as-an-experimental-objective.md) | Autonomy baseline, explicit interventions and evidence-gated expansion while preserving architecture | Accepted for planning; runtime unchanged |
| [0014](ADR-0014-rootless-podman-in-wsl2.md) | Rootless Podman in WSL 2 as the container mechanism | Accepted; resolves OD-1, backend is S006c |
| [0015](ADR-0015-container-capability-backend.md) | Per-call rootless Podman containers for capabilities, supervisor-owned cleanup | Accepted; S006c, refines ADR-0006/0014 |
| [0016](ADR-0016-hosted-provider-broker.md) | Hosted providers only through a supervisor-owned broker with secret isolation, reserved budgets and no fallback | Accepted (S014a); amends ADR-0005, supersedes planned S007f; not yet implemented |
| [0016](ADR-0016-versioned-runtime-treatments.md) | Versioned continuation/quiet treatments, checkpointed idle state and pre-request input records | Accepted; S007c |
| [0017](ADR-0017-owner-accepted-go-and-capability-testing.md) | Owner-accepted post-hoc GO for S014i-001; test each new capability instead of repeating the baseline | Accepted (owner); supersedes S014n |
| [0018](ADR-0018-supervisor-specialist-consultation.md) | Supervisor-mediated local specialist capability and one finite GPU lease | Accepted (S007e) |
| [0019](ADR-0019-study-manifests-and-evidence-exports.md) | Offline study inventories and portable stopped-archive exports, separate from runtime/world contracts | Accepted (S010a) |
| [0020](ADR-0020-source-bound-study-analysis.md) | Source-bound descriptive analysis and typed investigator annotations over verified exports | Accepted (S010b) |
| [0021](ADR-0021-hosted-recovery-identity.md) | Opt-in hosted run recovery: frozen request identity plus provider-reported model_version pin; provider stops never trigger recovery | Accepted (owner); S011r, amends ADR-0016 |
| [0022](ADR-0022-strategic-reset-habitat.md) | Strategic reset: build Habitat v1 in vertical slices; retire endurance/comparison campaigns; engineering demonstrations prove capabilities | Accepted (owner, 2026-11-16) |
| [0023](ADR-0023-pinned-agent-tools.md) | Run-local tools pin sandbox-validated entry source in protected checkpoint state | Accepted; S016b, refines ADR-0003/0015 |
| [0024](ADR-0024-supervisor-phenomena.md) | Supervisor-owned coupled fields with private checkpoint state and deterministic journal replay | Accepted; S017, extends S007e mediation |
| [0025](ADR-0025-time-and-run-lineage.md) | Bounded self-scheduled wakes and operator-only final-data lineage | Accepted; S018, extends runtime policies/checkpoints |
| [0026](ADR-0026-approved-survival-directive.md) | Owner-approved exact survival directive, prompted-objective interpretation and new-chat launch boundary | Accepted (owner, 2026-11-16); S012-001/002 reported, further launches suspended by ADR-0027 |
| [0027](ADR-0027-habitat-v2.md) | Habitat v2: workshop, local assistants/media; suspend further inhabitant experiments | Accepted for planning (owner, 2026-11-16); no implementation/inference |

Unresolved choices are tracked as `open_decisions` in
[`docs/roadmap/state.json`](../roadmap/state.json).
