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

## Addendum (S003c): a reply without a tool call does not end the run

Decided by the human on 2026-11-14 (open decision OD-5). Until S003c the loop
ended at the first reply that contained no tool call, so with a small model an
unprompted run lasted seconds. Now the runtime answers such a reply with a
fixed *continuation message* and calls the model again; the run ends only at
its step limit, its deadline, or a failure.

- The text is part of the experimental condition. It comes from the
  experiment's `continuation.message`; when that is omitted, from the default
  in the experiment-config schema bundled with the world: *"No one has
  replied. The world is still running, and the tools available to you are
  unchanged."* It states facts about the run and gives no instruction. The
  Simulation holds no copy of the default.
- Each time it is used it is recorded as an `environment.message` event before
  the model sees it.
- A world whose bundled contracts cannot express or record it (built before
  0.3.0) is refused rather than run with the old behaviour.
- Because runs now last as long as their limits allow, the context guard drops
  the oldest whole turns, keeping the initial prompt and the latest message,
  once blanking old tool results is not enough, and records it.
- Whether the final protocol for S010 and S012 also gives the agent time
  notices is a separate question (`notify_agent_before_s`, still refused).

