# Next session — S021 optional local assistants and visual creation

S020 is complete. Habitat 1.2.0 has scientific Python, four licensed offline
reference/data sources, procedural image/audio/animation/video work, FFmpeg and
safe read-only Window PCM WAV/WebM previews. Read
[S020b evidence](docs/habitat/demos/S020b.md),
[Habitat v2](docs/habitat/HABITAT_V2.md), ADR-0027 and the
[S021 scope](docs/roadmap/ROADMAP.md#s021--optional-local-assistants-and-visual-creation).

## First development task

In Simulation, inspect existing specialist.py, supervisor service IPC and the
capability permission checks. Design/implement the smallest extension from the
single pinned specialist to a frozen allowlist: models.list and models.ask with
an explicit allowed model id. Reuse reservations, deadline handling, finite
leases and recorded results; do not give Python containers an endpoint, socket,
network or GPU device. Builder owns corresponding contracts/manifests/releases.
Local assistants return bounded untrusted data, have no tools, no recursive
subtasks and no independent loop. Discovery must not prefer a model or require
consultation. Preserve the existing primary hosted model/profile/effort/limits.

Installed inventory from metadata includes Llama3.2:3b, Qwen3:4b, Qwen3.5:2b
and Granite4.1:3b; Qwen3.5 advertises vision. Reinspect current digests/capabilities
without inference first. Use deterministic fake services for engineering. If the
whole S021 slice is too large, split it in the roadmap before implementing;
retain image creation/understanding as required work, not an administrative
future programme. No model is disqualified as a bounded assistant merely by
its old autonomous-orchestrator result.

## Provisioning, local checks and limits

This handoff itself grants no downloads or inference. A future owner instruction
to execute S021 authorises its ordinary scoped development; specific new model
or system-software acquisitions still follow AGENTS.md. After approved
provisioning, bounded direct local component checks can establish availability,
actual RAM/VRAM/latency and cancellation. A mocked reply does not establish a
working generator. Do not launch an inhabitant loop to test model feasibility.

The visual path is installed Qwen vision first, with smaller SmolVLM as an
alternative; SD1.5/stable-diffusion.cpp is the planned local image-generation
candidate. Check exact release licences, artifact identities and worker isolation
before acquisition. Share a single-heavy-job resource admission policy across
local text and media; inspect actual free RAM/VRAM rather than assume fit.
Keep media bytes out of the hosted orchestrator: local descriptions/measurements
and artifact references only. No cloud media fallback or new hosted text service.

## Existing boundaries and closeout

Find sibling checkouts, read their AGENTS, inspect status/log/remote, sync/state
and baseline checks. Reuse the provisioned 1.1.0/1.2.0 images; never overwrite
an old release/image selection. Copy generated fixture bytes exactly, including
embedded line breaks. Use direct sandbox/supervisor-service/recorder components,
not full scripted supervisor demonstrations. Window remains read-only and does
not call models or Simulation. Shared schema changes require versions/examples/
changelog/tests; no imports across repositories.

Run relevant changed-source suites/lint and Builder olb check --tests. Update
roadmap/state/docs with actual evidence, then commit and push scoped work.
All Lunar/full inhabitant runs, endurance/survival studies, comparisons and
behavioural campaigns remain suspended. The next real Lunar experiment needs a
separate explicit owner decision after useful Habitat v2 completion.
