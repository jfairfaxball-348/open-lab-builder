# S007e: Specialist consultation and capability check

Engineering is complete. The registered capability check is **closed with
partial coverage after a provider quota stop**, not a complete four-run check.
The owner was told that guided/C1 finished, C2 was censored and C3 was unstarted,
and was asked whether to close with partial coverage or leave S007e incomplete.
The reply was **“Continue”**; this closeout interprets it as permission to close
with the partial coverage explicit and S008c next. No further hosted request
was sent. The original registration and its four scheduled cells remain intact.

## Built and validated

Builder `ff13809` records the design-first [ADR-0018](../decisions/ADR-0018-supervisor-specialist-consultation.md),
the reserved supervisor service, bounded manifest/documentation/demonstration,
build-time fake-service self-test and new minimal 0.7.0 world. Simulation
`b825682` implements independent admission, durable call reservations, the local
gateway's asynchronous lease, expiry/cleanup and observation recording. Only
the approved installed llama3.2:3b is available as `specialist-text`. Hosted
orchestration retains its existing broker, conversation and policies.

The capability receives a prompt and returns text. Neither capability subprocesses
nor the model receive an endpoint, credential or archive path. Permissions,
allow/deny lists, schemas and experiment bounds apply independently in the
supervisor. The specialist has no tools; its text is observed model output, never
authority. Calls consume the configured budget, including failed/uncertain
reservations and replay. Resume reacquires residency rather than restoring a
lease claim. The supervisor remains responsive during inference.

Minimal 0.7.0 digest:
`f86f0bf3d96b611f3263b107a952e05fda5eaa2a9ec3eb704b50fde28b4d9742`.
Its 37 fixture files match the published release byte-for-byte. The unchanged
0.6.0 fixture/release both verify at
`1ccc407cc300e7622bcca348ff22c5982bff5cf3a10559ee741304350e960da5`;
their pre-existing volatile release metadata differ, while bundled content
matches. The 0.6.0 fixture was not edited. Both releases pass self-tests.
No download, installation or settings change occurred.

Validation:

- Start: `uv sync` in both repositories; Builder `uv run olb state` and
  `uv run olb check --tests`: 305 tests and health checks passed. The initial
  Simulation suite passed.
- Final implementation: Simulation `uv run pytest`: **395 passed in 357.90 s**;
  `uv run ruff check .` passed. Eleven specialist/interrupt tests also passed
  separately, including fake-server routing/reuse, timeout, server failure,
  input/output bounds, permissions, pinned identity, resident-model refusal,
  OS-lock exclusion, expiry, resume budgets/reacquisition, deadline monitoring
  during inference and intact archives. Thinking-channel fixture text is absent
  from recorded observations. Real models are never used by tests.
- Builder `uv run olb check --tests`: **306 passed in 40.55 s**, all health
  checks passed; Ruff passed. Version/count expectations now require nine tools
  and 0.7.0; validation/integrity assertions were retained. The new build-time
  service test explicitly verifies fake transport, input/output bounds and
  refusal without a transport. A pre-existing non-UTF-8 punctuation byte in
  CONTRACTS.md was repaired while updating that document.

The authorized local engineering check used a scripted orchestrator:
`experiments/s007e-local.json`, run `run-20261115t124005z-90b5c7`. The archive
verifies. The supervisor checked the pinned digest, loaded, asked and unloaded
through loopback; subsequent `/api/ps` showed zero residents. Load: **8.233 s**;
load plus answer: **9.125 s**; unload: **0.046 s**. Ollama reported 43 input and
33 output tokens. The answer identified the risk that one example is
unrepresentative. These are measured load costs, not a guaranteed cold-start
benchmark. This check made zero hosted requests.

## Frozen capability check and results

