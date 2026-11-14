# Autonomy and experimental readiness — S013 realignment

Current implementation update: S007a local routing and S007c versioned runtime
policies are complete as engineering. See [policy specification](RUNTIME_POLICIES.md)
and [validation](../experiments/2026-11-14-runtime-policies.md). S007d-001 is now
complete with NO_GO; see the [registered report](../experiments/2026-11-14-autonomy-baseline.md).
The original planning/audit body is retained; earlier pilots remain engineering evidence.


Date: 2026-11-14. Status: strategic planning, not a runtime release or experiment.
Decision: [ADR-0013](../decisions/ADR-0013-autonomy-as-an-experimental-objective.md).
Execution plan: [ROADMAP](../roadmap/ROADMAP.md). Authoritative prospective
benchmark/validity specification: [Experiments](../experiments/README.md).

## Vision and the course correction

What does an artificial agent actually do when given a computational world,
meaningful affordances and time, without further human tasks? The long-term
instrument should expose independently initiated exploration, discovery,
agent-stated objectives, tool/model use, artifacts, verification, memory-informed
adaptation and eventually sandboxed tool authorship over extended periods.
These are observable questions. Subjective consciousness is not assumed or proved.

The infrastructure is necessary and worth preserving. More working capabilities
are not sufficient evidence that an inhabitant independently chooses useful
activity. We will develop intelligence/autonomy and experimental validity beside
the world, reliability/safety and observation streams. These are four streams
within the same three repositories, not a restart or a new agent framework.

Builder continues to publish worlds/contracts. Simulation hosts the inhabitant
and its independent recorder. Window presents that record read-only; it does not
write observations, control runs or become part of the agent's environment.
No runtime, schema, fixture or test is changed in this planning session.

## Audit at the planning boundary

All checkouts were clean before work. Reviewed AGENTS, recent commits, source,
tests, roadmap/state, architecture/decisions and the dated engineering reports.

| Repository / audited head | Fresh checks | Interpretation |
| --- | --- | --- |
| Builder `15b7b54` | uv sync; olb check --tests: 305 passed, six health checks; world 0.6.0 verify --self-test passed | Packaging/contracts and eight shipped capabilities are validated engineering |
| Simulation `830379c` | uv sync; ruff; pytest: 214 passed | Runtime/discovery/checkpoints/recovery/resource paths tested on Windows with scripted/fake models |
| Window `9ef9ba4` | uv sync; ruff; pytest: 38 passed | Existing API/archive read-only guarantees and safe rendering checks pass |

S006e is complete within its registered process-tier scope. Its 26 resource tests
cover native aggregate memory/process denial and termination, CPU cap/throttling,
suspended startup ordering, quota denial/live overflow, resume, failures and
unavailable/zero samples. Existing deadline/recovery tests also remain enabled.
Independently reverified resource archives `run-20261114t115404z-96a2a1` and
`run-20261114t115011z-113b13`, plus recovery archive
`run-20261114t111831z-64db06`; all passed the current archive verifier.

The historical S006e validation object is preserved unchanged in
[validation/S006e.json](../roadmap/validation/S006e.json). Completed state entries,
milestone sections, dated engineering reports and source history are retained.
This session's checks are separate; it does not rewrite their dates/results.

| Area | Verified engineering or historical evidence | Still unestablished/planned |
| --- | --- | --- |
| World packaging | Digest-bound minimal 0.6.0, self-tests, eight capabilities and generated discovery data | A sophisticated general computational world |
| Orchestration/comparisons | One local client; recorded model identity, replies, syntactic repairs; historical four-family comparison | Interchangeable independent catalog, hosted broker and controlled behavioural comparison |
| Continuation | Immediate fixed message after tool-free reply; independently recorded | Neutrality, deliberate idle treatment or evidence that continued calls mean continued purpose |
| Registry/discovery | Four meta-tools; directed real search/describe/invoke with argument guidance/repairs | Reliable unguided discovery or native nested-argument competence |
| Memory/checkpoints | SQLite and consistent scripted save/resume, fallback, replay accounting | Model-initiated retrieval and adaptive long-term plans |
| Recovery/resources | Native worker/supervisor faults, bounded retries, OS job limits, supervisor quota and samples | Physical reboot/power loss, Linux execution or long unattended reliability |
| Window | Read-only timeline/tool/artifact views; real text preview evidence and synthetic image checks | Comparative analysis UI, automated front-end rendering suite, real image generation previews and reliable liveness inference |
| Safety | Builder-written process tier; privilege source remains configuration | Container tier, arbitrary code, host computer control and agent-created tools |
| Science | Preserved engineering pilots/failures | Autonomy benchmark, preregistered philosophical campaign or consciousness conclusion |

