# ADR-0019: Offline study manifests and portable evidence exports

Status: Accepted (S010a, 2026-11-15). Refines ADR-0008's file interface without
changing the runtime, world, model route or Window boundary. Written before code.

## Decision

Add two versioned research contracts under schemas/v1: study-manifest and
evidence-export, initially 1.0.0. They are separate from the seven runtime
contracts and are not bundled into world releases. Existing worlds stay byte
identical. Builder owns schemas/examples/specification. Simulation reads the
operator-supplied schema directory and bundles the required research/config
schemas in an export; it neither imports Builder code nor embeds a schema in src.
The Window gains no code or write authority in this part.

A study manifest enumerates every planned cell, its role, condition, replicate,
seed-label interpretation, exact configuration pin and declared outcome. It
states question/contrasts, constant fields, limitations, analysis policy and
prospective/historical/engineering registration status. A prospective label is
an operator claim requiring external chronology evidence, never proved merely
by exporting old records. Attachments are byte-pinned registration/analysis/
annotation documents; their interpretation is not automated in S010a.

The offline Simulation exporter has no launch/provider/probe path. It copies
stopped archives into runs/<experiment>/<run>, retains all cells including ones
without archives, and writes a deterministic file index and provenance inventory.
It refuses active writer markers, unsealed/damaged/changing archives, links,
unsafe paths, duplicate cell/archive identities, changed input pins and existing
destinations. It checks before/after source hashes and verifies the copied
archives before publication. Configuration mismatch or nonempty/unknown initial
state is a visible inventory finding, not silently promoted to scientific validity.

Private operational state (.writer files, .supervisor.json and retained writer
owner markers) and runtime stderr diagnostics are not portable observations.
They remain untouched at source and are explicitly listed with hashes/sizes as
omitted. Other archive records, bundled contracts, exact model inputs, provider
ledger, all retained checkpoint/artifact revisions and segment observations are
preserved. The export is evidence, not a resumable run or a public-data release.

Exports contain inputs, schemas and copied records, so verification requires
only the exported directory. File hashes, schema validation and the existing
archive verifier establish internal integrity. An optional externally retained
SHA-256 of export.json anchors it; unpinned self-consistency is not authenticity.
No signature, preregistration proof, behavioural rating or autonomy GO is implied.
Only a new destination is written. Failed staging directories are retained for
inspection; source inputs/archives are never locked for writing or modified.

## Consequences and deferred work

S010a supplies transport/inventory integrity and protocol templates. Generalised
analysis/annotation validation is S010b; read-only Window comparison is S010c.
No new experimental execution or hosted spend is authorized. The new export/CLI
source changes the checkout's aggregate source hash; historical frozen manifests
are not updated to hide this. Their launch source checks must continue refusing
a changed checkout. Tests of a historical runner's budget gates use an explicit
frozen-source test double and separately test source-mismatch refusal.

Alternatives rejected: copying selected successful runs without a study manifest
(loses denominators); rewriting observations into a summary (loses provenance);
Window-side export (adds writes); embedding schemas in Simulation (duplicates
authority); modifying the agent loop (unnecessary experimental intervention).
