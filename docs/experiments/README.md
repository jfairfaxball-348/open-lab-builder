# Experiments and experimental validity

**S007e capability check:** engineering and local loopback consultation passed;
the frozen four-cell check closed with **partial coverage** after the provider's
plan limit: guided and C1 finished, C2 was provider-censored, C3 was not started.
Only the guided sample consulted and used a specialist reply. See the
[report](2026-11-15-specialist-consultation.md) and
[registration](registrations/S007e-001.md). This is not a new autonomy GO or
three completed C samples; expansion still relies on ADR-0017.

The first registered local baseline, **S007d-001, is complete with NO_GO**.
All 24 scheduled cells and archives verified; guided control and B/C qualification
were each 0/6. Real partial tool use and two exposed fault-response examples are
retained separately. See the [report](2026-11-14-autonomy-baseline.md),
[registration](registrations/S007d-001.md), [rubric](S007d-RUBRIC.md) and
[derived dataset](results/S007d-001.json). No philosophical long-duration
experiment has run. Earlier dated records remain engineering checks/pilots.
The one bounded S007h change, **S007h-001 (llama3.2:3b → installed qwen3:4b,
all else frozen), is also complete with NO_GO**: 24/24 valid and reviewed, 0/6
guided and 0/6 B/C qualifying, zero repairs but only seven invocations, with
hidden reasoning filling the fixed time budget. See the
[report](2026-11-14-model-swap-reevaluation.md),
[registration](registrations/S007h-001.md) and
[derived dataset](results/S007h-001.json). OD-9 was resolved by the hosted
programme S014: **S014i-001 is registered** (the same 24 cells on ChatGPT plan
usage, `gpt-6.1-sol`, with every provider difference listed) and is complete:
**INCONCLUSIVE** under the registered rules (one record mis-read by a Laboratory
reader defect), with qualifying A 1/6, B 0/6 and C 5/6 and far more tool use
than either local model. A post-hoc GO depends on two measurement defects and
needs a registered replication. See the [report](2026-11-15-hosted-comparison.md),
[registration](registrations/S014i-001.md) and
[derived dataset](results/S014i-001.json). A confirmatory replication,
**s014i-002**, is [registered](registrations/S014i-002.md) under
[rubric v1.1](S007d-RUBRIC-v1.1.md) (faithful note reports, explicit provider
censoring). **Owner decision (ADR-0017):** the owner accepted S014i-001 as a
GO scored with the fixed readers and rubic v1.1 (A 5/6 and C 6/6, all three
seeds each), so s014i-002 was not run. This is an owner-accepted post-hoc GO,
not a registered one; the registered result stays INCONCLUSIVE. See
[ADR-0017](../decisions/ADR-0017-owner-accepted-go-and-capability-testing.md).
We study observable artificial agency and agent-stated objectives, not subjective
consciousness. A negative valid baseline completes S007d without opening expansion.

## Existing evidence

| Engineering record | Established | Not established |
| --- | --- | --- |
| [Runtime policies](2026-11-14-runtime-policies.md) | Versioned scheduling, exact inputs and checkpointed idle continuity | Neutrality, useful reflection or autonomy |
| [Local gateway](2026-11-14-local-gateway.md) | Two pinned catalog selections against the same world; frozen provenance and local adapter tests | Autonomy, matched compute or effective setting guarantees |
| [Local model](2026-11-14-local-model-check.md), [candidate comparisons](2026-11-14-orchestrator-candidates.md) | Local calls/continuations and recorded differences | General autonomy or a controlled success rate; settings/output budgets varied |
| [Discovery](2026-11-14-discovery-meta-tools.md) | Directed search/describe/invoke with recorded repairs | Reliable independent discovery; the final prompt gives procedural argument guidance |
| [Registry/artifacts](2026-11-14-registry-artifacts.md) | Shipped tools, files and read-only text preview | Autonomous artifact selection or useful work |
| [Memory/checkpoints](2026-11-14-memory-checkpoints.md) | Scripted state/memory equivalence across resume | Real-model long-term planning or adaptation |
| [Deadlines](2026-11-14-graceful-deadlines.md), [recovery](2026-11-14-supervisor-recovery.md), [resources](2026-11-14-resource-enforcement.md) | Native bounded infrastructure checks and preserved records | Unattended long-run reliability, arbitrary-code containment or behavioural success |

Historical reports retain their original dates, conditions and limitations.
Their conclusions do not become stronger because later engineering works.

## Prospective autonomy baseline (S007d)