The candidate report observed requests for humans, invented surroundings,
repeated counting of supplied text, empty visible replies under reasoning budgets
and context loss. It used a two-tool world and varied settings with few repeats;
it does not prove every candidate fails in every richer world. S005b later
demonstrated a directed sequence, not independent discovery. The current richer
world therefore needs a fresh registered baseline, not a stronger retrospective
claim. Historical performance numbers were read, not remeasured in S013.

## Brain swap and controlled model comparison

The scientific purpose is to separate environmental limitations from limitations
of the inhabitant. Local-first and essentially zero-cost remain defaults.

**S007a, local implementation complete (engineering only):**

See [gateway validation](../experiments/2026-11-14-local-gateway.md). The
following design is implemented using a pinned inline catalog snapshot; server
context/sampling/offload remain explicitly unknown in model provenance.


1. Preserve the bundled model-provider manifests as the backward-compatible
   default. Add an approved immutable local catalog using the same versioned
   manifest contract, stored outside agent control and selected by experiment
   configuration. Builder owns definitions; Simulation validates/resolves them
   without importing Builder code. Record catalog bytes/digest in each archive.
2. Allow a top-level orchestrator id from that catalog without rebuilding the
   world release. Pin model digest/quantisation, provider/ref, adapter/version,
   effective context, sampling and offload settings or explicitly mark unknowns.
   Apply contract versioning if launch/archive fields need to change.
3. The world digest, capability registry, demonstrations, generic interface,
   initial prompt/continuation policy, tool permissions and supervisor constraints
   stay fixed between matched arms. Use the same approved model set, selecting
   only the top-level orchestrator differently. Model-provider access must not
   widen tool network permissions; test this separation for local routing too.
4. Use the current small orchestrator and another already-installed approved
   family for engineering acceptance. Larger local/offloaded candidates need
   specific download approval and measured RAM/VRAM/context/latency feasibility;
   larger size is not presumed better autonomy. Do not fill the 16 GB host until
   supervisor/OS headroom disappears.
5. Measure cold/warm load costs separately and specify whether setup is outside
   the active run budget. Effective context must be known or the comparison
   labelled limited; defaults cannot quietly vary between arms. Provider seeds
   are recorded controls, not deterministic-trajectory promises.
6. Keep specialist models.ask and unload/load/reload leasing in S007e. This
   preserves the original gateway ambition while making S007a a bounded next
   step; simple-tool baseline does not wait for specialist tools.

**Optional S007f decision, then separately authorised S007g code:**

- ADR-0005's loopback restriction remains effective. This planning note does not
  approve external requests. A separate approved ADR must identify the provider,
  egress endpoints, data leaving the machine and reproducibility limitations.
- Credentials stay in an approved secret store or file outside all repositories,
  archives and workspaces. Only a supervisor-side provider broker resolves an
  opaque credential reference; keys never enter worker/tool environments,
  model messages, logs or raw diagnostics. Test redaction on errors and retries.
- Provider egress authority is separate from agent tool network authority. A
  hosted orchestrator does not grant browsing, shell, arbitrary HTTP or host
  access to tools. The agent receives the same discovery interfaces/constraints.
- Record provider/model/version/snapshot identifiers when available, request
  settings, API/adapter version and returned usage. If weights/version cannot
  be pinned, state that limitation; do not manufacture an equivalent local digest.
- No paid request without explicit human authorisation and a finite approved
  currency/financial and token allowance. Default is disabled and zero-spend.
  Reserve conservative worst-case input/output/reasoning and price bounds before
  each attempt, transactionally across concurrency, retries and restart. Account
  for timeouts, duplicate requests and ambiguous billing at the reserved ceiling;
  do not release an uncertain liability to finance another request.
- Approved pricing/usage semantics and an enforceable per-request upper bound
  are prerequisites, not a best-effort estimator. Unknown tariffs, hidden-token
  charging or billing bounds cause refusal. Stop before another request when a
  bound cannot be demonstrated; do not claim current max_model_tokens support.
