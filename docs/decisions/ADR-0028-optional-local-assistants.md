# ADR-0028: Optional local assistants through a frozen supervisor catalog

Status: accepted for S021a implementation, 2026-11-16. Refines ADR-0018 under
ADR-0027; its legacy single-specialist protocol remains supported unchanged.

## Decision

Add a versioned closed `extensions.specialist` variant,
`version: local-models-v1`. It selects 1–8 unique model_ids from the verified
world's bundled, digest-pinned local Ollama manifests, with all existing call,
prompt/output/time/lease bounds plus context_tokens (1024–4096), model_ram_mb,
model_vram_mb, ram_reserve_mb and vram_reserve_mb. Context must leave room for
output plus a fixed framing reserve; UTF-8 byte length provides a conservative
prompt-token admission bound. Effective context remains server-reported.

Only an existing external or scripted orchestrator is supported; its connection,
profile, reasoning effort and usage limits are untouched. Configured model ids
must also appear in permissions.models. All selected profiles share one pinned
loopback provider; no endpoint, command, filename or model download comes from a
capability argument. Models receive only the supplied text prompt, with no tools,
conversation history, recursive delegation or independent loop.

`models.list({})` returns configured profile metadata in stable id order and
the effective per-call limits. This is a frozen allowlist, not a live host model
inventory or a quality ranking. It consumes no inference reservation and loads
nothing. `models.ask({model_id,prompt})` selects only an allowlisted, permitted id.
Both travel over the existing specialist pipe. Supervisor binding to a recorded
permitted outstanding tool call, argument equality and one-time servicing remain
mandatory. Empty arguments identify the new list operation; ask schemas require
nonempty model_id/prompt. No new arbitrary RPC facility is introduced.

The manifest's gpu permission remains false: this grants a brokered service,
not a GPU device to code. Sandbox containers retain no network, GPU, credentials,
service socket or recorder path. Model selection and model permissions are
revalidated by the supervisor; tool availability imposes no obligation to use it.

Reuse the OS gpu-lease lock, finite server keep-alive and supervisor-owned call
reservations. One heavyweight model at a time; unload the owned model before
switching, then recheck identity and foreign residency. Never unload unrelated
host work. Check free host RAM/NVIDIA VRAM against declared model budgets and
reserves before load, then inspect actual server-reported allocation/context and
remaining headroom after load. Refuse unknown/insufficient measurements and
oversized allocations, without a substitute model. These are cooperative
admission checks, not hard GPU or model-server memory isolation.

Use cancellable, bounded loopback HTTP for the new variant so stopping the lease
interrupts an in-flight socket; cleanup unloads only the owned digest. A server
may still take time to cancel work: finite keep-alive remains the crash backstop.
No fallback, retry or replenished budget after a failed/uncertain request.
Count/reserve before dispatch and conserve spent calls across resume; list reads
do not count. No reasoning channel is returned or recorded. Empty replies and
unexpected tool calls are explicit failures, not fabricated successful output.

Existing observation extensions record all configured manifests/policy, selected
identity, exact text input/output, reservations, resource observations, requested
context and server-reported allocation/context, timing and cleanup. Raw model
server response objects/hidden reasoning never enter the recorder.

S021a adds ordinary capability/model manifests and this closed extension variant;
no shared schema shape changes. Builder self-tests use labelled fake results.
Verification is direct component/fake-server and bounded installed-model checks,
never a full inhabitant simulation. No downloads or hosted requests are part of
S021a. Local image work remains required S021b, not delivered by this decision.
