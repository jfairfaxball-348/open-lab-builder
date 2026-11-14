# Runtime policies (S007c)

The scientific purpose is to control infrastructure interventions while permitting
observable inactivity. Both policies are experimental treatments. Neither is
asserted neutral, and a tool-free reply is not evidence of intent or failure.
No S007d benchmark is authorised or executed by this implementation milestone.

## Configuration and frozen identity

`extensions.runtime_policy` is an optional closed object. Its accepted fields:

| Field | Values / default |
| --- | --- |
| `id` | `legacy-immediate-v1` (default), `quiet-until-deadline-v1` |
| `max_tool_free_replies` | Quiet only: integer 1 through 16, default 1 |
| `context_guard_tokens` | Positive integer; default selected model manifest or 4096 |
| `context_policy` | `oldest-tools-turns-v1` only |
| `memory_policy` | `explicit-tools-v1` only |
| `turn_semantics` | `user-continuation-v1` only |

Unknown fields, versions and turn semantics are refused at launch. Summarisation,
implicit retrieval, model-requested sleep and mid-run human instructions are not
supported. No prose is parsed for scheduling authority. The experiment retains
its existing `continuation.message` field and bundled-schema default.

The supervisor resolves defaults and freezes `policy.json`, including the exact
continuation text, context guard, memory/repair identities and experiment digest.
The launch state event binds its canonical SHA-256. The model archive also carries
the resolved policy. Resume refuses changed policy/configuration or incompatible
checkpoint state. Historical archives retain their legacy policy interpretation;
they do not gain retroactive input observations.

## Scheduling and bounded reflection

Legacy immediately records/appends the configured user continuation after every
tool-free reply, including the last budgeted reply, as before. Successful tool
calls and tool-free prose retain their prior conversation shape and limits.

Quiet counts consecutive assistant replies containing **no parsed tool calls**.
Any parsed tool call resets the count, even if execution is refused or fails.
Below the configured threshold it delivers the same recorded continuation,
permitting at most that many consecutive tool-free replies before idling. This
is a bounded reflection opportunity, not a claim that reflection occurred.
At the threshold it appends no continuation and starts no further model call.
It remains idle for the remaining original active-time budget. There is **no
automatic wake**, no new message and no tool/model activity during this wait.
Pause/resume and worker recovery preserve idle state; they are not wake events.
An exhausted step budget still ends immediately instead of waiting.

The worker sleeps between bounded complete-state barriers (250 ms); it does not
poll the model. The supervisor continues resource, health and deadline checks,
and may checkpoint or pause at those barriers. Waiting counts as active time;
paused downtime does not. Graceful and hard deadline authority remain unchanged.
Health probes are infrastructure observations, not inference or model input.

Each segment records scheduling identity. A quiet idle entry is a supervisor
`limit_enforced` action with stage `runtime_idle`; restored idle entries are
labelled as restored. Complete-step checkpoints preserve the tool-free counter,
idle latch and policy digest. A crash can replay from an earlier checkpoint;
existing recovery events retain that rollback and original budgets.

## Context and exact inputs

`oldest-tools-turns-v1` names the existing guard: three characters per estimated
token, subtract the requested output cap, then blank older long tool results and
drop oldest complete assistant/tool groups. Preserve preamble, initial prompt
and the latest group, including fresh documentation. If protected content alone
exceeds the estimate, preserve it and explicitly report overflow. This is a
client guard, not a tokenizer guarantee or a request setting for server context.

Before every HTTP attempt, the worker submits the exact outgoing body and guard
details to the supervisor. The supervisor records a `limit_enforced` action with
stage `model_input`, then acknowledges it before any network call. Retries record
separate attempts. The request includes messages, tools and requested sampling;
context metadata includes before/after message digests, changes and overflow.
Scripted runs record their ignored conversation input and identify that backend;
they apply no tokenizer guard. No hidden reasoning response channel is recorded.
An unacknowledged input must never be sent to a server.

The full snapshot permits reconstruction despite truncated output displays,
context removal, failed model calls and recovery replay. Request snapshots grow
archives; long-run storage/performance is unverified. These are infrastructure
records outside the agent workspace, using existing event payload extensions.
No schema or world release changes are needed.

## Memory

`explicit-tools-v1` means no automatic retrieval, summary or prompt insertion.
SQLite notes enter model input only through returned `memory.search`/`memory.list`
tool results (or an explicitly requested demonstration). A written note alone
does not establish later use. The trace links actual tool results and subsequent
exact model inputs. Real-model memory competence remains a separate question.
