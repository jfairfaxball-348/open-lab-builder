# ADR-0020: Source-bound offline comparative analysis

Status: Accepted (S010b, 2026-11-15). Extends ADR-0019; written before code.

Builder adds study-annotations and study-analysis research contracts, both
1.0.0. No runtime schema or world changes. Simulation reads operator-selected
schemas as data, analyzes verified S010a exports, and writes a new report
directory outside the export. It never launches, repairs or modifies a run.

Mechanical facts retain event sequence vectors and source log hashes, full
artifact revision metadata, recorded requested/effective settings and policy
identities. Counts describe recorded actions only. Planned cells without records
stay present with unknown observations. Aggregation is by role and condition;
pilots never join evaluation. Pairwise descriptive contrasts expose differing
requested fields and recorded identities/settings, missing records and unknowns.
No contrast is automatically certified causally matched or independent.

Annotations are a separate operator-authored document pinned to an export. Each
entry has a category, label, rationale and references to a cell's event-log hash,
sequence IDs and optional artifact digests. Observation descriptions, exact
agent quotes and investigator assessments are separate kinds. Exact quotes must
resolve through a JSON pointer to agent.output/agent.statement text; an assessor
cannot turn a tool result into an agent claim. All references are validated;
unsupported or malformed citations refuse analysis rather than being published.
This validates provenance, not the truth of an assessment. Missing annotations,
single unmasked reviewers, uncertainty and conflicting entries remain visible.

The analysis report carries source/export/study/annotation/analyzer/schema pins.
It includes all seven research gates, with mechanical results and explicit
human/unverified requirements; no automatic launch GO. Historical inventories
never become prospective registrations, baseline currency and isolation/reliability
approval cannot be certified from records alone. Invalid exports are refused;
valid failed/censored traces and configuration/initial-state findings remain.

Outputs are deterministic JSON plus a human-readable Markdown rendering,
bundled schemas and normalized annotation input. Verification recomputes every
report from the pinned export and annotations; no source path or timestamp is
inserted. Repeated or relocated analyses must agree. Report and export reads
are bracketed by hash snapshots for cooperative stable-source checks. Existing
output and output inside sources are refused. Failed staging is retained.

S010c consumes these file interfaces in a strictly read-only Window. This does
not revise the frozen S007d rubric, historical GO/NO_GO, or permit new spend.
