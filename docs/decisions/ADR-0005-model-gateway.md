# ADR-0005: Provider-neutral model gateway, Ollama first, sequential loading

Status: Accepted (S001). Minimal form in S003b, full form in S007.

## Context

The development machine has Ollama installed and running with **no models
pulled**, `llama-cpp-python` in the base interpreter, a 4 GB NVIDIA GPU and
16 GB of system RAM. No PyTorch. Experiments must record exactly which model
ran, and must not be coupled to one server.

## Decision

- All model use goes through a **model gateway** inside the Simulation. The
  runtime and capabilities name gateway model ids (for example
  `orchestrator-small`), never provider-specific names.
- The gateway's internal request/response shape is **OpenAI chat completions**
  with tool calling. Ollama, llama.cpp's server and LM Studio expose this
  directly; other providers get an adapter.
- **Ollama is the first provider**: it is already installed, manages model
  files, and can unload models on request. Its native API is used only for
  management (list, load, unload, digests).
- Models are described by model-provider manifests with footprints. The
  gateway holds **one GPU-resident model at a time** by default: before
  loading a specialist it unloads the current model, and reloads the
  orchestrator afterwards. Loads and unloads are recorded as events.
- External (network) providers are representable (`locality: external`) but
  disabled unless an experiment explicitly grants network access.
- Non-chat models (speech, image generation) are reached through capabilities
  whose implementation asks the gateway for a GPU lease, so scheduling stays in
  one place.

## Alternatives

- **Call Ollama directly from the runtime.** Fastest to build; couples every
  experiment record and capability to one server's naming and API.
- **llama.cpp server only.** Fewer moving parts and finer control, but manual
  model file management and one process per model.
- **LiteLLM as the gateway.** Broad provider coverage, but a large dependency
  whose focus is hosted APIs; it has no notion of local memory scheduling,
  which is this machine's central constraint.
- **Keep several models loaded.** Not possible in 4 GB of VRAM.

## Consequences

- Swapping models costs seconds to tens of seconds per switch. Capabilities
  that need a specialist model are expensive; their manifests say so
  (`resources.exclusive_gpu`) so the agent can learn the cost.
- The orchestrator's context is re-evaluated after a reload unless the server
  caches it; S007 must measure this.
- Orchestrator quality is bounded by what fits in 4 GB. This is the largest
  known risk to the research value of experiments and is tracked as an open
  decision.