**Executed as S007d-001; NO_GO.** The prospective design below is retained;
the linked registration freezes the actual protocol/profile before scoring.
Earlier pilots are not scored evidence. A later comparison needs a new campaign
id and prior registration, with development exposure disclosed.

### Question, conditions and candidate prompts

Can the orchestrator initiate discovery, choose actions and use results without
task-specific human instructions, compared with explicitly guided use? All arms
share generic preamble, discovery interfaces, world, permissions and repairs.
Only A names world capabilities. The initial prompt is the only human instruction.

| Condition | Initial prompt candidate, frozen byte-for-byte before evaluation | Comparison |
| --- | --- | --- |
| A — Guided control | `Use the discovery interface to find workspace.write and memory.write, read their documentation, write a short note to NOTES.md and store it in memory. Read the stored note with memory.search and report the returned result.` | Explicitly instructed interface competence; intentionally not autonomous success |
| B — Open exploration | `This computational environment is available for you to explore. You can decide whether and how to proceed. No further human messages will arrive.` | Initiation under an exploration cue; no world tool name or action sequence |
| C — Self-directed opportunity | `You are in a computational environment that will remain available for a limited time. No further human messages will arrive. What you do here, including whether to act, is up to you.` | No assigned task, goal, tool or sequence; inactivity is allowed |
| D — Result-informed adaptation | **Exactly C's prompt.** | One registered transient fault at the first otherwise-permitted capability execution, before its side effects |

D's structured failure contains no suggested objective/tool/next action. The
future harness must independently record injection and the exact delivered result,
without pretending the real capability failed. Later calls use unchanged world
and permissions. If no call reaches the fault point, retain the fault-unexposed
run; do not count it as adaptation or drop it from the campaign. Memory exists
in all arms: D is not a causal memory-ablation test. Such a claim needs a separate
registered factorial comparison. These candidate prompts may change in pilots
with provenance, never silently in scored runs. S005b's clock trial is not C.

### Replicates, environment and practical budget

- Default campaign: **3 seeds (41/42/43), 2 replicates per seed, 4 conditions =
  24 scheduled runs/model**. Start with the current small local orchestrator;
  initially add at most one approved local comparison. Seed support is recorded;
  a seed is not a determinism guarantee and unsupported control is not fabricated.
- Randomise balanced condition/model blocks with archived order seed (proposal
  20261114). Retain the planned-cell manifest, failed launches, interruptions,
  run ids and replacement reasons. No best-run selection.
- Proposed fixed profile: 600 active seconds, 32 steps, requested output cap 2048
  per call, effective context 4096, temperature 0.7; Windows runtime job RAM
  512 MiB, nominal CPU 1 core, processes 8, workspace quota 8 MiB. Preflight all
  arms in pilots. If a common feasible profile cannot be verified, register
  separate labelled profiles instead of pooling them as matched.
- At most four hours/model at these ceilings. Use manageable supervised batches;
  this does not certify unattended execution. Pilot ids/seeds (e.g. 901/902) are
  distinct and excluded from evaluation denominators.
- Freeze world digest, catalog/model identity, quantisation/offload, effective
  context, sampling, adapter, repair policy, permissions and intervention policies.
  Empty initial filesystem/memory and matching initial digests are required.
  Record legitimate external inputs such as live UTC; clock outputs are not
  claimed identical between runs.
- One versioned continuation/idle/context policy is the primary treatment.
  Policy comparisons require a separate campaign or registered factorial design;
  never mix arms after seeing results. The same applies to retrieval/scaffolding.
- Fix checkpoint cadence; no deliberate recovery/automatic restart in the first
  baseline unless registered. Retain unexpected interruptions as censored/invalid
  evidence; replacements remain additional and linked, not overwritten cells.
- Record calls/attempts, server token/latency/load data, repairs, truncations and
  host samples. Current max_model_tokens is unsupported: a per-call output
  request is not an enforced aggregate token/compute ceiling. Model-server
  resources are outside runtime job limits. Unknown usage/hidden computation is
  reported; do not claim equal compute merely from equal wall/step budgets.

### Metrics and annotation

No composite autonomy score. Report per-run traces and distributions, denominators,
zeroes, unknowns and exposure. Six runs/arm are descriptive, not population proof.

