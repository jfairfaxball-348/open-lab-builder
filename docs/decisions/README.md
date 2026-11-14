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
| [0006](ADR-0006-isolation.md) | Two isolation tiers: supervised process now, container before agent-written code | Accepted; container mechanism open |
| [0007](ADR-0007-durable-state.md) | Append-only JSONL event log as the record; SQLite for indexes and memory | Accepted |
| [0008](ADR-0008-component-communication.md) | Components communicate through files under a data root; Window is read-only | Accepted; front-end stack decided in S004 |
| [0009](ADR-0009-checkpoint-barriers-and-agent-memory.md) | Complete-step checkpoints, append-only rollback/resume and agent-owned live memory | Accepted; refines ADR-0007 memory location |

Unresolved choices are tracked as `open_decisions` in
[`docs/roadmap/state.json`](../roadmap/state.json).
