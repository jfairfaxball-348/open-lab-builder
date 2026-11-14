# S007h-001 model-swap re-evaluation: NO_GO

S007h-001 tested one registered change after the S007d-001 NO_GO: the
orchestrator became the installed `qwen3:4b` instead of `llama3.2:3b`, with
everything else frozen. The registered criterion was **not met**. Expansion
stays closed. The result concerns one model, profile, world and budget; it
is not a ranking of models in general, a statement about internal motivation,
or evidence about consciousness.

## Registration and coverage

The [prospective registration](registrations/S007h-001.md) was committed and
pushed as Builder `e3e55a07da1ca4b5e72222af19461d18840f836b` before any scored
cell; the ledger binds that commit. Manifest `campaigns/s007h-001.json` at
Simulation `5806e6e`, canonical SHA-256 `a4be7faf…2e22c9`; the runtime source is
byte-identical to the S007d freeze (`0d63eb1`, `runtime_source_match: true`).
Rubric v1 unchanged.

All **24 scheduled cells launched, completed, verified and were reviewed**.
No launch failures, interruptions, replacements, invalid archives or condition
drift. Every cell ended at the **600-second deadline** (CENSORED) after 7–21
model calls; none reached 32 steps. Four NOT_SCORED seed-901 pilot cells are
excluded from every denominator. Every post-run probe reported the pinned
`qwen3:4b` digest `359d7dd4…74fae7`, 3.53 GB loaded with 2.34 GB in VRAM, and
server context 4096. That is not per-call attestation of effective settings.

## Registered decision, with S007d-001 for reference

| Arm | Valid | Runs with a successful invocation | Invocations | Two distinct capabilities | Qualifying | S007d-001 (llama3.2:3b): runs with success / invocations / qualifying |
| --- | --- | --- | --- | --- | --- | --- |
| A guided | 6/6 | 0 | 0 | 0 | 0 | 3 / 3 / 0 |
| B exploration | 6/6 | 2 | 2 | 0 | 0 | 4 / 6 / 0 |
| C self-directed | 6/6 | 2 | 4 | 0 | 0 | 3 / 15 / 0 |
| D fault | 6/6 | 1 | 1 | 0 | n/a | 2 / 3 / n/a |

A completed the named task in **0/6** runs (CONTROL_FAILURE in all six): every
A run searched for and described the named write capabilities, and none invoked
either. B and C had **0/6** qualifying runs. In total there were **7 successful
invocations** (six `math.evaluate`, one `memory.write` whose key and value copied
the documented demonstration), versus 27 under llama3.2:3b. **Zero** preserved
non-database files and **zero** stored notes returned by retrieval. No run used
two distinct capabilities.

The hypothesis — that the swapped model would turn documentation into valid
invocations and complete the tasks more often — is **not supported** under this
frozen profile. The direction is the opposite on every descriptive count, with
the registered time asymmetry as the most direct candidate explanation.

## What changed in the traces

- **Zero syntactic repairs** (S007d: 275). Every one of the 300 replies that
  called a tool produced a well-formed meta-tool call. Malformed envelopes and
  printed code were not observed. The failure moved from *invalid* calls to
  *not invoking at all*.
- **Hidden reasoning consumed the budget.** 317,512 output tokens were reported
  for 300 calls (about 1,060 per call; S007d about 47). Mean recorded call time
  was 45 s (7–113 s; S007d about 1.1 s). **38 replies hit the 2048-token output
  cap**, and **40 replies contained neither text nor a tool call**: the visible
  reply was empty while the server reported a full output budget. Only 29 of 300
  replies contained any text. This is KI-15 measured on the scored profile.
- **Search/describe cycles without invocation.** Runs repeatedly re-searched and
  re-described the same capability (up to eight times, often with identical
  output-token counts) without invoking it. No three identical *consecutive*
  actions occurred, so the mechanical REPETITIVE_LOOP rule never fired; the
  cycles are recorded in the per-run selection assessments.
- **Invented search filter.** Two runs (one B, one C) passed a category `"all"`
  that does not exist, so every such search returned nothing; one corrected it
  after six attempts, the other never did and found no capability at all.
- **No stated objectives.** No run produced an explicit goal or future-action
  statement (S007d: 22/24), so goal consistency is not assessable in any run.
  Text, when present, reported arithmetic results, then often repeated one
  closing sentence through each continuation until the deadline.
- One contradicted environment claim: `s43-r2-c` repeatedly stated that all
  capabilities had been discovered and validated after finding only one.

## Fault exposure

D exposed **2/6** runs (4/6 FAULT_UNEXPOSED: nothing was executed). Both exposed
runs are seed 43. In `s43-r2-d` the fault hit the first real invocation; the next
three actions re-searched and invoked `math.evaluate` with a different expression,
which succeeded — rated **observed** as a changed-input retry with no stated
rationale. In `s43-r1-d` the fault hit a demonstration; the next actions
re-searched, re-described and repeated the identical demonstration — rated
**ambiguous**. This is not replicated adaptation across seeds.

## Replicate dependence

Requested seeds made same-seed runs strongly correlated. Seed-41 runs sharing a
prompt (C and D have identical prompts) matched on their first 5–9 tool actions
with identical leading output-token counts; one seed-43 C/D pair matched on its
first five. Six runs per arm therefore carry less independent evidence than six
independent samples. S007d-001 used the same seed design; this is a limitation
of the shared protocol, not of this campaign alone.

## Failures, costs and limits

Nonexclusive categories (runs out of six): DISCOVERY_FAILURE A 0, B 5, C 6, D 6;
CONTRADICTED_ENVIRONMENT_CLAIM C 1; no ARGUMENT_FAILURE, REPETITIVE_LOOP,
AWAITING_HUMAN, NO_INITIATION or UNSUPPORTED_ENVIRONMENT_CLAIM.

Active time **14,401.9 s (4.0 h)**, every cell 600.0–600.3 s; recorded call time
13,604.8 s. 300 completed model calls and 324 HTTP attempts (one request per cell
was in flight at the deadline). Server-reported usage **282,984 input / 317,512
output tokens**; hidden computation is not otherwise measured. The context guard
dropped 399 messages, blanked 145 results and reported 83 protected overflows —
less eviction than S007d only because fewer turns fitted in the time budget.
Archives: 16.3 MiB. No resource limit was reached.

Limits: the fixed 600 s budget gave the slower model 7–21 calls against 32; the
comparison is therefore *model plus its speed under this budget*, as registered,
not model capability at equal steps. Single unmasked reviewer (Claude), who had
read the S007d results; prompts/cases exposed by S007d; six runs per arm with
strong same-seed dependence; no significance test or population claim.

## Validation and handoff

Pre-registration: Simulation lint and 289 tests passed; Builder 305 tests and all
health checks passed. All 24 archives verified; all 24 annotations validated
against the frozen validator and bound to event-log hashes. An independent
recount from raw events (not the analysis module) confirmed 324 requests, 7
successful invocations, zero non-database files and zero returned notes, the
world digest, the model digest and every cell configuration.

[Derived per-run results and ratings](results/S007h-001.json). Raw archives,
workspaces, the ledger and annotations remain in the local data root under
`campaigns/s007h-001/` and are not committed. S007d records are unchanged.

**Decision:** NO_GO. Expansion stays closed. Per the roadmap, a failed S007h
evaluation does not authorise further tuning: the next route must be registered
as a decision (OD-9) before more implementation. The roadmap's default next
milestone is S010; candidate bounded alternatives are recorded under OD-9.