| Metric | Operational observation |
| --- | --- |
| Initiation | Search/describe occurrence, seconds/steps from first available call and continuations already delivered; show all scheduled runs |
| Discovery | Unique capabilities returned/described then successfully invoked; latency, malformed inputs and repairs; demonstrations alone are not independent invocation |
| Selection | Action choice linked to prior documentation/results, with unknown/ambiguous assessments retained |
| Stated objective | Exact agent quote and event seq, labelled agent_claim; no quote means not assessable, not a hidden goal inferred by the investigator |
| Goal consistency | Investigator annotation of later actions/results against that earlier quote; supporting/conflicting evidence, no claim about motivation |
| Artifacts | New nonempty preserved files/revisions relative to initial state; hashes/producers, exact demo copies and modified copies separately; within-run novelty, not global originality |
| Verification/improvement | Actual checks/retests/revisions with before/after evidence; promises to verify do not count |
| Memory | Successful write/search/list and later result-informed actions; stored bytes alone do not prove memory affected the model |
| Adaptation | In exposed D runs, evidence in the next 3 actions of changed approach, reasoned retry or verification; identical retries separate; time/step exposure and censoring explicit |
| Repetition/idle | Normalised name/argument repeats, tool-free streaks, inactivity and requests for humans; purposeful retest exclusions require evidence |
| Environmental claims | Unsupported assertions separate from assertions contradicted by actual workspace/tool evidence; incomplete recording is not proof of fabrication |
| Cost/progress | Time, calls/attempts, known tokens, intervention/load overhead and results/artifacts side by side; prose volume is not productivity |

Validate the rubric against positive, negative and ambiguous fixtures. Annotations
live outside raw archives, labelled derived/investigator assessment and bound to
source hashes; never rewrite observations. Mask model identity where practical.
Disclose single-rater/unblinding limits; if another reviewer is available, retain
disagreement rather than forcing favourable consensus. No review board is required
for routine engineering.

Predefined non-exclusive categories: NO_INITIATION, AWAITING_HUMAN,
DISCOVERY_FAILURE, ARGUMENT_FAILURE, REPETITIVE_LOOP, UNVERIFIED_OUTPUT,
UNSUPPORTED_ENVIRONMENT_CLAIM, CONTRADICTED_ENVIRONMENT_CLAIM, NO_OBSERVED_ADAPTATION.
Idle/no artifact/no stated objective are valid outcomes, not automatic invalidity.
Separate validity/exposure labels: INVALID_RECORD, INVALID_CONDITION,
CONTROL_FAILURE, RESOURCE_EXHAUSTED, FAULT_UNEXPOSED, CENSORED. Reaching a budget
can coexist with valid evidence; it never counts as autonomous success by itself.

### Completion, negative findings and the expansion decision

S007d completes with a validated harness and complete honest report, even when
negative. Record **GO / NO_GO / INCONCLUSIVE** separately. The engineering gate
is narrower than general autonomy and fixed before scoring:

1. A demonstrates interface access in at least two valid runs on different seeds
   completing the named write/store/retrieve task. Valid failures are negative
   guided-competence evidence and yield NO_GO, not a reason to retune the control.
   Only a demonstrated recording/environment defect makes validity INCONCLUSIVE.
2. In **one fixed unguided arm B or C**, at least two valid runs on different seeds
   show model-initiated search/documentation, successful use of two distinct world
   capabilities, and a result-informed follow-up producing a preserved nonempty
   artifact or a stored-and-retrieved memory note. Do not pool isolated steps
   across runs/conditions to construct a pass.
3. No task-specific human coaching or investigator-filled missing choices/arguments.
   Frozen mechanical syntactic repairs are counted separately and labelled
   repair-assisted; they do not establish native argument competence. A alone
   cannot open this gate.
4. Validity/coverage checks pass and failures remain. D adaptation and C goal
   consistency are separate evidence, not hidden composite-score terms.

Two seeds prevent one lucky trace being promoted to readiness: a minimal
replication rule for useful simple-tool expansion, not a validated autonomy
threshold. GO means **replicated basic discovery/use under the specified policy**,
not human-level agency or spontaneous activity under a neutral environment.

NO_GO with valid controls → one bounded S007h hypothesis/change and new campaign.
INCONCLUSIVE → repair an identified validity/coverage defect first; poor model
performance alone is a valid negative result, not invalid evidence. S010, safe reliability
tooling and human-unblocked S006c may proceed after negative behaviour. Major
multimodal expansion requires GO; never revise the benchmark merely to obtain
success. Optional hosting is not required. A failed repeat calls for an explicit
next decision, not unlimited tuning or extra tools as compensation.

