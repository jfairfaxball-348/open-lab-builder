# ADR-0004: A small custom agent loop instead of an agent framework

Status: Accepted (S001). Implemented in S003.

## Context

The agent runtime must run for days, survive crashes, resume from checkpoints,
and emit a complete record of every model call and tool call from
infrastructure the agent does not control. It must not be tied to one model or
serving framework.

## Decision

Write the orchestration loop ourselves: call the model gateway with the
conversation and the meta-tools, record the reply, execute tool calls through
the tool host, persist state, repeat. Context management (summarising or
truncating a long conversation) is an explicit, recorded step in that loop.

## Alternatives

- **LangChain / LangGraph, AutoGen, CrewAI, smolagents and similar.** They
  provide loops, tool abstractions and memory quickly, but: their state is hard
  to checkpoint exactly; instrumentation hooks sit inside the agent process
  rather than in a separate recorder; they change frequently; and they bring
  large dependency trees. The loop itself is small; the hard parts here
  (supervision, recording, recovery) are ours regardless.
- **Run an existing coding agent (Claude Code, Codex) as the inhabitant.**
  Capable, but depends on external services, conflicts with local-first, and
  its internal loop is not ours to observe or checkpoint.
- **MCP client frameworks as the runtime.** Addressed in ADR-0003: MCP can be a
  transport, not the runtime.

## Consequences

- We own context-window management, retry policy and tool-call parsing,
  including for models with weak native tool calling. The gateway must
  normalise tool-call formats (ADR-0005).
- Every step is a plain, serialisable state transition, which makes exact
  checkpointing and replay feasible.
- If a framework later proves worthwhile for a narrow job, it can live behind
  the runtime interface without changing the contracts.
