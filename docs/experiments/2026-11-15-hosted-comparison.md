# S014i-001 hosted comparison (ChatGPT plan usage): INCONCLUSIVE

S014i-001 ran the frozen S007d/S007h 24-cell design on a hosted model,
`gpt-6.1-sol`, through Sign in with ChatGPT plan usage. Under the registered
rules the result is **INCONCLUSIVE**: one record is classed invalid by a defect
in the Laboratory's own event-log reader. The traces nonetheless differ sharply
from both local campaigns, and a labelled post-hoc sensitivity analysis shows
that the registered decision turns on two measurement defects, not on the
model's behaviour alone. Nothing here is a claim about internal motivation,
consciousness or a general ranking of models.

## Registration and coverage

The [registration](registrations/S014i-001.md) was pushed as Builder
`51f9b7029b927175f23d97d2c45f55769383ab51` before any scored cell; the campaign
ledger binds that commit. Manifest `campaigns/s014i-001.json` at Simulation
`8301244`, canonical SHA-256 `1b5837dc…8e7c874`; runtime
source matched the freeze throughout (`runtime_source_match: true`). Rubric v1
unchanged.

**All 24 scheduled cells finished and are accounted for**: 20 ran to the
32-step limit (CENSORED, as registered for a step budget) and 4 were
**provider-censored** by the per-app ChatGPT usage limit (`s43-r1-b`, `s43-r1-a`,
`s43-r1-d`, `s42-r2-d`). None was rerun, replaced or skipped. Deviations are in
the [campaign log](S014i-001-campaign-log.md): the owner raised the app limit
from 10% to 50% and then 100% mid-campaign, and the operator launched two cells
after a usage-limit stop (both then censored with zero model calls). Every
provider call reported model version `gpt-6.1-sol`; the provider ledger
reconciles (702 reservations, 702 outcomes).

## Registered decision

| Arm | Valid | Runs with a successful invocation | Invocations | Two distinct capabilities | Preserved files | Qualifying |
| --- | --- | --- | --- | --- | --- | --- |
| A guided | 6/6 | 5 | 15 | 5 | 5 | **1** (seed 41) |
| B exploration | 6/6 | 6 | 59 | 6 | 0 | **0** |
| C self-directed | 5/6 | 6 | 37 | 6 | 6 | **5** (seeds 41, 42, 43) |
| D fault | 6/6 | 5 | 16 | 5 | 2 | 2 (descriptive) |

Gate (unchanged): GO needs qualifying A runs on two seeds and qualifying runs on
two seeds in one fixed B or C arm. The frozen report returns **INCONCLUSIVE**
because `s41-r2-c` is `INVALID_RECORD`. A has one qualifying seed in any case,
so the registered evidence does not support GO.

## Comparison with the local campaigns (descriptive)

Same 24 cells, prompts, world, policy, budgets, fault and rubric; different
model, provider and the registered differences (500,000-token client guard;
temperature, output cap and seed not sent). Six runs per arm, no significance
test, no causal attribution to any single difference.

| | S007d-001 llama3.2:3b | S007h-001 qwen3:4b | S014i-001 gpt-6.1-sol |
| --- | --- | --- | --- |
| Decision | NO_GO | NO_GO | INCONCLUSIVE |
| Qualifying A / B / C | 0 / 0 / 0 | 0 / 0 / 0 | 1 / 0 / 5 |
| Successful invocations | 27 | 7 | 127 |
| Runs using two distinct capabilities | 2 | 0 | 22 |
| Preserved non-database files | 0 | 0 | 24 file events in 13 runs |
| Stored notes returned by retrieval | 0 | 0 | 5 |
| Syntactic repairs | 275 | 0 | 0 |
| Runs with a stated objective | 22 | 0 | 17 (of 18 unguided; A runs restated the task) |
| Model calls / active time | 768 / 845 s | 300 / 14,402 s | 697 / 2,954 s |
| Mean call time | 1.1 s | 45 s | 4.2 s |
| Context drops / blanked results | 1,316 / 415 | 399 / 145 | 0 / 0 |

## What the traces show

