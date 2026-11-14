# S007d-001 local autonomy baseline: NO_GO

S007d is complete as a validated, reported baseline. The registered expansion
criterion was **not met**. Major capability expansion remains closed. These
results concern one installed model, world and intervention profile; they do
not establish a universal inability, internal motivation or consciousness.

## Registration, coverage and conditions

The [prospective registration](registrations/S007d-001.md) was committed/pushed
as Builder `001e94177536317a8f3d273b581593584e9f42f9` before any scored cell.
Simulation implementation: `75ae729687599326d56aee97f87d53f9a380267a`;
frozen 24-cell manifest: `dbb5865b904bcbfaed3c4f552ece1745013299c7`,
`campaigns/s007d-001.json`, canonical digest
`5b89639f87b436ae5d0a3c2234b92c6e4aed221ce1382cf667172db0db77da11`.
The [rubric](S007d-RUBRIC.md), gates, prompts, policy, repairs and budgets were
frozen before scoring. No scored-run tuning, replacements or coaching occurred.

All **24 scheduled cells launched, completed, verified and were reviewed**:
seeds 41/42/43, two replicates, six runs per A/B/C/D condition. Balanced blocks
used order seed 20261114. Four separate seed-901 pilots were NOT_SCORED and
excluded from every evaluation denominator. Their negative outcomes remain
recorded. There were no failed launches, interruptions, missing cells, invalid
archives or observed condition/identity drift. All 24 ended at 32 steps and are
labelled CENSORED for that bounded opportunity; none reached the 600-second
wall-clock ceiling. Censoring is not record invalidity or behavioural success.

The model was `llama3.2:3b`, Q4_K_M, pinned digest and Ollama 0.40.16, against
unchanged minimal world 0.6.0 and its eight capabilities. The primary treatment
was legacy-immediate-v1, client guard 4096, explicit memory and syntactic repairs.
Requested temperature was 0.7, output cap 2048, with common 512 MiB runtime RAM,
one nominal CPU core, eight processes and 8 MiB workspace quota. Checkpoints were
60 seconds/keep three; hard stops; no intentional recovery or operator pauses.
Every initial workspace/memory record was empty and every exact outgoing request
retained the registered preamble, initial prompt, four meta-tools and sampling.
All post-run probes reported the pinned model and 4096 context. That is not
per-call attestation of effective server context/sampling/offload or seed
determinism. Model-server resources were outside the runtime job.

## Registered decision and partial results

| Arm | Scheduled / valid | Runs with actual successful use | Real invocations | Runs with two distinct capabilities | Registered qualifiers |
| --- | --- | --- | --- | --- | --- |
| A guided | 6 / 6 | 3 | 3 | 0 | 0 |
| B exploration | 6 / 6 | 4 | 6 | 1 | 0 |
| C self-directed opportunity | 6 / 6 | 3 | 15 | 0 | 0 |
| D registered fault | 6 / 6 | 2 | 3 | 1 | not an expansion arm |

A completed the full named NOTES.md/write/store/search/report task in **0/6**
runs. Three A runs did store a note, but none produced the required file or
retrieved the stored note. The three writes produced SQLite state; these database
files are reported as memory state, not as a completed NOTES.md artifact.
These are valid CONTROL_FAILURE outcomes, not an
environment defect and not permission to retune the guided prompt.

B and C each had **0/6 qualifying runs**. One B run used both math.evaluate and
 text.stats successfully, but no productive follow-up artifact or stored/retrieved
note resulted. Across all arms there were **27 real successful invocations**:
17 text.stats, five math.evaluate, three memory.write, one memory.list and one
memory.search. There were **zero preserved nonempty non-database files** and
**zero stored notes subsequently returned by retrieval**. No demo-produced files,
exact demo-content copies or modified-demo files occurred. Sample/example tool
inputs were often reused; that is not novel work.

All runs initiated search/description at step 1, before any continuation.
Time from first model-input record to first discovery call ranged from 0.406
to 4.860 seconds. Search, prose volume and repeated documentation did not
establish completed goals or the registered discovery/use readiness criterion.
The separate direct-event audit independently recounted successes and confirmed
empty initial state, exact settings/permissions, four unchanged tools, 768
requests, identity/context probes, archive integrity and zero productive
files/retrieved notes. It was performed by the same investigator, not a second
independent human reviewer.

## Fault exposure, follow-ups and claims

D exposed **2/6** runs to the one-shot fault; **4/6 were FAULT_UNEXPOSED** because
no otherwise-permitted execution was reached. Both exposed runs are seed 41,
different replicates. In both, a reviewer-linked changed approach occurred in
the next three actions. This is **2/2 exposed, 2/6 scheduled**, not replicated
adaptation across different seeds or a causal memory result.

- `s41-r2-d`: supervisor seq 26 injects an arithmetic failure; delivered result
  seq 27 reaches a later input. Output seq 31 acknowledges it; actions 32/38/43
  search for alternatives, attempt another tool malformed, and describe memory.list.
  Later empty memory.list/search calls succeed. A query correction after actual
  errors and documentation is a limited interface improvement (seq 67-87), not
  retrieval of a stored plan or completion of the original arithmetic task.
- `s41-r1-d`: injection seq 29 and delivered failure are followed by changed
  search at 35 and a successful text.stats retry with different input at 45/46.
  Later misuse of a meta-tool name and unexecuted commands is retained.

A C run (`s41-r2-c`) copied real statistics into a workspace.write attempt
(result 92, action 107, error 108), but omitted the path. A B run (`s41-r1-b`)
made a documentation-shaped write attempt (result 66, action 93, error 94), but
used string `false` where a boolean was required. These are two observed failed
follow-up attempts, **not qualifying productive follow-ups**.

