# ADR-0016: Versioned runtime treatments and pre-request input records

Status: Accepted (S007c). Refines ADR-0004's continuation semantics and extends
ADR-0009/0010 checkpoint barriers without changing supervisor authority.

## Decision

Preserve immediate continuation as `legacy-immediate-v1`. Add
`quiet-until-deadline-v1`: after a configured consecutive tool-free reply
threshold, stop inference and wait until the original active deadline. There
is no automatic wake; resume preserves the idle latch. The threshold bounds
reflection opportunities without interpreting model prose. Both are treatments,
never claims of neutrality. Time/steps/permissions remain supervisor-controlled.

Freeze defaults, exact continuation text, context and explicit-memory identities
in `policy.json`, bound to a launch event and the experiment digest. Checkpoints
preserve scheduling counters, idle latch and policy digest. Complete-state
barriers while idle let the existing supervisor pause, checkpoint or stop safely.

Record exact outgoing model request bodies before each HTTP attempt, including
context guard mutations and retries. A dedicated worker-to-supervisor request
produces a supervisor-owned `limit_enforced` action with stage `model_input`;
the worker waits for acknowledgement before contacting the server. This applies
the context policy and does not grant the worker access to privileged event APIs.
Existing event payload extensions suffice; schemas and world bytes are unchanged.
No reasoning response channel is recorded. Memory retrieval stays explicit.

## Alternatives and limitations

Repeatedly asking the model whether it wants to wait would itself impose model
calls and nudges. Parsing prose for intent would introduce an interpretation as
authority. Periodic automatic wakes could be another treatment, but are excluded
from this bounded implementation. The quiet policy can leave most of a run idle;
that is an allowed observation, not a failed experiment by definition.

The guard still estimates token capacity and preserves protected content on
overflow. Effective server context, sampling and offload remain unverified per
call. Full request snapshots increase archive storage and I/O; long-run overhead,
Linux execution and physical reboot durability are unverified. A valid scheduling
trace establishes none of motivation, useful reflection or general autonomy.

Specification: [Runtime policies](../architecture/RUNTIME_POLICIES.md).
