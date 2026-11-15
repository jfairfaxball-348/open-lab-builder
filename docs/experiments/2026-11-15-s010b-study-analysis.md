# S010b: evidence-linked comparative analysis

S010b implements general offline descriptive analysis and citation validation.
It does not change runtime treatments, historical rubrics/results, world releases
or the Window. Parent S010 remains incomplete until S010c. No new model request,
provider probe, download, installation or settings change was made.

## Engineering and scientific boundaries

ADR-0020 was written before code. Two additive research contracts,
study-annotations and study-analysis 1.0.0, join the two S010a research interfaces;
all remain outside runtime/world bundles. The protocol defines categories,
source pins, role separation, annotation evidence and all seven research gates.

Simulation adds `ols evidence analyze` and `ols evidence verify-analysis`.
Deterministic JSON and Markdown retain every declared cell, condition, role,
replicate/seed label, requested configuration, recorded identity/settings/policy,
context/repair/fault/recovery references and full artifact revision metadata.
Repeated call signatures and no-tool-call observations are descriptive facts,
not claims about internal goals. Unknown/unavailable information stays unknown.

Annotations distinguish investigator observation descriptions, exact attributed
agent claims and investigator assessments. Every entry validates cell/log pins,
sequence IDs and optional artifact observations; quotes must exactly resolve to
cited assertion text. Duplicate/stale/missing/wrong-kind references refuse output.
Missing ratings, uncertainty and disagreements stay visible. Citation validation
is not independent judgement of an assessment's truth.

Reports group strictly by role and condition. Within-role pairwise contrasts
expose all differing configuration pointers and recorded-field disagreements or
unknowns. Every contrast explicitly declines causal matching and independence.
Seven gates carry mechanical checks plus explicit human/external requirements;
there is no automatic launch approval, baseline-currency claim or autonomy score.

## Existing-data acceptance

The unchanged S010a export was analyzed retrospectively, including all eight
scheduled S007e/S008c cells and seven archives. This is reused development
evidence, not a newly preregistered evaluation or an exhaustive behavioural rerating.

| Condition | Planned | Archives | Missing | Provider-censored |
| --- | ---: | ---: | ---: | ---: |
| S007e C | 3 | 2 | 1 | 1 |
| S007e guided | 1 | 1 | 0 | 0 |
| S008c C | 3 | 3 | 0 | 0 |
| S008c guided | 1 | 1 | 0 | 0 |

Six source-linked entries preserve both positive and negative findings: the
guided direct specialist call succeeds and a later inspected note paraphrases its
representativeness limitation; S007e C1 records no direct specialist consultation;
S008c C1 records no direct statistics invocation. A separate entry retains S007e
C2's provider censoring, and one exact model statement is attributed as a claim
with uncertain interpretation. Guided action stays guided. Other unannotated
behaviour remains unreviewed; S008c's historical C2/C3 regression findings and
S007e's partial coverage remain exactly as previously reported.

The complete scheduled denominator survives; S007e C3 remains unstarted with null
observations. There are four role/condition groups and six descriptive contrasts;
none is certified causally matched or independent. All seven gates are present:
identity/registration have findings (opaque hosted weights, retrospective
inventory), provenance/denominator/annotation-link checks ran, and baseline
currency/isolation/reliability/allowance remain external requirements.

Source export.json SHA-256:
`24022908a57bc6dfe9b39cf8f598740c3ac83786efb492003993ab59b34a3d98`.
Analysis.json SHA-256:
`dbd4451df63e825f4c278dcb26dba4d1288da7e57b76e7fcb8ade78cc2ebb8d1`.
A [sanitized acceptance summary](results/S010b-001.json) retains source/analysis
pins, groups, contrasts and annotation evidence references. Full raw bundles,
annotation text and diagnostics stay local/ignored, not published.

Two analyses produced identical hashes. The CLI verified the report against its
external pin. A relocated export/report pair recomputed identically without the
original locations. Before/after snapshots of the export and report match, and
all seven original data-root archives still match every S010a copied/omitted
file digest and byte count. Added ChatGPT plan usage: zero requests; remaining
quota unknown. No specialist load/switch occurred.

## Verification and limits

Final checks: Builder Ruff/health passed with **361 tests** (50.06 s); Simulation
Ruff passed with **445 tests** (469.10 s). Implementation commit: `4af3a77`
(Simulation); Builder delivery is the S010b closing commit in git log.
[Detailed validation](../roadmap/validation/S010b.json).

Synthetic acceptance covers positive artifact production, idle/no-tool traces,
failed/provider-censored records, unstarted/launch-failed cells, role-separated
denominators, event-linked repair/context/fault/recovery traces, repeat signatures,
exact quotes, conflicts/uncertainty, missing ratings and unknown settings.
Tampered reports/exports, bad citations, unsafe output, changing inputs and
existing destinations refuse publication. Tests block network use and verify
unchanged sources, deterministic repeat and relocation. A test-helper argument
collision was corrected; no archive assertion was bypassed. Lint import ordering
was corrected. Final checks are recorded in the S010b validation snapshot.

Stable-source hashing is not an atomic defence against a privileged concurrent
writer. Report authenticity needs a separately trusted pin; preregistration
chronology and completeness of the original schedule need external evidence.
The aggregate normalized Simulation source pin requires the matching checkout
for exact recomputation of older reports. Single unmasked assessments and
correlated repeated prompts limit interpretation. Linux execution was not tested.
Window comparison and its browser/read-only acceptance are **S010c**, the exact
next milestone. Parent S010 is not complete.
