# ADR-0023: Run-local tools pin validated source in protected checkpoints

Status: Accepted (S016b). Refines ADR-0003/0015 within their existing boundaries.

## Decision

`tools.create` is a reserved runtime-managed capability, enabled only by the
experiment's `agent_created_tools` flag on a container world with subprocess
permission. It reads a bounded workspace Python entry file as data. The file
must define `run(arguments)` and return one JSON object; stdout is reserved
for JSON. The runtime never imports, compiles or executes this source.

The runtime accepts a bounded, non-referencing JSON Schema subset and at most
five input/expected-output examples. Every example executes through the
unchanged `python.run` capability inside a fresh container; schemas and exact
expected values are checked before registration. Example execution can change
the workspace even on failed registration. No automatic retries occur.

Accepted source bytes, generated manifest, digest and run provenance are held
in runtime state, outside the workspace, and included in the existing protected
checkpoint component. Search/describe/demonstrate/invoke expose this pinned
registration alongside Builder capabilities. Editing or deleting the original
workspace file does not replace the registered tool. To change a registration,
create a new id; replacement and cross-run sharing are out of scope. Resume
verifies checkpoint integrity and revalidates registration data and digest,
without rerunning side-effecting examples or trusting workspace manifests.
Only the entry file is pinned. Inputs, workspace data and imported workspace
modules remain mutable, so this is not an attestation of all transitive code or
of future behaviour. No successful validation changes execution permissions.

Agent ids must use `agent.<slug>` and cannot shadow any existing capability or
meta-tool. Permissions are fixed to `python.run`'s workspace-write, subprocess,
network-none boundary. Both the target tool and `python.run` remain subject to
allow/deny and permission checks. No network, GPU, models or package privileges
can be requested. At most sixteen registrations are permitted per run.

The Builder manifest reserves `runtime-tools/tools.create` using the existing
MCP invocation shape. Builder self-tests inject an explicitly non-registering
fake, checking the interface only; real validation is demonstrated by Simulation
container tests. No shared schema changes are needed. Tool results carry
provenance and source digest in existing observation extensions.
Generated agent manifests use the same reserved server with their own id as
the tool name. This denotes a protected source snapshot, not an invented file
entrypoint in the immutable world release.

## Alternatives and limits

Re-reading mutable source on each invocation would let an earlier successful
test label different code as validated. Treating workspace manifests as trusted
registrations would let arbitrary Python manufacture authority. Pinned snapshots
avoid both. A successful example is engineering evidence for that example,
not a proof that the code is safe, correct on all inputs, or autonomous. The
container remains the security boundary, including during validation.
