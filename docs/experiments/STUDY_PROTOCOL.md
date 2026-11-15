# Study protocol and portable evidence (S010a)

A study is an operator-authored inventory, not permission to run experiments.
The two S010a research contracts are `study-manifest` and `evidence-export` 1.0.0.
They are separate from the seven runtime contracts and are not bundled into
world releases. Minimal 0.8.0 and all historical registrations remain unchanged.
See ADR-0019. S010b now implements [source-bound descriptive analysis](STUDY_ANALYSIS.md)
with two additional research contracts; Window comparison remains S010c.

## Declare the study

Use `examples/v1/study-manifest/engineering-template.json` as a working,
unstarted example. Its adjacent configuration is pinned and requires no archive.
The evidence-export example illustrates schema syntax only, not a verified bundle.

State one question, changed fields, requested constant fields as JSON pointers,
seed interpretation, analysis policy and limitations. A requested constant is
checked across declared configurations separately within each role; equal input
JSON does not establish equal effective compute, sampling or independence.
Missing fields remain `missing`. Record known backend limitations explicitly.

List every scheduled cell with a unique cell ID, condition, replicate label,
seed label (or null), and role: pilot, evaluation, capability_check or engineering.
Never silently replace a failed cell or pool pilots into evaluation. Configuration
pins are SHA-256 of UTF-8 JSON with sorted keys, separators `(',', ':')` and
`ensure_ascii=False`. Attachment pins hash raw bytes. Paths are portable relative
paths within the study directory; links, traversal, Windows reserved names and
case collisions are refused. Attachments may carry registrations, analysis plans
or annotations; their semantics are not validated by export. S010b validates separate source-bound
annotation inputs against the pinned export.

Registration kinds are prospective, historical and engineering. Prospective
requires an operator-supplied full commit ID. Neither that field nor a digest
proves chronology, approval or preregistration. Freeze prompts, continuation,
context, repair policies, comparison rules and stop rules before scored runs,
and retain independent evidence of the freeze. Historical inventories must say
that they are retrospective. No old negative result becomes a GO through export.

Declare recorded, not_started, launch_failed or interrupted outcomes with a
plain explanation. Recorded requires an archive; not_started and launch_failed
require null. Interrupted can refer to a sealed stopped archive, but unsealed
crash residue cannot be exported as a verified archive. It remains a declared
cell without a reference until ordinary archive recovery seals it. Export never
recovers, resumes, repairs or launches an experiment.

## Export and verify

From Simulation, with operator-selected schema and data directories:

```text
uv run ols evidence export STUDY --schemas SCHEMAS --data-root DATA --out NEWDIR
uv run ols evidence verify NEWDIR --sha256 MANIFEST_SHA256
```

`SCHEMAS/v1` contains common, experiment-config, study-manifest and
evidence-export schemas. Simulation reads these as data and imports no Builder
code. An export contains `inputs/`, `contracts/v1/`, `runs/` and `export.json`.
It copies source bytes, configurations and attachments without rewriting them.
Each exported file has a digest and byte count. Record facts include final state,
stop reason, configuration agreement, world/policy/event pins, recorded model
identity/settings, initial-state evidence and provider terminal codes. Unknown
weight identity, effective settings and initial state remain unknown. A mismatched
configuration or nonempty/unknown initial state is an explicit inventory finding,
not silently corrected and not an automatic scientific verdict.

Only stopped, internally verified archives without writer markers are accepted.
Sources and inputs are hashed before and after copying; detected changes refuse
publication. Output must be new, outside study inputs; inside DATA it must be
under `exports/`. Links, nonregular files, damaged archives, extra/tampered export
files and collisions are refused. Failed staging directories remain for diagnosis.
No source writer locks are acquired and no source files are changed. This is a
stable-source check for cooperative stopped archives, not an atomic filesystem
snapshot or a defence against a malicious privileged concurrent writer.

The bundle omits only named operational/debug records: root `.writer.guard`,
`.writer.lock`, `.supervisor.json`, `runtime.stderr.log`, and segment writer JSON
and stderr logs. Omitted names, sizes and original hashes remain in the manifest;
their unavailable contents cannot be revalidated from the bundle. Science records,
artifacts, checkpoints, request snapshots and provider mirrors are retained.
These may contain private material: export is a local data copy, not automatic
anonymisation or permission to publish.

Verification needs only the bundle and installed Simulation verifier. Preserve
`export.json`'s SHA-256 separately to detect coordinated manifest replacement.
Without an external pin, verification proves internal consistency only. Even a
pinned bundle does not prove authenticity, consent, independent samples, causal
comparability or agent motivation. Identical inputs and exporter yield identical
manifest bytes; no host path or timestamp is inserted into the manifest.

## Analysis-plan template

Before scoring, write the question, unit of analysis, all conditions/replicates,
inclusion/exclusion rules, pilot separation, stop/censoring rules and treatment
of missing data. Describe whether seeds are effective or labels, and justify
independence. List intended comparisons and confounds: model identity/settings,
world, policy, context, repair, initial state, budget and interventions.

Keep three separate fields for each proposed assessment: observed behaviour
(with event-log digest, sequence IDs and artifact hashes), exact attributed agent
claims, and investigator interpretation with alternatives and uncertainty. Count
all scheduled cells, including idle, failed, interrupted and unstarted cells.
Tool counts and text volume do not establish autonomy; there is no composite
score in S010a. S010b implements annotation citation validation, descriptive comparisons and
seven explicit research-gate checks/requirements; semantic interpretation remains
a human assessment. Read-only presentation remains S010c.
