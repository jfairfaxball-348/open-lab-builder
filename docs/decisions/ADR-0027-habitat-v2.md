# ADR-0027: Habitat v2, creative freedom before further experiments

Status: Accepted for planning by owner instruction, 2026-11-16.
Extends ADR-0022; supersedes its automatic return to S012 after assembly and
the active S010c fallback. Historical records and launch permissions are unchanged.

## Decision

Build a rich computational universe in three delivery phases:
[Habitat v2](../habitat/HABITAT_V2.md). The inhabitant discovers opportunities,
chooses projects and can revisit its creations. The coupled field remains an
optional phenomenon; it does not organise development.

S012-002 is a positive engineering and behavioural observation: sustained
tool-using activity under an assigned purpose. Its 151 successful tool calls,
35 memory writes and saved skill warrant richer opportunities. They establish
neither independent goal formation nor consciousness nor cognitive continuity.
Both S012 reports, registrations, validation snapshots and archives are retained.

All Lunar runs, survival studies, endurance studies, comparisons, repeated
behavioural benchmarks and exploratory hosted inference are suspended. No full
inhabitant simulation, including a scripted end-to-end run, is part of this
development programme. Use unit/integration, sandbox and offline functional
checks with deterministic fixtures and fake model services. Component tests may
exercise supervisor service handlers without launching an inhabitant loop.
After specifically approved provisioning, bounded local model component checks
are engineering verification, not experiments or a new approval programme.
This planning session authorises no inference. A future real Lunar experiment
requires a separate explicit owner decision after useful Habitat v2 delivery.

Retain the current ChatGPT-plan connection, gpt-5.6-luna/low configuration and
limits as a future option. Add no hosted text-generation service. All media AI
generation and understanding must be local, with no hosted fallback, external
media endpoint or use of hosted generation credits. This includes inspecting
images, audio and video: media bytes stay out of the hosted orchestrator request.
Return local descriptions, measurements and artifact references instead.

Reuse S007e's broker, reservations and finite lease for optional local delegation.
Extend it to an owner-allowlisted, digest-pinned models.list/models.ask interface
in container worlds. Local models receive bounded input and return untrusted
data, with no tools, host authority, recursive delegation or independent loop.
Model choice belongs to the inhabitant within the configured allowlist; neither
ordering nor discovery text should prescribe a model or oblige consultation.

Builder owns contracts/releases, Simulation owns execution and recorder, Window
only reads archives. Arbitrary code stays in rootless network-free containers.
Fixed local model workers run behind the supervisor, with validated byte inputs,
bounded outputs and resource admission. Never hand containers model endpoints,
GPU devices, credentials, recorder paths or privileged service sockets.

The implementation must bind the approved workshop image and later library/model
assets to immutable identities; old worlds retain their old image behaviour.
Shared contract changes follow CONTRACTS.md, including schema versions, examples
and tests. This decision changes no schema, runtime, world release or model file.

## Consequences

Scientific packages, offline references and procedural media deliver wide freedom
first. Local image generation and understanding follow promptly through the same
bounded service route; audio and audiovisual completion follow. Large generative
video models are excluded from the useful-state promise on the audited 4 GB GPU.
Required downloads/system installations need specific owner approval; no weights,
software or datasets are acquired in this session. No hardware purchase assumed.
