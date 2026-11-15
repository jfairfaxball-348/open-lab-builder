# S014c Gemma integration check: tool use works, multi-step turns fail

Date: 2026-11-15. Engineering check, NOT_SCORED. Provider: Gemini API free
tier, the owner's Open Lab project, with the key installed by the owner through
`ols provider set-key`. Approved budget: 20 requests, raised by the owner to 32.
**22 used.** No paid tier, no other provider and no fallback were involved.

## Project limits (read from AI Studio, 2026-11-15)

Gemma 4 26B and Gemma 4 31B on the Open Lab project, free tier: **30 requests
per minute, 16,000 input tokens per minute, 14,400 requests per day**; no prior
usage. A Laboratory request carries about 600–2,000 input tokens and up to about
4,000 at the client guard, so input tokens per minute bind first. The profile
spaces requests at least 15 seconds apart.

## Result

S014c is **not complete**. Integration works up to a provider-side failure:

- In all three live smoke runs (one 26B, two 31B), the model searched for an
  arithmetic capability, described `math.evaluate` and invoked it on `6*7`,
  which returned 42. Every call was well formed, with zero syntactic repairs.
  The unchanged JSON Schemas were accepted via `parametersJsonSchema`.
- The next model turn, the first whose history holds two consecutive
  function-call turns, received **HTTP 500 INTERNAL** in every run. The broker
  retried once and then ended the step with a recorded error, as designed.
- One out-of-run replay of such a request (31B) succeeded. Gemma answered from
  the tool result ("returned the value 42"). That is the only result-informed
  follow-up observed, and it was not within a run.

| Requests by history shape | gemma-4-26b-a4b-it | gemma-4-31b-it |
| --- | --- | --- |
| No call or one call turn | 3/3 ok | 6/7 ok (one transient 500) |
| Two or more call turns | **0/6 ok** | **2/6 ok** |

A minimal synthetic two-call conversation (one `add` tool, no Laboratory
content) failed on 26B and succeeded on 31B. That places the 26B failure on
Google's side. On 31B, one failing request was byte-identical, apart from
provider-issued call ids, to the replay that succeeded, so the 31B failures
are intermittent and provider-side too.

## Changes made during the check

- **Model:** the owner switched the Gemma arm from `gemma-4-26b-a4b-it` to
  `gemma-4-31b-it` (same limits) after 26B failed every multi-step request.
- **Adapter 1.1.0:** thought signatures are no longer resent. Gemma accepts
  their absence. I first attributed the 500s to resent signatures from a
  single successful replay; a later identical request without them also
  failed, so that attribution was wrong and the code comment was corrected.
  The behaviour change is harmless and recorded per run.
- **Earlier fix found by tests, before any live request:** thought text is never
  resent to the provider or written to the archive.

## Evidence

Ledger: `<data root>/providers/google-gemini/ledger.jsonl` (22 reservations,
each with its outcome, usage and model version). Runs (each archive verifies;
each `provider-ledger.jsonl` mirrors the exact request bodies, which hold no
credential): `s014c-gemma-smoke/run-20261115t074840z-e772ab` (26B),
`s014c-gemma-31b-smoke/run-20261115t075225z-1341ee` and
`run-20261115t080039z-f8052a` (31B). Single-request diagnostics are under
`<data root>/diagnostics/`. Configurations:
[26B](configs/S014c-gemma-smoke.json), [31B](configs/S014c-gemma-31b-smoke.json).
Reported usage: 10,276 input and 228 output tokens in total.

## What this means for the programme

As of today, Gemma on the free Gemini API cannot reliably sustain the
multi-step tool use every benchmark cell needs. Running the campaign on it now
would mostly measure provider errors. Options, none taken without the owner:
re-check reliability later with a small approved probe (service behaviour may
change); allow more broker retries per step (costs budget and changes the
provider-error profile, so it would be registered); or treat Gemma as unavailable
for the matched campaign and record why. The ChatGPT arm (S014d) does not
depend on this.

Sources: [Gemma on the Gemini API](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api);
a similar public report of 500s after a second tool response
([Google AI forum](https://discuss.ai.google.dev/t/bug-report-500-internal-error-with-multi-turn-tool-use-gemini-2-5-pro-preview-03-25/78103))
and of frequent Gemma 500s ([Google AI forum](https://discuss.ai.google.dev/t/constant-500s-with-gemma/142215)).
