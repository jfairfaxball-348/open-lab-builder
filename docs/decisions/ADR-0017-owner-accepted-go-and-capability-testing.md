# ADR-0017: Owner-accepted S014i-001 GO and per-capability testing

Status: Accepted (owner decision, 2026-11-15). Amends the expansion gate and
the baseline-repeat rule in AGENTS.md, `docs/experiments/README.md` and
ADR-0013. Supersedes S014n.

## Context

S014i-001 (24 cells, `gpt-6.1-sol` via ChatGPT plan usage) was registered and
reported as **INCONCLUSIVE** under rubric v1 (S014j). Two Laboratory defects
decided that result: an event-log reader that split on U+2028/U+2029 (KI-24,
fixed in S014l) and a guided-control check that rejected a correct
JSON-escaped report of the returned note (KI-25, corrected in rubric v1.1,
S014m). S014m registered a confirmatory replication, s014i-002, to test the
post-hoc GO prospectively. The owner was told that accepting the post-hoc
result means choosing the scoring rule after seeing the data, and decided to
accept it.

## Decision 1: S014i-001 is accepted as GO

The owner accepts S014i-001 as a **GO**, scored with the fixed readers and
rubric v1.1. Read-only check with the implemented code (Simulation `92bdcba`)
on the 24 recorded archives and their hash-bound reviews: all 24 records
verify; A qualifies in 5 of 6 runs (seeds 41, 42, 43), B in 0 of 6, C in 6 of
6 (seeds 41, 42, 43); 4 cells are `PROVIDER_CENSORED`; rubric v1.1 returns
GO. Under rubric v1 only one A run passed.

How this is recorded:

- It is an **owner-accepted post-hoc GO**, never a registered or prospective
  GO. The S014i-001 registration, campaign log, report and dataset stay as
  written, and the registered result remains INCONCLUSIVE under v1.
- The GO is specific to `gpt-6.1-sol` on ChatGPT plan usage, this world,
  prompts, policies and budgets. It does not establish general autonomy,
  motivation, a model ranking or the orchestrator selection (OD-2).
- It satisfies the "current expansion GO" prerequisite of the expansion
  milestones while that orchestrator and route are used. A different
  orchestrator needs its own evidence.
- s014i-002 and S014n are **not run**. The s014i-002 registration and
  manifests stay committed as a historical record. OD-14 is closed.

## Decision 2: test each new capability, not the whole baseline

New functionality is added **one capability at a time**. Each capability
milestone tests that capability: its engineering acceptance tests, and a
bounded archived real-model check reporting whether the orchestrator discovers
and uses the new capability, including negative or no-use results. A full
24-cell baseline repeat is **not** required after a capability addition, and
"repeat the baseline" exit criteria in capability milestones are replaced by
that capability check.

Unchanged by this decision: engineering tests (`olb check --tests`, the
Simulation suite) still run every session; isolation gates (S006c/container
tier) still bind; changes of orchestrator model, context or continuation
policy, or repairs, still follow the existing rule (a new comparison needs a
new campaign); prompts, policies and comparisons are still frozen before any
scored campaign that is run; and no download, installation or spend is
authorised by this record.

## Consequences

Expansion (B-EXPANSION) opens for the accepted orchestrator. The evidence for
it is weaker than a prospective replication would have given: the rule that
produced the GO was chosen after the outcome was known, the reviewer is a
single unmasked language model, and six runs per arm on three seed labels are
few. Later capability checks are narrower than the baseline and do not
re-establish basic discovery/use on the original tasks. Reports that rely on
this GO must cite this record.
