# S007c runtime policy engineering validation

Date: 2026-11-14. Scope: versioned continuation, quiet scheduling, context guards,
explicit memory and reconstructible input traces. This is engineering evidence;
S007d remains UNEXECUTED and B-EXPANSION remains closed. No new models, downloads,
hosted calls, credentials or system changes were used.

## Implementation

Simulation now freezes `legacy-immediate-v1` or `quiet-until-deadline-v1` in
`policy.json`, with exact continuation text, context/memory/turn/repair versions,
client guard and experiment digest. Defaults preserve legacy conversation inputs.
Unknown fields, versions, context/summary/memory and turn semantics refuse launch.
The specification is [Runtime policies](../architecture/RUNTIME_POLICIES.md),
with design rationale in [ADR-0016](../decisions/ADR-0016-versioned-runtime-treatments.md).

Quiet permits 1-16 consecutive tool-free replies, then appends no continuation
and stops inference until the original active deadline. Any parsed tool call
resets the streak, including denied/failed calls; prose is never parsed for
intent. There is no automatic wake. A 250 ms sleeping state-barrier loop lets
the supervisor retain deadline, resource, checkpoint and pause authority without
polling the model. Step exhaustion still ends immediately. Checkpoints preserve
counter, idle latch and policy digest; resume/recovery cannot silently reset them.

Before every HTTP attempt the supervisor records and syncs the exact outgoing
request and context mutations, then acknowledges before network transmission.
Retries and failed calls retain inputs. Scripted inputs are labelled ignored
conversations, not HTTP traffic. Context preserves preamble, initial prompt and
latest assistant/tool group; protected overflow is explicitly reported rather
than silently dropping them. This guard is not a server-tokenizer guarantee.
No automatic memory retrieval, hidden summary or reasoning response capture was
introduced. Stored notes return as tool results only through explicit retrieval.

These protocols use existing extension points; schemas, generated fixtures and
minimal world 0.6.0 were unchanged. Historical S007a archives still verify; new
recovery segments record the effective legacy interpretation without rewriting
older observations or inventing earlier exact inputs.

## Native local-model scheduling pilots

Committed Simulation configurations: `experiments/s007c-legacy.json` and
`experiments/s007c-quiet.json`. Both use installed `llama3.2:3b`, the same world,
prompt, preamble, model/tool permission set, requested temperature 0, seed 903,
output cap 128, client guard 4096, two-step cap, 20 active seconds and 2-second
checkpoint interval. The initial prompt explicitly asks for one short sentence
without a tool call: this is a directed scheduling check, not unguided autonomy.
No model or world edits occurred between launches. World content digest:
`1ccc407cc300e7622bcca348ff22c5982bff5cf3a10559ee741304350e960da5`.

| Policy | Local archive id | Observed calls / inputs / continuations | Result |
| --- | --- | --- | --- |
| legacy-immediate-v1 | run-20261114t180326z-a87542 | 2 / 2 / 1 | Terminated at max_steps; 28 events; 7.516 active seconds |
| quiet-until-deadline-v1 | run-20261114t180340z-bcaf9b | 1 / 1 / 0 across pause/resume | Paused at step 1, then remained idle to original deadline; 52 events; 20.031 active seconds including both segments |

Both first replies said the task requires capability discovery, rather than
simply complying with the directed prompt. The legacy continuation was followed
by `capabilities.search(query="engineering check")`, returning no matches.
This task-instruction mismatch is retained. Quiet paused with its idle latch
set; resume recorded a restored idle entry, made no further inference call and
injected no wake text. Both archives verified without problems before/after
resume as applicable. Archive bytes remain only in the local data root.

Legacy model-call durations were 6594 and 453 ms; quiet's single call was 625 ms.
These include request-recording overhead and differ in host load/cache state;
they do not establish comparative efficiency. The shared first request body is
recorded exactly; matching requested seeds do not promise deterministic runs.
The slight deadline overshoot is an observation, not a hard real-time guarantee.
Effective server context, sampling and offload remain unverified per call.

## Validation, limitations and handoff

Before edits, Builder health passed 305 tests in 41.71 seconds and Simulation
passed 252 tests in 224.89 seconds. The focused changed-behaviour suite passed
27 tests after implementation. Added coverage exercises unsupported-policy
refusals, implicit/explicit legacy equality, no inference busy-loop, bounded
reflection and reset semantics, idle hard/graceful deadlines, step ceilings,
pause/resume, native worker termination/recovery from an idle checkpoint,
policy tampering, exact inputs through retries and HTTP failure, explicit
memory retrieval, and refusal to transmit unacknowledged input.

Older tests with exact event sequences now assert the additional input records
explicitly; conversation and deadline/step assertions remain. No failing assertion
was removed or weakened. The draft recovery test used a fractional checkpoint
interval that the existing schema correctly refused; it now uses the supported
one-second interval. No schema relaxation was made.

Long-run request snapshot storage/fsync overhead, Linux execution and physical
reboot durability remain unverified. Scripted memory-return coverage does not
establish useful real-model memory use, reflection, intent, neutrality or autonomy.
Neither the choice of quiet policy nor a tool-free reply is a behavioural GO.
No primary benchmark treatment was selected based on these pilots.

Exact next milestone: **S007d - Autonomy Baseline and Behavioural Benchmark**.
Preregister one primary policy/profile, validate the harness and keep pilot data
separate before scored cells. Existing expansion and hosted-provider gates remain.

Final Simulation suite: **275 passed in 259.68 seconds, without warnings**.
Lint passed. Source/configurations committed and pushed as `80cb67b`.
Both S007c configurations validated; committable privacy/diff checks passed.

Final Builder validation: lint passed; **305 tests passed in 40.96 seconds**,
with all project health checks passing. Prior S007a validation is retained in
`docs/roadmap/validation/S007a.json`.