- First validate through local fake providers without keys or spending. A real
  smoke check requires the separate specific approval/cap. Remote runtime/compute
  limits cannot be equated with local Job Object limits; report differences.

Hosted comparisons remain optional arms. Declining them must not block the local
benchmark, safe capability work, protocol or philosophical research path.

## Policies, safety and interpretable negative results

The existing continuation is factual in wording but still an intervention. The
current immediate reply/call loop can create apparent persistence. S007c versions
legacy behaviour and one bounded quiet alternative before scoring; no scheduling,
context guard, retrieval or prompt is silently changed here. Store exact inputs,
mechanical repairs and context removals. SQLite durability is separate from a
model choosing to retrieve/revise a plan. Checkpoint rollback and replay can
affect action histories and must be reported, not erased.

S007d is the first prospective evidence milestone, fully specified in the existing
experiments page. Its completion means a validated report. The separate expansion
gate asks only for replicated basic discovery/use in one unguided condition;
goal consistency, adaptation and costs stay separate evidence. A GO is not an
autonomy certificate. A valid NO_GO is useful science and directs one bounded
S007h change, not a moving benchmark or an unlimited feature race. Invalid records/conditions yield INCONCLUSIVE and a named validity repair. Valid
failures of the guided control remain negative competence evidence (NO_GO), not
a licence to tune the control until it succeeds.

Container isolation remains a hard gate for arbitrary Python/shell, computer
control, executable proof-language surfaces and agent-created tools. S006c must
test host/repository/archive/network/process/resource/shutdown boundaries on an
actual backend. S006e's process limits are not an OS sandbox: disk can overshoot,
CPU cycles differ from active-time samples and Windows notifications are best
effort. No model output can weaken these boundaries. The human WSL/engine gate
was cleared on 2026-11-14 (ADR-0014) and S006c delivered the Windows container
capability tier (ADR-0015); S006f and later execution milestones remain
independent of local gateway/policy/benchmark/S010 tooling.

S010 freezes conditions and makes comparison/export evidence-linked and read-only.
S011 engineering success remains distinct from its behavioural panel. Unattended
certification requires the actual container tier and actual fault/sleep/reboot
tests; current native process-kill tests are not those future results. Register
whether a 72-hour premise/deadline uses active or elapsed wall time and how
downtime is handled; the current budget excludes downtime, so they are not synonyms.
S012 requires current baseline evidence and all validity/reliability gates. A valid
negative baseline can lead to an explicitly registered bounded null-result
question on the existing world; it cannot be advertised as established autonomy.

## Ordered next sessions and scope control

1. **S007a:** local gateway/catalog and two configuration-only orchestrators, fixed
   world/tool rights, effective context and identity provenance; no hosted calls.
2. **S007c:** versioned continuation/context/idle policy with legacy compatibility.
3. **S007d:** implement/validate the prospective benchmark, preregister then run it;
   report GO/NO_GO/INCONCLUSIVE independently of milestone completion.
4. **If GO:** S007e consultation/leases, or useful narrow S008c, then selected
   vision/audio/generation by utility/hardware. Repeat after each meaningful change.
5. **If NO_GO:** one S007h hypothesis/change and repeat. If still negative, choose
   a documented bounded route or S010 rather than silently escalating capabilities.
6. **Independent:** S006f (S006c is complete); S010 after the baseline report even if
   negative; optional S007f/S007g only with their separate authorisations.
7. **Later:** actual S011 reliability ladder, then S012 under frozen valid conditions.

Completed milestones are not renumbered/reopened. S013 is an unused administrative
planning id, not a new implementation phase after the still-future S012. Templates
apply to revised future work; old completed entries are left as recorded. A brief
scientific-purpose/evidence statement is sufficient for routine milestones; full
preregistration belongs to campaigns, not every small engineering change.

## Session validation and preservation

Baseline checks above passed. Final Builder ruff and olb check --tests passed:
305 tests in 59.05 seconds plus all six health checks. The one-off planning audit
passed unique ids, complete future milestone fields/prerequisite references,
local links/anchors, historical sections/entries and exact S006e validation
preservation, unchanged clean sibling heads and documentation-only scope.
One pre-existing architecture link anchor was corrected. Current validation
records these checks separately from historical S006e evidence. No new autonomy run, hosted request, model download or sandbox test was
performed. S006e's validation, completed entries/sections, and dated reports are
checked against the pre-session Git version; sibling source and working trees
remain unchanged. This is a controlled course correction, not a restart.