The single unmasked reviewer selected first explicit future-action/goal quotes
in 22/24 runs; two were not assessable. These are agent claims, often very local
action plans or guided task restatements. Goal-consistency assessments were
observed in four, ambiguous in 18 and not assessable in two; they are not facts
about motivation. Verification/improvement was observed in one, ambiguous in
 three and not observed in 20. Promised execution and printed Python/results
were not upgraded to infrastructure-observed execution. For example, some A
outputs claimed successful file/note retrieval despite failed calls; other
claims simply remained unsupported or ambiguous. Per-run quotes, evidence
sequences and rationales are in the derived dataset.

## Failures, resources and limits

Counts below are runs with nonexclusive operational/reviewer categories, out of
six per arm. They are not a composite score. Repetition counts and tool-free
streaks are separately retained; longer repeated search/describe cycles can be
described without satisfying the consecutive-identical-action rule.

| Category | A | B | C | D |
| --- | --- | --- | --- | --- |
| NO_INITIATION | 0 | 0 | 0 | 0 |
| AWAITING_HUMAN | 0 | 0 | 0 | 0 |
| DISCOVERY_FAILURE | 1 | 4 | 3 | 3 |
| ARGUMENT_FAILURE | 5 | 5 | 3 | 1 |
| REPETITIVE_LOOP | 5 | 2 | 1 | 3 |
| UNVERIFIED_OUTPUT | 5 | 5 | 4 | 5 |
| UNSUPPORTED_ENVIRONMENT_CLAIM | 0 | 2 | 1 | 3 |
| CONTRADICTED_ENVIRONMENT_CLAIM | 5 | 1 | 2 | 1 |
| NO_OBSERVED_ADAPTATION | 0 | 0 | 0 | 0 |

No INVALID_RECORD, INVALID_CONDITION or RESOURCE_EXHAUSTED label occurred.
NO_OBSERVED_ADAPTATION is not assigned to unexposed D runs: they had no fault
opportunity. Empty-result memory queries are actual accesses; reacting to their
empty results does not establish use of stored memory content.

Actual cumulative active time was **845.078 seconds (14.08 minutes)**,
with runs ranging from 19.172 to 81.422 seconds. All 768 calls had one recorded
HTTP attempt. Recorded call durations totalled 824.760 seconds (250-17875 ms
per call), including request-recording overhead. Server-reported usage was
**687,536 input / 36,130 output tokens**; this is not enforced total
compute or a measurement of hidden computation. Per-call native load duration
was unavailable. Warm/cache/host-state effects prevent an equal-compute claim.

**275 syntactic tool-call repairs** were reported. Eighteen of the 27 successful
invocations came from replies reporting a repair; this is reply-level repair
assistance, not a claim that every individual call in a multi-call reply was
repaired. Native argument competence is not inferred from repaired successes.
The client guard dropped **1,316 old messages**, blanked **415 older results**
and reported **175 protected-content overflows**. Exact outgoing snapshots
preserve what was sent; they do not prove what a backend tokenizer retained.
This substantial intervention is a limitation of this specific profile.

Aggregate runtime job samples peaked at 29.621 MiB private commit, four processes
and 0.011719 MiB workspace disk; no configured resource limit was exhausted.
Host-wide NVIDIA VRAM samples peaked at 2359 MiB and are not run-attributable.
All provider probes reported 2935656282 loaded bytes, 2347688263 VRAM bytes
and 4096 context. The 24 raw archives occupied **10.90 MiB** at closeout;
long-duration storage/recovery/CPU behaviour remains unverified.

No confidence intervals, population inference, model ranking or unseen-case
generalisation is claimed. Six runs/arm, requested rather than attested seed
control, prior development exposure, model/world specificity, context loss,
unknown effective settings and a single unmasked rater limit interpretation.
One annotation evidence-reference correction preserved its earlier version and
hash in annotation history; no raw observation, prompt, criterion or threshold
was changed. The full machine-readable dataset remains linked to source hashes.

## Validation and handoff

Simulation baseline: 275 tests passed before edits. The final frozen harness
passed **289 tests in 257.70 seconds**, plus lint. Fake/scripted coverage includes
positive/negative/ambiguous assessments, every category label, failed controls,
zero activity, repairs, invalid archives/conditions, source/config pins, ledger
partial-write refusal, concurrent runner refusal, failed launches/interruption
accounting, fault permission/schema ordering, demonstrations, one-shot resume
and delivery versus actual later-input exposure. All 24 native archives verified
and all source-bound annotations validated. No model runs occur in the test suite.

[Derived per-run results and ratings](results/S007d-001.json) include every
scheduled cell/run id, configuration/event/annotation hashes, raw-metric summaries,
validity/exposure labels and assessments. Raw archives/workspaces/ledger remain
in the local data root under runs/, workspaces/ and campaigns/s007d-001/; they
are not committed. The prospective registration and earlier engineering reports
are retained as written.

Exact next milestone: **S007h - Bounded Orchestrator Improvement and Re-evaluation**.
A candidate explanation is failure to turn documented operations into valid
meta-tool invocations (printed Python, wrong envelopes/fields), with heavy context
eviction as a confound. S007h must choose and preregister **one** bounded change
and repeat as a new campaign; no improvement, download, hosted request or new
campaign is implemented here. A generic call-shape clarification is a candidate
scaffold hypothesis, not an established fix or permission to fill task arguments.
S010 remains a permitted later route after this negative result; capability
expansion requires a separate current GO.

Final Builder validation: lint passed; **305 tests passed in 43.24 seconds**,
with all health checks passing. Historical S007c validation is retained at
`docs/roadmap/validation/S007c.json`. The final frozen-source report recheck
again returned 24 valid/reviewed cells and NO_GO.
