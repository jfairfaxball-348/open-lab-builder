# ADR-0021: Hosted run recovery with a provider-reported identity pin

Status: Accepted (owner direction 2026-11-15: "Design hosted recovery"). This
amends the ADR-0016 implementation note "Hosted runs refuse automatic recovery".
It is implemented in S011r.

## Context

Recovery in this project means appending a new segment to the same run from
its last complete-step checkpoint. Until now, a real model could resume only if
its weights had an attestable digest. Local Ollama models have one; hosted
models do not. Hosted runs therefore refused every resume. S011a needs three
one-hour runs, each with a registered fault that is then recovered, and the
owner chose to make that possible on the hosted Luna route rather than switch
to a local model.

No hosted provider offers a cryptographic pin. The strongest identity
available is:

- what the Laboratory itself sends: provider ref, adapter id and version,
  frozen catalog, inference settings, sampling, and the broker's limits and
  cadence;
- what the provider reports on each response: `model_version`.

Note that `model_version` is a provider claim. It is not attested.

A second constraint: hosted provider failures, including the plan usage-limit
refusal, reach the supervisor through the same "model server could not produce
a reply" path that triggers automatic recovery for local models. Recovering on
that path would amount to automatic continuation after a provider refusal, which
the owner has ruled out.

## Decision

1. **Opt in.** A hosted run may resume only if its configuration says
   `extensions.recovery.hosted_identity = "provider-model-version-v1"`. That
   field is the only new recovery field, and only hosted runs accept it. Local
   runs keep the digest rule unchanged.
2. **Frozen request identity.** A resume must reproduce exactly the frozen
   `model.json` of the prior segments: catalog, provider ref, adapter
   id/version, inference (including `reasoning_effort`), sampling, broker
   limits, minimum interval and attempts. If the owner changes the broker
   profile, the treatment has changed, so the resume is refused.
3. **Provider-reported version pin.** In an opted-in run, the first accepted
   response fixes the pin `V` = its `model_version`. On resume, `V` is read from
   the run's own provider-ledger mirror:
   - every accepted response in earlier segments must report the same `V`;
   - if no response was accepted yet, the first one after resume fixes `V`.

   Any accepted response that reports a different version (or none) is **not
   delivered to the runtime**. The broker records it as the terminal outcome
   `provider_identity_changed`, and the run stops. That stop is a provider stop,
   never a recovery trigger.
4. **What triggers automatic recovery.** For hosted runs, only an
   infrastructure failure inside the Laboratory triggers it: an unexpected
   runtime exit, within the registered `max_restarts`. Provider unavailability,
   terminal provider outcomes, budget exhaustion and identity changes never
   trigger it. Hosted runs have no Ollama health monitor.
5. **Refused resumes.** An operator or startup resume is refused if the run's
   provider ledger records any terminal outcome, budget exhaustion or identity
   change. A provider stop ends the run. Continuing would need a new registered
   run.
6. **Accounting.** The request ledger is keyed by run id, so every segment
   shares the run's ceilings. A request that was in flight at the crash and is
   then replayed from the checkpoint is counted again. The original time and
   step budgets are unchanged, as for local recovery.
7. **Records.**
   - Each resumed segment records a supervisor action at stage
     `hosted_identity_pin`, with the pinned version or `unpinned`.
   - The model identity keeps `digest: null` and states the limit "hosted model:
     provider-reported model_version pin, not cryptographically attested".
   - Reports must call this *consistent provider-reported identity*, never
     *the same weights*.

## Consequences

- S011a can register hosted runs that each include a runtime-crash fault and its
  recovery, with honest identity wording.
- If the provider silently changes the model behind an unchanged
  `model_version` string, this design cannot detect it. That limit is stated in
  every report.
- A provider-side change ends the run instead of mixing two model identities in
  one record.

## Alternatives

- **Keep refusing hosted resume and run S011a locally.** Offered to the owner
  and not chosen.
- **Pin only the configuration and ignore `model_version`.** Rejected: it would
  allow a run to switch provider snapshots mid-record without any trace.
- **Probe the provider before resuming.** Rejected: an extra model request that
  is not part of the run, it spends allowance, and it attests nothing more.
