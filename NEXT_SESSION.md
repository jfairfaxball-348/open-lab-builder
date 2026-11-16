# Next session — S021b local image understanding and creation

S020a/S020b and S021a are complete. Habitat 1.3.0 offers scientific Python,
references, procedural media/FFmpeg, read-only previews and optional bounded local
text delegation. Parent S021 remains incomplete until genuine local image
creation, editing and understanding are delivered. Read [component evidence](docs/experiments/2026-11-16-local-assistant-components.md),
[ADR-0028](docs/decisions/ADR-0028-optional-local-assistants.md), Habitat v2 and S021b.

## Exact first development task

In Simulation, implement bounded artifact-input staging for a local image-
description service using installed pinned Qwen3.5:2b: validate source identity,
containment, format and pixel/byte limits, then supervisor-only dispatch with
fake outputs first. Reuse S021a recorded-call binding, reservations, single heavy
job lease and headroom checks. Sandbox Python keeps no network, GPU, model
endpoint or protected paths. Never route media bytes to hosted text.

Reinspect inventory/digests and headroom before bounded local checks. Qwen3.5's
text check does not prove vision fit/support/quality. Images need an explicit
media service, not base64 inside models.ask. Establish visual worker/decode
restrictions. For generation/editing, pin exact SD1.5 and stable-diffusion.cpp
artifacts, licences and restricted-worker design before requesting specific
acquisition approval under AGENTS.md. New downloads/system installs remain
blocked until approval; this handoff grants none. Do available engineering work
first. SmolVLM is an alternative with its own acquisition approval if needed.

## Completion and boundaries

Save a real generated PNG, edit it and describe the saved output locally, with
source hashes, persistent artifacts, provenance and actual peak RAM/VRAM/latency
after approved provisioning. Fake routing cannot establish a generator. Preserve
revision/checkpoint/lineage and safe Window observation. Never unload unrelated
models or relax admission to force a result. Required image scope needs owner
revision if no candidate fits; do not silently drop it. S022 follows only after
S021 completes; neural video remains outside the hardware promise.

Find sibling checkouts; read AGENTS/status/log/remote, sync/state and baseline
checks. Respect repository ownership. Reuse provisioned images and rebuild/copy
release bytes exactly, including upstream reference formatting. Preserve legacy
worlds/protocols and all S012 records. Model-server admission samples are neither
hard memory ceilings nor independently measured peaks.

Use direct sandbox/service/recorder tests and fakes; no full inhabitant simulation,
even scripted. No Lunar run, behavioural benchmark, comparison or endurance study.
Retain hosted Luna/low connection and limits; no hosted media or exploratory
hosted inference. The next real experiment needs a separate explicit owner
decision after useful Habitat v2 completion. Finish relevant checks and Builder
olb check --tests; update evidence/handoff, then commit/push scoped changes.
