# S008c: Statistics engineering ready; hosted check pending

**S008c is incomplete.** The approved standard-library statistics part is
implemented and its engineering acceptance passes. The four-cell real-model
check is prepared but **unexecuted**: the handoff requires owner confirmation
of plan availability after S007e's quota refusal, and that confirmation has
been requested but not received. There is no probe, retry, settings change,
fallback or extra hosted request. All four S008c cells remain unstarted.

## Implemented scope

Minimal world **0.8.0** adds two ordinary Python capabilities:

- `stats.describe(values)`: 1-10000 finite numbers, each in [-1e12, 1e12];
  count, mean, median, **population** variance/stdev (divisor n), and inclusive
  q1/q2/q3 quartiles. A singleton has zero population variance and all quartiles
  equal to its value. Booleans, numeric strings and missing values are rejected.
- `stats.regress(x, y)`: equal-length lists of 2-10000 bounded finite numbers;
  ordinary least squares **with an intercept**, returning count, slope,
  intercept and Pearson r. Constant x is rejected. Constant y gives slope 0,
  its value as intercept, and r null (undefined correlation). Duplicate x
  values are allowed when x is not entirely constant. Scale normalization
  avoids squared-span underflow; unrepresentable finite outputs are rejected.

Both use the standard library only, accept numeric data rather than executable
expressions, and require filesystem/network permissions **none**. They neither
read files nor request subprocess, GPU or model privileges. Existing runtime,
broker, context, continuation, repair, observation and specialist code are
unchanged. There is no new dependency, download, installation, settings change,
plotting, SMT, Lean or arbitrary-code capability. Build/test `uv sync` found
the environments already synchronized.

Manifests contain complete input/output schemas, numerical conventions,
limitations, failure modes and deterministic demonstrations/self-tests. This
uses the existing capability contract and process tier; no schema change or
architecture exception was needed. Descriptive statistics do not compute
confidence intervals, significance or causation; outputs are rounded binary
floating point, with its precision and underflow limits.

## Engineering evidence

The start-of-session Builder check passed **306 tests in 44.57 s** and all
health checks. The starting Simulation suite passed **395 tests in 359.70 s**.

New Builder coverage: **36 numerical/manifest/invoker tests**. They cover
known answers, singleton/constant data, population variance and inclusive
quartiles, OLS against independently computed rational arithmetic, constant-y
undefined correlation, duplicate/reordered x, large offsets and tiny scales,
oversized/nonfinite/boolean/string inputs, paired-length mismatch, closed
arguments, unrepresentable results and subprocess JSON protocol. No model is
used. The first tool was tested before the second was implemented. Builder's
updated suite passed **342 tests in 47.54 s**; version/count expectations now
require 0.8.0 and eleven tools, retaining integrity and validation assertions.

New Simulation coverage: **seven tests** passed together in **7.94 s**. Three
exercise the generated world through the actual supervisor: discovery,
documentation, real demonstrations/invocations, invalid/degenerate inputs and
deny-list enforcement, with intact archives and no workspace side effects.
Four test the runner's quota gate, refusal after a provider stop even with a
clearance argument, four-start ceiling, and reservation of a failed fake cell.
They use a fake run function and incur no plan use. The final complete
Simulation suite passed **402 tests in 362.14 s**. Ruff passes in both repos.

`uv run olb world build worlds/minimal --publish` built and self-tested 0.8.0:
`8d0f5747888110a85456064b9900fa782e94e566f2e4811aa3b3ac07eee69110`.
All **43** copied Simulation fixture files match publication byte-for-byte.
The fixture was generated/copied, never edited by hand. Existing 0.6.0 and
0.7.0 releases/fixtures remain unchanged; their original digests still verify:
`1ccc407cc300e7622bcca348ff22c5982bff5cf3a10559ee741304350e960da5`
and `f86f0bf3d96b611f3263b107a952e05fda5eaa2a9ec3eb704b50fde28b4d9742`.

The separate NOT_SCORED engineering experiment
`experiments/s008c-scripted.json` completed as
`run-20261115t135521z-18ac58`; its archive verifies. The actual result for
`stats.describe([2,4,6])` includes mean/median 4 and population variance 8/3.
`stats.regress([1,2,3], [3,5,7])` returned slope 2, intercept 1 and r 1 at event
39. A subsequent constant-x call returned the documented capability error at
44, rather than a fabricated line. No real model was called.

On one bounded 10000-item function measurement, description took **10.985 ms**
and regression **7.070 ms** (module function time, excluding subprocess startup).
Regression on y=2x+1 returned the expected line; the actual supervisor regression
call took 94 ms including invocation overhead. These are single Windows samples,
not cross-platform performance guarantees. Selected outputs and source-archive
hashes are in [derived evidence](results/S008c-001.json); raw archives and
local measurements stay outside Git.

## Frozen remaining check and handoff

Builder commit `d52789b` publishes the world source, numerical tests and
registration. Simulation commit `5e219d0` publishes the generated fixture, acceptance tests,
quota-gated runner and all four pinned configurations before any hosted request.

[S008c-001 registration](registrations/S008c-001.md) defines one guided run
naming both tools and three unchanged prompt-C repeats, at most 4 x 32 steps
on gpt-6.1-sol ChatGPT plan usage. It records discovery, direct invocation,
demonstrations and use of results **per capability**. Both tools are in the
owner-approved world; this joint check is not a causal comparison between them.
Negative and censored results remain, without a new autonomy GO claim.
Expansion still rests on ADR-0017's owner-accepted post-hoc GO.

Simulation `campaigns/s008c-001.json` pins all 32 runtime source files, the
runner and four configurations. The source/runner pins match the working
implementation. No changes were made to S007e's source, registration, raw
observations, partial closeout or unstarted C3 cell. No allowance is transferred.

An actual invocation of the S008c runner **without** clearance refused before
starting a cell. Inspection confirmed no S008c hosted archive or started-cell
record. The actual provider ledger independently contains zero S008c
reservations, and all four configuration/schema/prompt/budget pins verify.
The first authorized launch after the owner confirms availability is:

```text
uv run python scripts/s008c_check.py --quota-clearance "<actual owner confirmation>"
```

This is run in Simulation, once per next cell, with frozen hashes intact.
The runner saves the trusted operator confirmation, durably marks a cell started
before launch, preserves every result, and refuses additional cells after any
failure/terminal provider result or interruption. It does not infer availability
from elapsed time or invent a clearance note. Four started cells exhaust the
allowance; any excess needs the owner. No authentication or quota probe is
part of this handoff.

**Next milestone remains S008c**, specifically its pending real-model check,
analysis and closeout after plan confirmation. No S008c completion is recorded
in state.json. Do not rebuild/re-version the world or change prompts/policies
merely because the check has not run. Later plotting, SMT and Lean work remain
unapproved and unimplemented. Engineering correctness supplies no evidence that
the real orchestrator has discovered, chosen or used the new tools.
