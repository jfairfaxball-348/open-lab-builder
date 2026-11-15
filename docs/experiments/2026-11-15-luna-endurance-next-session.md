# S011p — Luna 5.6 qualification and first one-hour run (next session)

Status: **planned, not executed**. Owner direction: 2026-11-15. The next coding/experiment session should attempt this milestone, not S010c. This is a roadmap change only: no provider models have been queried, no experiment configuration frozen, no model requests sent and no ChatGPT plan allowance used by this edit.

## Scientific question

Can the lower-cost `gpt-5.6-luna` orchestrator, using the existing Open Laboratory discovery interfaces, initiate meaningful self-selected work and preserve an auditable record during a supervised one-hour opportunity without human task-by-task prompts? Independently, what allowance and scheduling constraints does this model encounter on the owner's Sign in with ChatGPT route?

Do not infer consciousness, continuous purpose or equivalent intelligence from uptime, call count, tokens, tool use or a model's narrative. Luna's published standard API prices are **not** a conversion factor for ChatGPT Plus plan percentages.

## Order of work in the next session

1. Read Builder and Simulation `AGENTS.md`, current git status/history, S011p/S011a, ADR-0016/0017, runtime policies and earlier hosted result/defect reports. Verify existing tests first. Preserve all completed S010a/b evidence and leave S010c parked, not complete.
2. **Zero-request eligibility check:** in Simulation run `uv run ols provider models openai-chatgpt` and confirm the authenticated account lists the *exact* `gpt-5.6-luna` provider ref. Inspect actual reported context/model metadata, the current plan usage page and broker profile. This command queries model metadata but is not a model inference. If Luna is absent, stop; do not silently substitute GPT-6 Luna, Sol, an API key, credits, another provider or another subscription route.
3. Define and test a Luna model-catalog entry/configuration consistent with the real model-list metadata and pinned adapter, without copying Sol's claimed model identity or inventing an effective context/weight digest. Document all unsupported sampling/reasoning settings and freeze what is actually sent. The existing preview may not honour requested temperature/output cap/seed; expose unknowns rather than assuming them.
4. **First live Luna check — NOT_SCORED:** an explicitly bounded tool-use round trip on the existing minimal world, requiring `capability.search`/`describe`, one genuine `math.evaluate` invocation (`6*7` -> `42`), result-informed response, and a verified archive. Add a separate short workspace/memory check if needed for the one-hour experiment; cap total live attempts (including retries). Do not report a demo as a direct invocation. Fake-server/CLI tests precede any live request.
5. **Prepare one-hour experiment** only after the live check passes: choose and version the world (prefer 0.8.0 if using regression), one unguided prompt (C is the initial candidate), permissions, context guard, explicit memory, continuation/quiet policy, model identity, single-run limits, interruption treatment, observer metrics and a deterministic maximum model-request rate. A pacing limiter is an infrastructure intervention: implement/test/record it if missing, never pretend the existing runtime already enforces it. Distinguish active waiting from actual model activity. Use a fresh empty workspace.
6. Pre-register this one-hour run **before** the first scored request. Keep any smoke/pilot separate. Require a finite owner-approved broker request ceiling and permission to consume plan usage, with ChatGPT Settings -> Usage checked by the owner immediately before launch; per-app/5-hour/weekly availability is not remotely predictable. Do not alter the app percentage, buy credits, use fallback billing, relax safety limits or bypass provider stops.
7. Launch **one** supervised run with a nominal 3,600-second active duration and independently recorded model-call pacing. Preserve goal declarations as agent claims, tool discovery/use, files, memory writes and later retrieval, result-informed revisions, repetition, idle/stopping, system-continuation messages and all provider/OS events. No human coaching while it runs. At the end, verify the archive, request ledger, frozen configuration and artifact hashes, and report observed active duration versus model-active time.
8. If the model stops voluntarily, enters quiet idle, hits local budget, reaches a five-hour/weekly/app quota, loses provider access or cannot maintain continuity, **retain the real outcome** as idle, capped, censored or interrupted as appropriate. No automatic continuation after a usage refusal, no silent retry, replacement, model swap or claim that a censored run completed one hour. Don't invoke unsupported hosted resume; a fresh attempt would be a new registered run.
9. Publish a concise engineering/behaviour report with exact run IDs, timings, calls, source event references, token observations, artifacts, negative findings, effective model/version, request-ledger reconciliation and the next safe step. Do not promote Luna to the Sol-specific owner-accepted post-hoc GO without its own evidence. Run all affected test suites and update roadmap/state truthfully.

## Finite-budget and scheduling gate

- The historical hosted benchmark sent hundreds of requests in less than an hour. Faster inference can **increase** calls per hour. Provider pricing, reported tokens and subscription-plan consumption are different measures. Measure them, do not infer one from another.
- Propose a conservative model-call cadence and a hard local maximum number of HTTP attempts, counting retries and ambiguous attempts. If the runtime lacks an enforceable clock-based cadence, add it with fake-clock/fake-provider tests before launch, or do not claim a paced one-hour test.
- Determine whether the current `quiet-until-deadline-v1` treatment answers this session's question; it has no automatic wake. If selected, explicitly register that stopping work may produce a long but legitimate idle observation. If `legacy-immediate-v1` is selected instead, label the repeated environment continuations as interventions; do not equate prompted continuation with spontaneous work.
- No unsupported reasoning-effort control may be silently assumed. Try a separately bounded diagnostic if justified; record the actual route's acceptance/rejection, and freeze exactly one setting for the scored run.
- Before 12/72-hour work, design a separately tested provider-identity/interrupt solution. Hosted resume is currently **refused** because a cryptographically pinned provider model is unavailable. Do not weaken this rule merely to keep a clock running.

## Milestone exit

Completed only when Luna is confirmed accessible, the real bounded check and its archive are verified, the one-hour run is executed or its failure/censoring accurately documented, all local limits/interventions are tested and recorded, and a report distinguishes reliability from autonomous behaviour. An unavailable model, failed smoke, blocked allowance or aborted run is an honest partial result; do not mark S011p complete until the stated criteria have actually been met. The next recommendation is S011a one-hour fault/recovery reliability, then S011b (12 hours) and S011c (72 hours) if their separate gates pass.

## Links

- Model reference: https://developers.openai.com/api/docs/models/gpt-5.6-luna
- Plan-usage and sessions: https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions
- Prior hosted result: [S014i-001](2026-11-15-hosted-comparison.md); accepted post-hoc decision: [ADR-0017](../decisions/ADR-0017-owner-accepted-go-and-capability-testing.md)
- Runtime: [versioned policies](../architecture/RUNTIME_POLICIES.md), [roadmap](../roadmap/ROADMAP.md)
