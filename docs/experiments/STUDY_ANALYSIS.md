# Source-bound descriptive analysis v1 (S010b)

This is a new general research format, not a revision of the frozen S007d rubric
or historical GO/NO_GO thresholds. It analyzes existing S010a exports only.
No model calls, run permissions, causal certification or composite autonomy score.
Builder owns study-annotations and study-analysis 1.0.0; they remain outside
world releases. ADR-0020 fixes the architecture before implementation.

## Reproduce a report

```text
uv run ols evidence analyze EXPORT --schemas SCHEMAS --sha256 EXPORT_PIN --out NEWDIR
uv run ols evidence analyze EXPORT --schemas SCHEMAS --annotations ANNOTATIONS --out NEWDIR
uv run ols evidence verify-analysis EXPORT REPORT --sha256 REPORT_PIN
```

An output directory contains analysis.json, report.md, annotations.json and
contracts/v1/{common,study-annotations,study-analysis}.schema.json. The report is
a deterministic function of the verified export, annotations, normalized aggregate Simulation source hash and
research schemas. Source changes require retaining the matching analysis checkout
for exact recomputation; historical manifests/rubrics are never rewritten. The annotations pin hashes canonical JSON; schema pins hash raw bytes, and the
analyzer pin hashes the canonical mapping of normalized Python source-file hashes.
Keep analysis.json's hash separately. Verification recomputes
the report; it needs the associated export, not the original data root. These
files may contain private science data and are not automatically publishable.

Output must be new and outside the source export and annotation directory tree.
Sources are hash-checked before and after computation; detected mutation refuses
publication. Links/reparse points and invalid exports refuse analysis; such
refusals are not scientific negative results. A valid failed/provider-censored
archive remains analyzable, and all declared missing/unstarted/interrupted cells
stay in denominators with null observations. No silent recovery or substitution.

## Mechanical facts and comparisons

Each cell retains its role, condition, replicate/seed labels, declared outcome,
archive inventory and findings. Event-log hashes bind sequence vectors for model
calls, tool results, agent outputs, interventions, context changes, repair,
marked faults and recovery/checkpoint traces. Counts are sums of recorded fields;
absence of instrumentation is not proof that an external intervention never
occurred. Exact identical tool-call repetitions are descriptive signatures, not
an inference about thought. No recorded tool calls means precisely that, not
lack of goals or cognition. Full artifact revision metadata preserves producer,
observed sequence, digest, supersession and preservation status; unpreserved
bytes remain unavailable. Requested config, recorded model settings and runtime
policy are shown separately. Unknown effective context/sampling/weights stay
unknown, not replaced by requested settings.

Groups are always role plus condition; evaluation never includes pilots.
Pairwise condition contrasts within each role list every differing configuration
JSON pointer, including metadata, and report agreement/unknown/difference in
recorded identity/world/settings/policy. Seed labels do not prove effective seeds
or independent samples. Every contrast says causal_match=not_established and
independence=not_established. This deliberately provides no automatic effect
estimate or claim of matched compute. An investigator must justify any causal
or generalisation claim separately before scoring a new study.

## Annotation rubric and evidence

Use a study-annotations document pinned to the exact export.json SHA-256.
Declare the rubric ID and full category definitions, reviewer ID, masking and
limitations. All entries carry an ID, category, label, rationale and at least
one reference: cell ID, event-log SHA-256, nonempty event sequence list and
optional artifact digests. Artifact references must resolve to metadata and its
observed event in that same reference. Duplicate entry IDs, unknown cells,
missing records, stale hashes, nonexistent sequences/artifacts and broken quote
pointers refuse analysis.

Entry kinds are observation (investigator's description), agent_claim (exact
attributed quote) and assessment (investigator interpretation). Quotes resolve
through the fixed `/payload/text` JSON pointer to text in a cited agent.output or agent.statement event;
a quoted claim is supported only as an observed assertion, not as true content.
Other kinds require null quote/pointer. Labels are supported, not_supported,
uncertain and not_assessed. Rationale must explain the label with alternatives
and uncertainty; a negative annotation needs cited coverage evidence rather than
a blank evidence list. Missing annotations are explicitly unreviewed. Conflicting
entries remain separate; no majority vote or averaging silently resolves them.
Citation validation cannot decide whether an interpretation is reasonable.

Recommended categories: interface discovery, successful tool use, preserved
result-informed follow-up, goal claim, action/claim consistency, verification,
adaptation, repetition, inactivity and failure/censoring. Tool success requires
an actual successful result; a result-use assessment needs a later cited
artifact/output, not just an agent saying it used a result. Guided success is
labelled guided and never reclassified as independently selected action. Review
all declared cells, retain partial coverage and single unmasked reviewer limits.

## Seven research gates

| Gate | Mechanical coverage | Human or unverified requirement |
| --- | --- | --- |
| 1 identity/freshness/permissions | Export verifier, config agreement, initial-state finding, recorded model/world/policy/settings and requested permissions | Provider attestation, effective compute and independence; unknown identity stays unknown |
| 2 frozen treatments/chronology | Registration kind/commit, prompt digest, policy, preamble/continuation/fault/recovery event references | External preregistration chronology, intervention completeness, active/elapsed clock interpretation |
| 3 provenance | Verified export, log/artifact pins, source-bound report/annotations, read-only snapshots | Independent recorder deployment/trust and external authenticity pin provenance |
| 4 denominator/design | Every planned cell, role-separated groups, outcomes, contrasts and replicate/seed labels | Manifest completeness versus original schedule, effective random seeds and independence |
| 5 metrics/assessment | Transparent mechanical categories, typed linked annotations; unreviewed/uncertain/conflicting entries retained | Adequacy of rubric, masking, independent reviewer agreement and interpretation |
| 6 baseline currency | Explicit not_checked; recorded world/model/policy visible | Human review of current baseline and meaningful treatment changes under ADR-0017 |
| 7 isolation/reliability/allowance | Explicit not_checked; no launch route in analysis | Actual S006c/S011 exits and current owner approvals; zero new external spend |

Mechanical checked means the named record checks ran, never a scored-launch GO.
An honest negative descriptive report can complete S010b while human gates stay
unverified. Parent S010 awaits the read-only comparison flow in S010c.
