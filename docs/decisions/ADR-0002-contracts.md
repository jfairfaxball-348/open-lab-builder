# ADR-0002: JSON Schema contracts as the only cross-repository interface

Status: Accepted (S001)

## Context

Three repositories must stay independent yet agree exactly on the shape of
worlds, capabilities, experiments and observation records. Run archives must
remain readable long after the code that wrote them has changed.

## Decision

- Contracts are JSON Schema draft 2020-12 files under `schemas/v<major>/` in
  the Builder repository. Documents are plain JSON (JSON Lines for event logs).
- Every document names its contract and version (`schema`, `schema_version`).
- Semantic versioning with the compatibility rules in
  [CONTRACTS.md](../architecture/CONTRACTS.md): additive changes are minor,
  breaking changes create a new major directory, old majors are kept.
- **The Simulation and the Window do not import Builder code.** Each world
  release carries the schemas it was built with; each run archive carries the
  schemas needed to read it. Consumers validate with any JSON Schema library.
- Schemas are closed at the top level, with an open `extensions` object as the
  sanctioned place for experiments.
- Constraints JSON Schema cannot express (for example, a capability's
  demonstrations satisfying its own input schema) are implemented in
  `open_lab_builder.contracts` and listed in CONTRACTS.md so other consumers
  can reproduce them.

## Alternatives

- **Pydantic models exported to JSON Schema** — one language's classes become
  the source of truth and the Window would depend on a generated artefact.
- **Protocol Buffers / Avro** — strong evolution rules but binary, needing
  code generation, and poor at embedding a tool's own input schema, which the
  capability contract requires and which model tool-calling APIs express as
  JSON Schema anyway.
- **A shared Python package** imported by all three — couples the repositories
  at the code level and ties old archives to old code.
- **Open schemas (`additionalProperties: true`)** — maximally forward
  compatible, but typos pass silently. Rejected in favour of closed schemas
  plus `extensions`.

## Consequences

- Some duplication: each consumer implements its own (small) validation.
- The semantic checks must be kept documented, or consumers will diverge.
- Archives are self-describing and portable.
