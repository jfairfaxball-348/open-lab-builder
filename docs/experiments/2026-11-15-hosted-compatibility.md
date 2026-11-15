# S014g hosted compatibility suite: ChatGPT plan usage admitted

Date: 2026-11-15. Engineering check, NOT_SCORED. Provider set after the owner's
decisions: ChatGPT plan usage only (Gemma scrapped, OD-12; Anthropic excluded).
Registered settings: `gpt-6.1-sol`, client context guard 500,000 tokens (OD-13),
temperature/output cap/seed requested but not sent (preview route), reasoning
effort not sent. Usage cap: the owner's 10% per-app plan limit; ledger ceilings
nominal. Scripted and live success here is integration evidence, not autonomy.

## Result: `openai-chatgpt` passes every case

| Case | Fake suite (Simulation `21b8c6c`) | Live (2026-11-15) |
| --- | --- | --- |
| Text reply | pass | pass: "I'm ready." with no tool call |
| Structured tool call | pass | pass: search, describe, demonstrate, invoke well formed; zero repairs |
| Real capability invocation | pass (`math.evaluate` 6*7 → 42) | pass: `math.evaluate` returned 42 |
| Result handling | pass: every result returned under its `call_id` | pass |
| Result-informed second turn | pass | pass: "returned **42** for `6*7`" |
| Multi-turn context | pass: each request extends the previous history unchanged; documentation untruncated; no drops | pass: 8 steps, no context drop or truncation |
| Archive verification | pass in every case | pass (both runs) |
| Budget enforcement | pass: per-run ceiling stops sending | not exercised live (ceilings nominal by owner decision) |
| Rate limit | pass: retried within the step | fakes only |
| Plan refusals (usage limit via HTTP or stream, not eligible, unsupported capability, invalid user) | pass: stop the provider, no retry | fakes only |
| Temporary failures (503 usage unavailable, admission 503, cut stream, dropped connection) | pass: bounded to 2 attempts, each counted | fakes only |
| Timeout | pass: counted as spent, retried | fakes only |
| Ended session (refresh `invalid_grant`) | pass: nothing sent, tokens cleared, run stops | fakes only |
| Interruption | pass: automatic recovery refused at launch; operator resume of a paused run refused (no model digest), nothing sent | n/a |
| No token or reasoning text recorded | pass in every case | pass: 0 token hits |

Live runs: `s014g-chatgpt-text/run-20261115t085138z-85c809` (2 requests) and
`s014g-chatgpt-tools/run-20261115t085147z-deec02` (8 requests). All 10 requests
completed first time; the provider ledger holds 22 reservations and 22 outcomes
in total across S014d and S014g.

## Limits of this result

- Error, timeout and session-end handling are verified against fakes. Provoking
  them live would spend plan usage or require revoking the session.
- Interrupted hosted runs cannot be resumed at all; a campaign must account for
  such a cell as interrupted, never rerun it silently.
- In the live tool run the model kept answering after the result (steps 6–8)
  because the run continues until `max_steps`; that is runtime design, not an
  integration fault.
- One full Simulation test run had an unrelated container-tier timing failure
  (`test_timeout_removes_the_container`); it passed alone and in a full rerun
  (358 passed).
