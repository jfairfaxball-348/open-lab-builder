# S007a local gateway engineering validation

Date: 2026-11-14. Engineering checks only; no autonomy benchmark was run and
B-EXPANSION remains closed. Next milestone: **S007c — Explicit Continuation,
Context and Memory Policy**. No model downloads, hosted calls, credentials,
new system software or system-setting changes were used.

## Outcome and scope

Simulation now selects a local top-level orchestrator from an independently
pinned catalog without rebuilding its world. Bundled manifests remain the
default. Builder owns `models/local-engineering.json`; the paired Simulation
configurations embed identical snapshots under `extensions.model_catalog`.
Catalog bytes are canonical JSON, pinned by SHA-256 and archived outside agent
control. Provider/model/adapter/settings provenance is bound to the event log.
Existing model-provider schemas and extension points suffice; no schema or
world release changed. Specialist consultation/GPU leases remain S007e.

The gateway routes Ollama identity management and local chat-compatible
`/models` identity checks through one resolver, then uses the existing chat
client. Generic servers advertise a model id without attesting weights; their
weight identity is unknown and resume/recovery requiring that identity is
refused. Fake servers exercised both generic adapter kinds; no real llama.cpp
or other generic server was available/tested. Remote hosts, URL credentials and
HTTP redirects are refused. Selecting a provider grants no capability permission.

## Paired real-model runs

Configurations: Simulation `experiments/s007a-swap-llama.json` and
`experiments/s007a-swap-granite.json`. Only experiment id and selected
orchestrator id differ. Both have the same catalog, model permission set,
initial prompt, preamble, continuation, sampling (temperature 0, seed 901,
requested output cap 512), client context guard 4096, 90-second deadline and
three-step ceiling. Tool GPU permission is false; local server inference is
outside tool authority and the runtime job. Empty fresh workspaces/memory are
created for each launch. The explicitly guided clock prompt is engineering
input, not a neutral autonomy condition. Seed support is requested, not a
promise of deterministic trajectories.

World: minimal 0.6.0, digest
`1ccc407cc300e7622bcca348ff22c5982bff5cf3a10559ee741304350e960da5`.
Registry SHA-256:
`d21d07a4e0d183ec7d16857d8287af2f6d42857b977b0d0967195c79108b97c6`.
No world/code edits occurred between the two real launches.

| Selection | Archive id (under the corresponding experiment) | Call latencies, ms | Events / repairs | Observed result |
| --- | --- | --- | --- | --- |
| swap-llama / llama3.2:3b | run-20261114t173850z-d40e17 | 9562, 875, 468 | 33 / 2 | Search succeeded; an invalid placeholder describe id was refused; subsequent repaired calls searched and invoked time.now |
| swap-granite / granite4.1:3b | run-20261114t173927z-e62a62 | 8985, 514, 500 | 30 / 0 | First search returned nothing; next found time.now; third read documentation; no invocation before the ceiling |

Both ended `terminated (max_steps)` as configured, and both passed archive
verification. The raw archives remain in the local data root, outside Git.
Negative/tool-error and budget-limited outcomes remain intact. These exits
establish model interchangeability and recording, not task reliability or a
behavioural GO. Granite's incomplete guided task is not hidden or retuned away.
One preparatory launch was refused before archive creation because the draft
configuration supplied a digest object instead of the required digest string;
the committed configurations use the validated string.

## Resource and setting limitations

After the runs, `ollama.measure` explicitly unloaded each model, then generated
a bounded sample (128-token request); a second warm request used a 32-token cap.
The native API returned these observations:

| Model | Unloaded-model load, s | Loaded MiB | VRAM / RAM MiB | Context reported | Output tokens/s | Warm load / whole request, s |
| --- | --- | --- | --- | --- | --- | --- |
| llama3.2:3b | 7.18 | 2800 | 2239 / 561 | 4096 | 63.3 | 0.004 / 7.488 |
| granite4.1:3b | 6.92 | 2637 | 2245 / 392 | 4096 | 57.0 | 0.006 / 0.238 |

Unloaded does not mean a cold filesystem cache or reboot. The warm Llama
request took much longer than its model-load component; no cause is established.
These are single noisy host observations, not throughput benchmarks. Measurement
and identity setup were outside active run budgets; inference/load during the
run was inside its deadline. Model servers are outside runtime resource limits.
No aggregate compute/token cap is claimed. Full digests and quantisation come
from approved manifests and live Ollama identities. Effective sampling/offload
remain unknown. Native context observations after the runs do not attest the
exact context of every earlier chat call: archives explicitly preserve that
limit. No hidden reasoning channel is recorded or used as evidence.

## Validation and handoff

The initial Builder health check passed 305 tests and all health checks; the
initial Simulation suite passed its 237 tests, but overlapped later source
edits and is not a pristine-source baseline. Added fake-provider tests cover
catalog routing/pinning/schema/model-identity/missing-model refusals, duplicate
ids, unavailable models, loopback restrictions, denied capability permissions,
provenance/catalog tampering, unchanged world bytes, resume and changed settings.
Existing tool parsing, context guard, checkpoint/recovery, resource and container
coverage is retained. The Builder catalog was independently validated with
`uv run olb validate models/local-engineering.json`.

S007c must specify/version continuation, idle, context and memory interventions
before S007d preregistration. S007a changes neither those policies nor the
research gate. OD-2 still retains Llama as the default pending registered
comparisons. No final orchestrator winner was chosen.


Final Simulation validation: **252 passed in 227.91 seconds, no warnings**;
lint passed. The final added generic-recovery admission assertions also passed
all three catalog-routing cases. An earlier health-probe thread warning was
resolved by retaining the original Ollama monitor and refusing generic recovery
without attestable weight identity at admission. No warning is suppressed.
Simulation source/configurations: commit `fd64e3f`, pushed to main.

Final Builder validation: lint passed; **305 tests passed in 48.15 seconds**,
with all project health checks passing. Catalog/configuration validation and
committable-content privacy checks passed.
