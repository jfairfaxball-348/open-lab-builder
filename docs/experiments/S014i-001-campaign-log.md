# S014i-001 campaign log

Operational record of the registered campaign
([registration](registrations/S014i-001.md), Builder `51f9b70`). It records
what happened in execution order, including deviations. It is not the analysis.

## 2026-11-15, first session

- 09:12Z: supervised batch 1 started (`--max-cells 4`, registration
  `51f9b7029b927175f23d97d2c45f55769383ab51`).
- `s43-r1-c`: terminated at 32 steps; 32 requests ok; about 124,000 input
  tokens in total; archive verifies.
- `s43-r1-b`: 30 model calls, then at 09:17:07Z the provider returned
  `subscription_sharing_usage_limit_exceeded` (as a `response.failed` stream
  event). The broker stopped the provider and the run failed as recorded:
  **provider-censored**.
- `s43-r1-a` and `s43-r1-d`: started by the runner within the same batch,
  each refused on its first request with the same code; zero model calls;
  **provider-censored**.

**Deviation from the registration.** The registration says no further cell
starts after a usage-limit stop until the limit resets. The operator script
checked for refusals only between batches of four, so A and D were launched
after B's stop. Under the registered no-replacement rule they stay censored
and are reported as an operator deviation, not as behaviour. From cell 5 on,
the operator script runs one cell at a time and stops after any terminal
provider outcome; the frozen runtime source is unchanged.

**Which limit.** After the stop, ChatGPT's usage page showed the plan itself
far from exhausted (5-hour window 91% left, weekly 73% left), with the app
limit at 10%. The refusal therefore came from the owner's per-app limit. The
page does not state the app limit's window; plan usage moved by about 9 points
of the 5-hour window during the stop, so the app share appears to be counted
against the 5-hour window (reset about 13:25Z). One full cell is about
120,000 input tokens, so about two cells fit per window at 10%.

Accounting after batch 1: 4 of 24 cells finished (1 complete, 3
provider-censored); provider ledger 127 reservations, 126 outcomes (the one
unresolved reservation is from `s014i-pilot-001`).

## 2026-11-15, owner-directed change and resumption

- The owner noted that OpenAI documents the per-app setting as a weekly limit.
  The observed refusal came after about 1% of the weekly plan and about 10% of
  the 5-hour window, so in practice the 10% setting also bounded the 5-hour
  share (undocumented; inferred from the usage page).
- **Owner-directed deviation:** at the owner's instruction the app limit was
  raised from 10% to **50%** (confirmed after reload, about 09:22Z). The
  registration said usage settings would not change during the campaign; this
  change affects only how often cells are provider-censored, not the model,
  prompts, world or runtime. Cells already censored stay censored.
- One out-of-campaign probe (`s014i-limit-probe`, one step, NOT_SCORED,
  excluded from every denominator) completed `ok`, showing the refusal had
  cleared before the next scored cell started.
- The campaign resumed with the one-cell-at-a-time operator script.
