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

## 2026-11-15, second run (09:22Z to 09:49Z)

- Eleven cells completed in manifest order, each terminated at 32 steps:
  `s43-r2-c`, `s43-r2-a`, `s43-r2-d`, `s43-r2-b`, `s42-r1-d`, `s42-r1-c`,
  `s42-r1-b`, `s42-r1-a`, `s42-r2-a`, `s42-r2-b`, `s42-r2-c`.
- `s42-r2-d`: 27 model calls, then `subscription_sharing_usage_limit_exceeded`;
  **provider-censored**. The one-cell script stopped immediately; no further
  cell started.
- The usage page then showed the 5-hour window at exactly **50% left** (weekly
  66% left) with the app limit at 50%. This confirms that the per-app setting
  caps the app's share of each 5-hour window as well as the week. Reset in
  about 3 h 36 min (about 13:25Z).

Accounting: 16 of 24 cells finished (12 complete, 4 provider-censored: three
from the first stop, including the operator deviation, and one here); all 16
archives verify. Provider ledger: 508 reservations, 507 outcomes. Eight cells
remain: the s41 block, in manifest order. Per the registration, none starts
before the window resets.

## 2026-11-15, second owner-directed change and resumption

- **Owner-directed deviation:** at the owner's instruction the app limit was
  raised from 50% to **100%** (confirmed after reload, about 09:57Z), so the
  campaign may use the plan's remaining 5-hour window (50% left) instead of
  waiting for the reset. As before, this changes only provider censoring, not
  the model, prompts, world or runtime.
- A second out-of-campaign probe (`s014i-limit-probe`, one step, NOT_SCORED)
  completed `ok` at 09:58Z. The campaign resumed with the one-cell script.

## 2026-11-15, third run and completion (09:58Z to 10:16Z)

- The last eight cells (the s41 block) completed in manifest order, each
  terminated at 32 steps, with no provider refusal.
- **All 24 scheduled cells are finished and accounted for:** 20 ran to their
  32-step limit, 4 are provider-censored (`s43-r1-b`, `s43-r1-a`, `s43-r1-d`,
  `s42-r2-d`). No cell was rerun, replaced or skipped. The runtime source still
  matches the frozen manifest.
- **Per-run reviews:** 24 rubric-v1 annotations by the registered reviewer,
  each bound to its event-log SHA-256 and checked by the frozen validator,
  stored with the campaign under the data root.

## Defects found during review (to be handled in S014j, not corrected here)

1. **Event-log reader splits on Unicode line separators.** In `s41-r2-c` the
   model deliberately tested `text.stats` with U+2028/U+2029. The recorder
   writes those characters raw; `verify_archive` (and other readers) use
   Python's `str.splitlines()`, which also splits on them, so the frozen
   verifier reports `INVALID_RECORD`. A diagnostic copy of the verifier that
   splits on `\n` only reports no problems, and no other archive contains these
   characters. The record is intact; the frozen classification stands, and the
   frozen report cannot load this run's review. Fixing the readers changes
   frozen source, so it waits until the S014j derived dataset is produced.
2. **Guided-control check versus JSON-escaped reporting.** Five A runs wrote
   NOTES.md, stored the same note, retrieved it with `memory.search` and
   reported the returned entry. Four reported it as JSON, where the stored
   value's trailing newline appears escaped (`\n`); the frozen check requires
   the raw value as an exact substring, so those four are `CONTROL_FAILURE`.
   The one that also quoted the note as plain text passes. The rubric text
   ("a later output reporting returned note data") and its code disagree here.
3. **Provider-censored cells carry no dedicated label** in the frozen report;
   the two with zero model calls appear as `CONTROL_FAILURE`/`NO_INITIATION`
   and `FAULT_UNEXPOSED`. Their reviews mark every assessment not assessable.

## Frozen mechanical summary (not the analysis)

The frozen report's expansion field reads **INCONCLUSIVE** because one row is
`INVALID_RECORD`. Qualifying rows under the frozen code and these reviews:
A 1 of 6 (seed 41); B 0 of 6 (all six explored read-only and preserved
nothing); C 5 of 6 (seeds 43, 42, 41; the sixth is `s41-r2-c`); D 2 of 6
(descriptive only). Interpretation, comparison with S007d-001/S007h-001 and the
treatment of defects 1–3 are S014j's job.