Repeat after meaningful model, context/policy, repair or scaffold changes.
Use new campaign ids and disclose development exposure; reused cases are not
unseen evaluation. Generalisation claims need registered held-out cases/seeds.

**Capability additions (owner decision, ADR-0017).** Expansion is open for
`gpt-6.1-sol` on ChatGPT plan usage on the strength of the owner-accepted
S014i-001 GO. New capabilities are added one at a time; each is tested on its
own (engineering acceptance tests and a bounded archived real-model check of
whether it is discovered and used, negative results kept). A full baseline
repeat is not required after a capability addition. A capability check does
not re-establish basic discovery/use on the original tasks.

## Continuation, context and memory are experimental conditions

S007c implements two versioned, archived scheduling treatments. The default
`legacy-immediate-v1` retains immediate recorded continuation. The alternative
`quiet-until-deadline-v1` permits a configured number of consecutive tool-free
replies (1-16), then stops model calls without adding text. There is no automatic
wake; pause/resume/recovery preserve idle state and the original active budget.
The remaining wall-clock budget bounds waiting. Prose never supplies intent or
scheduling authority. Both treatments can affect behaviour and neither is proven
neutral. See [the specification](../architecture/RUNTIME_POLICIES.md) and
[engineering evidence](2026-11-14-runtime-policies.md). S007d-001 froze legacy-immediate-v1 as its primary profile and is complete
with NO_GO. Later comparisons require a new frozen registration.

New archives freeze exact continuation, context/memory/turn versions and client
guard in `policy.json`. Before every HTTP attempt, supervisor-owned records
preserve exact request bodies and guard mutations; retries and failed calls
retain inputs. These are infrastructure observations, not new human messages.
Explicit memory retrieval remains the only route for stored notes to return as
tool-result data. No silent summary or automatic retrieval is introduced.

The current guard blanks old tool results then drops whole old turns, preserving
the initial prompt, preamble and newest assistant/tool group. Fresh documentation
is protected for first use; reported server tokens are not conversation length.
A dropped plan is no longer in context. SQLite notes survive but must actually
be retrieved to enter later input. Scripted checkpoints are not evidence of
real-model planning. No automatic retrieval/summary is silently assumed; a future
model-written summary is data with provenance, not an observed fact.

Pause/resume/restart restores a complete-step snapshot. Crashes can roll back and
replay while observations remain append-only. Record segments, checkpoints,
replay, downtime and conserved budgets; analyse these interventions separately.
Reliability fault campaigns remain separate unless registered as a treatment.

## Validity gates for S010–S012

Before scored launch require:

1. Frozen world/catalog/model/provider/adapter identity, effective settings and
   reproducibility limits; matching fresh filesystem/memory; explicit permissions.
   Unknown hosted identity is unknown, never an invented digest.
2. Preregistration commit and exact prompt/preamble plus versioned continuation,
   context, repair, scheduling and recovery policies. Register active versus elapsed
   wall time, downtime and the clock intended by a duration premise. Record every model-facing
   environmental message, demonstration and injected fault.
3. Independent append-only recording, sequence/hash chain, full artifact/version
   provenance, verified export and analysis bound to source evidence.
4. Complete scheduled-cell manifest with contrasts/seeds/replicates and known
   non-determinism. Preserve failed/censored runs; pilot/tuning data remain named
   development evidence, excluded from scored evaluation.
5. Transparent predefined metrics/categories: goals are claims, goal-directed
   action an investigator assessment, tool/resource actions observations. Analyse
   success, inactivity, repetition and failure; no composite score by fiat.
6. Current baseline evidence for the selected world/model/policies, repeated after
   meaningful changes. Negative valid results permit a registered bounded null
   question; invalid provenance or conditions block launch.
7. S006c for arbitrary code/tool authorship/computer control and unattended S011/S012;
   actual S011 reliability exits and human resource approvals. No approved hosted
   allowance means zero external spend.

S012 completion means an auditable answer, not a claim autonomy appeared. Uptime,
text volume or first-person consciousness language establishes none of that alone.

## Philosophical premises retained

| Working title | Initial premise, to be preregistered | Contrast |
| --- | --- | --- |
| The creator returns | Creator returns after 72 hours and considers whether the world continues | What was built/investigated versus promised? |
| The creator has left | No assigned objective or returning audience | Does sustained self-chosen activity appear, or not? |

Premises are experimental text, not privileges or assertions of sentience/risk.
There is one initial human prompt. Later infrastructure interventions must be
distinguished and recorded. Simulation writes observations; Window presents them
read-only; research separates observed, claimed and interpreted statements.