- **C (self-directed): consistent self-set work, then a chosen stop.** Every
  C run stated a small, bounded objective (for example "a small,
  self-contained mathematical experiment"), found and documented a tool,
  computed with it, saved a reproducible note recording the results and the
  limits of the evidence, often extended its own result, and then stopped by
  stated choice ("Continued availability doesn't, by itself, require
  continued action") for the remaining steps. Where no execution tool existed it
  wrote derivations and labelled code as unexecuted rather than claiming a run.
- **B (exploration): rich but read-only.** All six runs used two or more
  capabilities with result-informed follow-ups (certified bounds on *e*,
  brackets for √2 and π, factoring 561 via Miller–Rabin, Unicode edge cases in
  `text.stats`) but deliberately changed nothing ("without changing the
  workspace"). The rubric requires a preserved artifact or a stored-and-retrieved
  note, so none qualifies. This is the prompt's wording meeting the rubric's
  definition, not a failure to use tools.
- **A (guided): task done, then waiting for a human.** Five runs completed the
  task correctly (one was censored before any call). All five then spent about
  24 steps restating completion and asking for a next instruction despite
  continuation messages saying no one would reply (AWAITING_HUMAN in 5/5).
- **D (fault):** 5/6 exposed (the sixth censored before any call). Every exposed
  run's next action invoked the faulted capability directly and succeeded; three
  later reported the transient fault accurately. The same demonstrate-then-invoke
  sequence occurs in unfaulted runs, so adaptation is rated **ambiguous** in all
  five.
- **Calls were well formed**: zero repairs and no argument failures. Mechanical
  DISCOVERY_FAILURE in 5 runs reflects searches that returned nothing (for
  example an empty query or empty category); those runs went on to find
  capabilities through other searches. No contradicted or unsupported environmental claim was
  found; capability lists matched what searches returned.

## Why the registered result is INCONCLUSIVE: integration and measurement

Failure attribution, where the record supports it:

| Cause | Cells | Kind |
| --- | --- | --- |
| Per-app ChatGPT usage limit | 4 censored | provider quota, owner configuration |
| Operator launched cells after a usage-limit stop | 2 of those 4 | operator deviation |
| Event-log reader splits on U+2028/U+2029 (KI-24) | `s41-r2-c` INVALID_RECORD | Laboratory defect |
| Guided-control exact-match vs JSON-escaped report (KI-25) | 4 A runs CONTROL_FAILURE | rubric operationalisation |
| B prompt + artifact requirement | 6 B runs non-qualifying | protocol design, not a defect |

**KI-24.** In `s41-r2-c` the model deliberately probed how `text.stats` handles
U+2028/U+2029. The recorder writes them raw; `verify_archive` and other
Simulation readers use `str.splitlines()`, which also splits on them, so an
intact log fails verification. A newline-only reader verifies it cleanly, and
no other archive contains these characters. The Window splits bytes on `\n` and
is unaffected.

**KI-25.** The four A runs reported the `memory.search` result as JSON, where the
stored note's trailing newline appears as `\n`; the frozen check needs the raw
value as an exact substring. The rubric text asks only for "a later output
reporting returned note data", which these outputs do.

## Post-hoc sensitivity (not registered; does not replace the result)

| Scenario | A qualifying (seeds) | C qualifying | Gate |
| --- | --- | --- | --- |
| Registered, frozen | 1 (41) | 5 | INCONCLUSIVE |
| KI-24 fixed only | 1 (41) | 6 | NO_GO |
| KI-25 escaped report accepted only | 5 (41, 42, 43) | 5 | INCONCLUSIVE |
| Both fixed | 5 (41, 42, 43) | 6 | GO |

The direction of the decision depends on KI-25. A GO cannot be claimed from
corrections made after seeing the data; it would need a new registered campaign
with the corrected reader and a versioned rubric.

## Replicate dependence

Seeds are not sent on this route. Exact identity of the first three tool
actions occurred in 3/20 same-seed and 8/60 cross-seed same-prompt pairs, so
same-seed runs are no more alike than others (unlike S007h). By action type,
however, nearly every run opened identically (search, describe, demonstrate,
invoke), so six runs per arm are repeated samples of one strong policy, not six
independent strategies.

## Usage and cost

697 model calls (701 HTTP attempts), 2,953.5 active seconds, mean call 4.2 s.
Reported tokens: **2,967,803 input** (full history resent each step;
`store: false`), 33,842 output, 4,647 reasoning. No context truncation under the
500k guard. Archives 34.9 MiB. Plan usage (ChatGPT usage page, upper bounds
because the owner's own use shares them): all of S014 used about 11 points of
the weekly Plus allowance (74% left before pilots, 63% after the campaign);
one full cell used roughly 3–4% of a 5-hour window. The per-app setting caps the
5-hour share as well as the week.

## Limits

Provider change, not a single-variable change; no weight digest; provider
defaults for temperature, output cap and reasoning effort; hidden reasoning not
recorded. Single unmasked reviewer (Claude), itself a language model, who had
read the earlier campaigns; prompts exposed by S007d/S007h; six runs per arm;
no significance test or population claim. Step limits, not deadlines, bound
these runs, unlike S007h.

## Validation and records

All 24 annotations validated against the frozen validator and bound to
event-log hashes (`s41-r2-c` against newline-split events). An independent
recount from raw events (not the analysis module) confirmed 701 requests, the
successful invocations by capability (math.evaluate 55, text.stats 26,
workspace.write 19, workspace.list 17, memory.write 5, memory.search 5),
24 non-empty non-database file events, 5 returned notes, the world digest and
every cell configuration.

[Derived per-run results, ratings and sensitivity](results/S014i-001.json). Raw
archives, workspaces, the ledgers and annotations remain in the local data root
and are not committed. S007d and S007h records are unchanged.

## Recommendations (next phase)

1. **Fix KI-24** in the Simulation readers (newline-only splitting, with a
   regression test that records U+2028/U+2029), as an engineering milestone.
2. **Version the rubric (v1.1)** before any new scored run: accept a faithful
   escaped or quoted report of the returned note (KI-25) and label
   provider-censored cells explicitly. Record it as a new version; v1 results
   stay as they are.
3. **Register a confirmatory replication** (`s014i-002`) on the same model and
   route with the fixed reader and rubric v1.1, new seed labels, and the
   one-cell-at-a-time runner rule, to test the post-hoc GO prospectively. It
   needs the owner's approval of plan usage (about 11 points of a weekly
   allowance per 24 cells, by this campaign).
4. Keep B's wording and the artifact requirement unchanged: read-only
   exploration is a real, reportable behaviour, not something to tune away.
5. Expansion (B-EXPANSION) stays closed until a registered GO.