[Registration](registrations/S007e-001.md), Simulation manifest
`campaigns/s007e-001.json`, and all configurations were committed and pushed
before the first hosted request. Runtime source still matches its frozen
hashes. [Derived measurements](results/S007e-001.json) bind each event/provider
log by SHA-256 and distinguish observations from investigator assessment.
Raw archives/workspaces and the durable progress record remain under the local
data root, outside Git. No run was retried, replaced or resumed.

| Cell | Completed steps | Discovered | Direct use | Demo use | Result used | Coverage |
| --- | ---: | --- | --- | --- | --- | --- |
| Guided | 32 | Yes | 1 | 1 | Yes | Complete at step limit |
| C1 | 32 | Yes, search summary only | 0 | 0 | No | Complete at step limit |
| C2 | 13 | Not observed | 0 | 0 | Not observed | PROVIDER_CENSORED |
| C3 | — | Unknown | — | — | Unknown | NOT_RUN_PROVIDER_STOP |

Guided evidence: search result event 18 and documentation event 26 exposed
`models.ask`; demonstration reply event 43 followed actual lease/inference
observations 35-42. The model paraphrased its limitation into NOTES.md in the
successful write at events 72-73 and reported that use at 81. Direct consultation
returned the same limitation at 103; a subsequent successful overwrite at
114-115 attributed the direct consultation, with a report at 123. These later
recorded actions support the investigator's **result-used** assessment. The
demonstration is separate from direct invocation. There is no claim that the
answer improved task quality or established independent empirical evidence.

C1 received the capability summary in search result event 18, chose workspace
and arithmetic tools and produced a birthday-problem note without consulting
the specialist. C2 pursued a similar arithmetic experiment but never received
a specialist search result or used it before censoring. The provider returned
`response_failed:subscription_sharing_usage_limit_exceeded` on its 14th
attempt, after 13 completed model calls. An early live count was 12; the final
archive establishes 13. The frozen stop rule prevented C3 from launching.
Every one of the three created archives verifies, including the failed run.

Guided lease costs: load **3.094 s**, first consultation including load
**3.891 s**, reused consultation **0.905 s**, unload **0.108 s**. The 60-second
lease expired and unloaded while the hosted run continued. Load/unload overhead
was **3.202 s**; it excludes inference. No orchestrator unload/reload occurs on
this hosted route. C1/C2 incurred no specialist switch cost.

Plan accounting: **78 reserved HTTP attempts**, **77 completed model calls**
(32 + 32 + 13), **315,572 reported input tokens**, **4,397 reported output
tokens**, including **496 reported reasoning tokens**. All successful provider
outcomes reported `gpt-6.1-sol`; zero syntactic repairs and no context truncation
were observed. The quota-denied attempt returned no usage; its usage is unknown.
The plan percentage/remaining allowance is opaque to the application. No API
credits, alternate provider, extra probe or additional run was used.

## Limits and next work

The guided run establishes this integration under explicit instruction. C1 is
a completed discovery-without-use observation; C2 is censored and C3 unobserved.
**Unguided specialist consultation/result use is not established.** Coverage
is partial; do not quote this as three completed C samples or a new autonomy
GO. Expansion still relies on ADR-0017's owner-accepted post-hoc GO. The
assessor is one unmasked investigator and identical C prompts are repeated
samples, not a generalisation test.

The GPU lock excludes cooperating supervisors under one data root, not unrelated
GPU clients. Other resident Ollama models are refused without being unloaded.
Orderly segment cleanup and expiry were run; abrupt supervisor loss relies on
the server's finite keep-alive and does not guarantee immediate unload. Model
servers remain outside runtime resource limits. Native settings/offload are
not independently attested per call; local-orchestrator swapping, containers
with GPU/network and Linux execution remain unverified or unimplemented.

**Next milestone: S008c — Scientific and Proof Tools**, the owner-approved
standard-library statistics part. It is not implemented in this session. Its
hosted capability check must wait for confirmed plan availability; there is no
automatic quota probe or settings change. S007e C3 remains unexecuted and is
not silently transferred into S008c's separate allowance.
