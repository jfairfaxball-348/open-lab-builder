# S014d ChatGPT plan-usage integration check: tool-use round trip demonstrated

Date: 2026-11-15. Engineering check, NOT_SCORED. Route: OpenAI Responses API
under the owner's ChatGPT Plus plan through Sign in with ChatGPT (preview for
open-source and locally hosted apps). Approved budget: 8 per run, 20 per day,
30 total. **12 used.** No API key, no credits, no other provider and no fallback
were involved.

## Owner actions and decisions

- **OD-10 resolved:** the owner chose to license all three repositories under
  Apache-2.0 before signing in (Simulation `2280785`, Window `3a88970`, pushed;
  Builder in the S014d commit). The documentation's eligibility wording, re-read
  on 2026-11-15, is unchanged: "open-source and locally hosted apps".
- The owner signed in through the official browser flow and consented to plan
  usage. Registration issued a client, the ID token verified against OpenAI's
  published keys, and the granted scopes include `chatgpt.tokens.use.direct`.
- At the owner's request, Claude set the per-app limit for "The Open Laboratory"
  at chatgpt.com/settings/usage to **10%** of the weekly plan allowance (minimum
  offered; credits after the limit stay off). The setting was confirmed after a
  reload.
- Model: `gpt-6.1-sol`, first of eight models the account lists at
  `GET /v1/models` (`visibility == "list"`). This is the smoke model only; the
  campaign arm is chosen in S014h.

## Documentation changes found at the pre-sign-in re-check

Since S014a the preview's unsupported-field list grew (`max_tool_calls`,
`metadata`, `moderation`, `multi_agent`, `prompt`, `prompt_cache_retention`,
`safety_identifier` added), explicit system messages are rejected, and function
tools must be grouped in namespaces or supplied as `additional_tools`. The
adapter follows the current page; HOSTED_PROVIDERS.md is updated.

## Result

S014d's exit criterion is **met**: a tool-use round trip on the hosted model,
with effective settings recorded.

| Run | Client context guard | Requests | Outcome |
| --- | --- | --- | --- |
| `s014d-chatgpt-smoke/run-20261115t082528z-66ca75` | 4096 (local baseline) | 6/6 ok | search → describe, repeated three times; no invoke; `max_steps` |
| `s014d-chatgpt-smoke-16k/run-20261115t082620z-039e25` | 16384 (diagnostic) | 6/6 ok | search → describe → demonstrate → **invoke `6*7` → 42** → answered from the result; `max_steps` |

- Every request completed (`response.completed`), 2.4–3.6 s each, 22–30 output
  tokens, zero reasoning tokens reported, model version `gpt-6.1-sol`. No
  provider error, retry or refresh occurred. Multi-turn histories with
  namespaced `function_call` and `function_call_output` items were accepted.
- In the 16k run the model's final text was "It returned **42**", matching the
  tool result; that is a result-informed answer inside a run.
- In the 4096 run the Laboratory's own context policy, not the provider, shaped
  the loop: the guard reserves the requested 2048 output tokens, so the
  4.5 kB documentation result survived one step and was then truncated to a
  short stub, after which the model described the capability again. At step 3,
  with the full documentation in view, the model chose another search instead
  of invoking; that choice is model behaviour and is reported as observed, not
  explained. Gemma passed the same guard in S014c because its turns were
  shorter. The 16k variant is a diagnostic, not the matched condition.

## Effective settings (recorded in each run's `model.json`)

Temperature 0.7, output cap 2048 and seed 41 were requested and **not sent**
(unsupported on the preview route; no seed on the Responses API). Reasoning
effort was not sent (provider default). Tool schemas were sent unchanged with
`strict: false` in namespace `laboratory`. `store: false`; full history resent
each step. Reasoning items are withheld from the runtime, never resent and
never recorded.

## Integrity

Both archives verify. The provider ledger reconciles (12 reservations, 12
outcomes); each run's `provider-ledger.jsonl` mirrors the exact request bodies.
A scan of both archives and the provider directory (41 files) found none of
the stored access, refresh or ID tokens.

## Not established

- Behaviour or autonomy of any kind: two six-step runs on a fixed instruction.
- Token refresh, revocation and the documented error codes were exercised only
  against fakes (Simulation `tests/test_chatgpt.py`); live tokens did not reach
  expiry during the check.
- How much of the 10% plan allowance one request consumes; OpenAI's metering
  is opaque to the app.

## Consequence for the programme

A hosted arm under the 4096-token guard is limited by the Laboratory's context
policy before the model's capability is tested. Whether S014h keeps 4096 for
comparability with S007d/S007h or registers a larger guard for all hosted arms
is a decision for S014g/S014h (OD-13), not something this check settles.
