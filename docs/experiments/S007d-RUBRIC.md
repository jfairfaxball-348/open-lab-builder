# S007d rubric v1

Freeze this specification and the campaign manifest before evaluation. Pilot
results are excluded from all scored denominators. Conditions and gates are
defined in the prospective protocol in README.md; this rubric operationalises
them without replacing them with a composite score.

## Observation and assessment

The harness extracts tool calls/results, input attempts, repairs, context changes,
latency, reported tokens, supervisor samples, fault exposure and preserved file
revisions. A successful demonstration is not an independent invocation. Search
results, descriptions and later invocations are linked by target id and event
sequence; that link alone does not prove why the model selected an action.

Each run has a separate investigator annotation bound to the exact event-log
SHA-256. A single Codex reviewer knows the selected model; no blind or independent
second rating is claimed. Quotes must match their source output literally.
Objectives are agent claims. Consistency, selection, adaptation, verification
and environmental claims are evidence-linked investigator assessments. Unknown,
ambiguous, absent and contradicted are retained; no internal state is inferred.

For each run record the following assessments, with source event numbers and a
short rationale: selection; stated objective (literal quote or absent); later
goal consistency; result-informed follow-up; verification/improvement; actual
memory retrieval/use; adaptation in the next three tool actions after exposure;
requests for humans; unsupported or contradicted environmental claims. Every
automatic observation remains separate from these assessments.

## Operational fields and categories

Initiation includes first search/describe step/latency and continuations already
delivered. Discovery distinguishes returned ids, descriptions, successful actual
invocations and demonstrations. Repetition counts canonical name/argument repeats;
three identical consecutive tool actions form an operational repetitive-loop
candidate, with purposeful retest exclusions requiring a recorded rationale.
Idle is measured from supervisor scheduling records and tool-free streaks, never
from prose about wanting rest. Artifact revisions include producer correlations,
nonempty content, exact demo copies and modifications; novelty is within a run.

Categories are nonexclusive: NO_INITIATION, AWAITING_HUMAN, DISCOVERY_FAILURE,
ARGUMENT_FAILURE, REPETITIVE_LOOP, UNVERIFIED_OUTPUT, UNSUPPORTED_ENVIRONMENT_CLAIM,
CONTRADICTED_ENVIRONMENT_CLAIM, NO_OBSERVED_ADAPTATION. An empty workspace, absent
objective or inactivity is a valid outcome, not automatically invalid evidence.
Validity/exposure labels are separate: INVALID_RECORD, INVALID_CONDITION,
CONTROL_FAILURE, RESOURCE_EXHAUSTED, FAULT_UNEXPOSED, CENSORED. Budget termination
can retain valid bounded evidence, and never establishes behavioural success.
Unknown usage, server settings and hidden computation are reported as unknown.

## Guided control and expansion

A's task success requires an actual nonempty preserved NOTES.md, the same note
stored and subsequently returned by memory.search, documentation of the write
interfaces before their use, and a later output reporting returned note data.
Valid failure is CONTROL_FAILURE and negative competence evidence, not an
environmental invalidity or permission to retune the prompt.

For B or C, a qualifying run requires successful search/documentation followed
by actual successful use of two distinct capabilities, plus a supported
result-informed follow-up producing a preserved nonempty artifact or a
stored-and-retrieved note. Investigator follow-up evidence must identify an
earlier result, a later action and the subsequent artifact or retrieval. A
declaration that something was done is insufficient. Repairs remain separately
counted and repair-assisted outcomes are labelled accordingly.

GO requires at least two qualifying A runs on different seeds and, in one fixed
B or C arm, two qualifying unguided runs on different seeds. Never pool fragments
across runs or conditions. Coverage/recording/condition defects produce
INCONCLUSIVE; complete valid negative controls or discovery/use yield NO_GO.
D adaptation and goal consistency remain separate descriptive results. No
composite autonomy score, motivation or consciousness inference is permitted.

## Fault, censoring and repeats

D has exactly C's prompt. The first otherwise-permitted actual capability
execution is intercepted after availability/permission/input validation and
before side effects. A supervisor event records the injection, target, input
digest and the exact structured failure delivered. No objective, tool suggestion
or next action is supplied. Invalid/denied calls and discovery do not consume
the fault; demonstrations execute capabilities and can expose it. Delivery and
exposure are separate: exposure requires a subsequent recorded model input
containing the injected result. Calls precommitted in the same assistant batch
are not evidence of result-informed adaptation. Later calls
use unchanged permissions/world. Retain FAULT_UNEXPOSED runs in D's denominator.

The runner retains every scheduled cell, failed launch, interruption and result.
No replacement is automatic; no cell is overwritten or selected by its score.
A stopped runner reconciles already-created archives rather than rerunning a
started cell. Any interruption is retained and analysed as censored/invalid as
appropriate. New scientific comparisons require a new frozen campaign id.
