# ADR-0018: Supervisor-mediated specialist consultation

Status: Accepted (S007e, 2026-11-15). Refines ADR-0005; preserves ADR-0016.
Written before implementation.

## Decision

`models.ask` is a world capability with the existing MCP invocation shape:
`server: supervisor-gateway`, `tool: models.ask`. This reserved pair is an
in-process supervisor service, not a network MCP client. No arbitrary MCP
server is enabled. The ordinary discovery, permission and input/output checks
still apply. The worker sends a consultation request over its existing pipe;
the supervisor independently checks the frozen configuration, capability,
permissions and arguments before contacting the gateway. Capability processes
receive no gateway handle, endpoint, credentials or archive path.

The experiment's closed `extensions.specialist` object selects the single
bundled gateway id `specialist-text` and bounds calls, prompt/output characters,
output tokens, per-call seconds and lease seconds. Only an external orchestrator
(or the scripted test stand-in) is supported in this milestone. The specialist
is the approved, digest-pinned local Ollama llama3.2:3b. It has no tools and sees
only the supplied prompt. Replies are untrusted model-output data, never commands.
No retry, provider substitution, model selection argument or privilege expansion.
The gateway translates this single chat request to Ollama's native chat API
with a finite keep-alive and output-token cap. This narrow exception to
ADR-0005's management-only native API rule is needed because the compatible
chat endpoint cannot enforce the lease's residency lifetime. No reasoning
channel or tools are requested or forwarded.

One supervisor-owned OS lock under the data root serializes specialist leases.
Acquisition refuses other resident Ollama models rather than unloading unrelated
work. Identity is checked before load. First use loads, later calls reuse the
lease, expiry and every orderly segment exit unload. An asynchronous worker does
HTTP only; the supervisor alone records and polls its results, so deadlines and
resource monitoring continue during a consultation. Native finite keep-alive
limits residency after a supervisor crash; an abrupt crash cannot promise an
immediate unload. Lease state is never restored from checkpoints. Call
reservations are synced in the event log before dispatch and counted across
resume/replay, including failed or uncertain calls. A resumed segment reacquires
and revalidates the model. Model servers remain outside runtime job limits.

Record lease acquire/load/unload/release, failures, durations, digest, exact
specialist prompt/reply and reported usage as supervisor-owned observations in
existing event extensions. No reasoning channel is recorded. Hosted orchestration
continues through its existing broker with unchanged conversation/policies.

Builder build-time self-tests inject a labelled fake specialist transport for
the reserved service and validate the demonstration's request/result schemas.
They never contact a model. Simulation fake-server tests and the separately
authorized load/ask/unload check establish actual routing; build-time fake
replies are not evidence of real inference. World 0.7.0 adds this capability and
manifest; the archived 0.6.0 release and fixture remain byte-identical.

## Alternatives and limits

Giving capability subprocesses an Ollama address would bypass scheduling and
recording. Running inference inside the supervisor's event loop would block
deadline enforcement. A general MCP broker, multiple specialists, local
orchestrator swapping and GPU/network access inside containers are deferred.
Existing schema extension points suffice; no schema version changes are needed.
The lease excludes cooperating Laboratory supervisors using the same data root,
not unrelated applications or an external Ollama client. Server-reported identity
and keep-alive are not hardware-level GPU isolation. The capability check follows
ADR-0017's owner-accepted post-hoc GO and does not re-establish general autonomy.
