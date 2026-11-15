# S010a: study protocol and portable evidence export

S010 was split before implementation into S010a (this part), S010b (general
comparative analysis) and S010c (read-only Window comparison). Only S010a is
implemented. Its purpose is to preserve complete planned-cell denominators and
record provenance; transport/inventory integrity does not establish scientific
comparability, preregistration chronology, motivation or a new autonomy GO.

## Built

ADR-0019 was written before code. Builder defines study-manifest and
evidence-export 1.0.0, validated examples and a usable unstarted engineering
study/configuration template. The study protocol specifies registration claims,
roles, contrasts, constant fields, seed limits, pinning, outcomes and a separate
analysis-plan template. These two research interfaces do not enter world bundles.

Simulation adds `ols evidence export` and `ols evidence verify`. They copy stopped
verified archives, pinned inputs and operator-selected schemas, then create a
deterministic file/hash inventory with source facts and explicit findings. Every
planned cell survives even without an archive. Requested constants are checked
within roles; unknown settings/digests remain unknown. Original archives are
never rewritten. Named operational/debug omissions retain original hashes/sizes.
New output only; detected source changes refuse publication and retain staging.

The Window has no changes. Runtime behaviour, policies, historical campaign
manifests/configurations and existing worlds are unchanged. The new offline
source files necessarily change the current checkout's aggregate source hash;
historical launch scripts still refuse a different checkout. Historical budget
unit tests now model the frozen source pin explicitly and separately verify that
source mismatches refuse launch. No historical source pin was rewritten.

## Existing-data acceptance

A retrospective engineering inventory, not a new preregistration, enumerated all
eight planned S007e-001/S008c-001 cells. Configurations were copied verbatim from
their committed originals and pinned canonically. Raw bundles and local diagnostic
scripts remain ignored; the following manifest pin is retained separately here.

| Cohort | Planned | Archives | Preserved outcome |
| --- | ---: | ---: | --- |
| S007e-001 | 4 | 3 | Guided/C1 reached max_steps; C2 failed after provider quota censoring; C3 not_started |
| S008c-001 | 4 | 4 | All four reached max_steps |
| Total | 8 | 7 | No replacement, exclusion or denominator reduction |

Final `export.json` SHA-256:
`24022908a57bc6dfe9b39cf8f598740c3ac83786efb492003993ab59b34a3d98`.
The final exporter source hash matches its recorded pin. There are 252 copied
files and 14 named operational/debug omissions. Every archive verifies, agrees
with its declared configuration and records an empty initial workspace. All
seven hosted weight digests remain null. S007e C2 retains provider terminal code
`response_failed:subscription_sharing_usage_limit_exceeded`.

Three requested configuration constants (provider ID, model ID, runtime policy)
are equal across the eight declared cells. Worlds, guided prompts, capability
content, opaque effective settings and correlated repeats prevent interpreting
these constants as a matched causal contrast. Zero inventory findings means only
that the selected mechanical checks found no config/initial-state discrepancies.
The provider failure remains present independently of that count.

Two separate final exports produced the same manifest digest. A copied, relocated
bundle verified with the external pin; the portable synthetic test additionally
renamed the original root and inputs before verification. Hash snapshots before
and after the historical exports match every selected source archive byte.
The CLI also exported the usable one-cell unstarted template (zero archives).
No Ollama call, provider probe, model execution, installation or settings change
was made. Added ChatGPT plan usage: zero requests; remaining plan quota unknown.

## Validation and limits

Final checks: Builder Ruff/health passed with **355 tests** (50.75 s); Simulation
Ruff passed with **423 tests** (405.58 s). Simulation delivery: `95b168d`;
Builder delivery is the S010a closing commit in git log. The detailed command
record is [S010a validation](../roadmap/validation/S010a.json).

Synthetic tests cover positive artifact production, idle behaviour, failed model
and provider outcomes, unstarted/launch-failed cells, unknown/nonempty initial
state, role-separated constants, deterministic repeat, portable verification,
no-network operation, unchanged source bytes, and tamper/damage/active/change/
link/collision refusal. Test-only alternate initial-state archives were rebuilt
with valid canonical LF event chains; an initial Windows CRLF fixture error was
fixed rather than bypassing archive validation.

Builder's scratch minimal 0.8.0 build and all capability self-tests pass; its
content digest remains
`8d0f5747888110a85456064b9900fa782e94e566f2e4811aa3b3ac07eee69110`.
The first manual verify named the build parent and correctly failed for a missing
manifest; verification of the printed release directory then passed. An import
ordering lint failure was corrected; final results are recorded in S010a.json.

Exports are local copies, not anonymised public releases or resumable runs.
Internal hashes do not prove authenticity; an external pin detects replacement
relative to that pin, not chronology. Stable stopped-source pre/post checks are
not an atomic snapshot against arbitrary privileged races. Unsealed crash residue
is refused, and failed staging is retained. Annotation semantics, effective-setting
comparisons, seven-gate analysis and evidence-linked ratings remain S010b.

Exact next milestone: **S010b — Evidence-Linked Comparative Analysis**, using
existing evidence only unless the owner separately authorises new runs. After
that, S010c adds the Window comparison flow; parent S010 remains incomplete.
