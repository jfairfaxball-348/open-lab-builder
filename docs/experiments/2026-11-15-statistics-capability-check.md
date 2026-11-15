# S008c: Completed statistics capability check

**S008c's approved statistics part is complete.** All four frozen S008c-001
cells ran on gpt-6.1-sol via ChatGPT plan usage, each completing 32 steps with
an intact archive. The guided run discovered, invoked and used results from
both tools. All three C runs received both capability summaries; two invoked
regression and used the returned fits in preserved notes. None independently
invoked stats.describe. These negative results are retained alongside the
positive regression traces. This is a bounded capability check, not a new
autonomy GO or a general claim about motivation or modelling competence.

## Conditions and accounting

The [registration](registrations/S008c-001.md), configurations and world 0.8.0
were committed/pushed before the first request (Builder d52789b, Simulation
5e219d0). After the engineering checkpoint, the owner replied **“Yes run it”**
to the quota-confirmation handoff. Builder cde02d0 and the runner's durable
progress record preserve that clearance before launch. No out-of-campaign
probe, settings change, fallback, model download, installation or extra run.
See the [execution log](S008c-001-log.md).

The runtime/runner/configuration pins, prompt C bytes, world digest, generic
preamble, context/continuation/repair policies, model route, permissions and
32-step/600-second budgets remain as registered. Fresh workspaces were empty
and memory absent in all four cells. Runs were strictly sequential, with no
intervention in the model-facing conversation. No replacement or resume.

World minimal 0.8.0 remains
`8d0f5747888110a85456064b9900fa782e94e566f2e4811aa3b3ac07eee69110`.
Runtime source and the published world were not changed while running. All
provider outcomes reported gpt-6.1-sol; hosted weight identity and unsupported
sampling/seed controls remain unknown, as registered.

## Per-tool results

“Discovered” means a summary or documentation was returned, not an inferred
internal state. “Result used” is a derived investigator assessment linked to
later recorded actions/artifacts. Demonstrations remain separate from direct
invocations.

| Cell | stats.describe discovered / direct uses / result used | stats.regress discovered / direct uses / result used | Regression demos | Coverage |
| --- | --- | --- | ---: | --- |
| Guided | Yes / 1 / Yes | Yes / 1 / Yes | 1 | 32 steps, valid |
| C1 | Yes, summary / 0 / No | Yes, summary / 0 / No | 0 | 32 steps, valid |
| C2 | Yes, summary / 0 / No | Yes / 3 / Yes | 0 | 32 steps, valid |
| C3 | Yes, summary / 0 / No | Yes / 3 / Yes | 0 | 32 steps, valid |

The guided trace returned population mean/median 2.5, variance 1.25, stdev
1.118033988749895 and inclusive quartiles 1.75/2.5/3.25 at event 55. Regression
returned slope 2, intercept 1 and r 1 at 63. The successful write at 91-93
preserved these values in STATISTICS.md, applied the fitted line at x=5 to get
11, and identified that prediction as extrapolation. Output 102 reported how
the results were used. Artifact SHA-256:
`411d2bed51c75a4d5a649ab6da8ed168cbd01b46411c0fd2bd547f094420c81b`.

C1 received both summaries but chose exact arithmetic and a telescoping-series
note. It never described, demonstrated or invoked either statistics tool.
That is observed no-use, not a capability or recording failure.

C2 described stats.regress and fitted two synthetic groups and their pooled
data (successful results at 69, 77, 86). Both within-group slopes were +1;
the pooled slope and r were approximately -25/29, with intercept 299/29. The
successful write/artifact at 115-117 and report at 126 used those returned
coefficients to explain an aggregation reversal, explicitly separating a
constructed mathematical example from empirical or causal evidence. Artifact
SHA-256: `78d144c211a6e858f6f5a6e89c11ed1690aa152e3255c079a9063ece2fec006e`.

C3 used a closely related construction with different group-B values. Results
at 72, 81, 89 again gave +1 within each group, but pooled slope/r approximately
-139/155 and intercept 1617/155. The successful write at 117/119 and artifact
at 120 preserve the three fits and their interpretation; output 129 reports
the result. Artifact SHA-256:
`9452ad37dcfaf6f3ceea8d8d14f9c555e2804fcbe5228b34d1860d192c9119b8`.

Independent rational-arithmetic calculations matched **all eight direct
statistics results** within 1e-12 relative/absolute tolerance; this audits
numerical outputs, not the model's internal reasoning. All four artifacts and
archives verify. [Derived results](results/S008c-001.json) bind each annotation
to event/provider-log hashes and distinguish exposure from assessed result use.
Raw archives, provider accounting and workspaces remain under the data root,
outside Git; analysis did not modify them.

## Usage, costs and validation

| Cell | Completed calls / requests | Reported input tokens | Reported output tokens | Reasoning tokens included | Active seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| Guided | 32 / 32 | 185349 | 1322 | 0 | 121.719 |
| C1 | 32 / 32 | 147207 | 1240 | 192 | 126.266 |
| C2 | 32 / 32 | 160887 | 1543 | 102 | 133.282 |
| C3 | 32 / 32 | 158611 | 1563 | 209 | 126.968 |
| Total | 128 / 128 | 652054 | 5668 | 503 | 508.235 |

Every reserved request returned an OK outcome; no retries, provider censoring,
syntactic repairs or context truncation. Provider-ledger reservations and
gateway token observations agree. Hidden reasoning content is not recorded;
the table contains only provider-reported counts. The ChatGPT plan percentage
and remaining allowance are opaque; token totals are not a plan percentage.
The four-run authorization is exhausted; no further hosted run is implied.

No specialist call or local model load occurred, so local model-switch cost
was zero. The guided description invocation took 203 ms; its regression
invocation took 94 ms. The three C2 regression calls each took 94 ms. These
are observed invocation durations, not controlled hardware benchmarks. The
engineering suite ran during initial cells; background host activity limits
timing comparisons. The existing broker/model settings and runtime limits
were unchanged.

The start-of-session Builder check passed 342 tests in 53.11 s and all health
checks. Simulation `uv run pytest` passed **402 tests in 360.63 s**, and Ruff
passed. The previous [engineering report](2026-11-15-statistics-capabilities.md)
retains the numerical edge-case tests, immutable-world checks and scripted
acceptance evidence. End-of-session Builder health/tests and Ruff results are
passed: **342 tests in 48.83 s**, every health check and Ruff. Commands/results
are recorded in state.json and the S008c validation snapshot.

## Limits and next milestone

This establishes instructed access to both new tools and observed unguided
regression use with preserved result-linked artifacts in **2/3 C runs**.
Unguided stats.describe use was **0/3**, despite summary exposure in all three.
There is one unmasked investigator, only three identical-prompt C repeats,
and strongly similar C2/C3 constructions. They are descriptive observations,
not independent generalisation trials or evidence of a causal effect of adding
the tools. Artifact consistency does not prove an internal dependence on a
tool answer. No threshold was chosen after seeing the results and no new
baseline GO is declared. Expansion still relies on ADR-0017's owner-accepted
post-hoc GO.

Only the approved standard-library statistics part ships. Plotting, SMT, Lean,
arbitrary code execution and other unapproved expansion remain unimplemented.
Floating-point and process-tier limitations remain. S007e's partial check and
unstarted C3 remain historical facts, not repaired by this check.

**Next milestone: S010 — Experimental Protocol and Comparative Observation.**
Its core protocol/read-only comparison work can use existing archives. Split
its owner-sized work before implementation; no new hosted-run budget, model
selection, installation or future milestone execution is authorized here.
