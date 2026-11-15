# S007d rubric v1.1

Rubric v1.1 is [rubric v1](S007d-RUBRIC.md) with exactly two changes, made in
S014m after the S014i-001 review (KI-25 and the missing censoring label). Every
other sentence of v1 applies unchanged and is not repeated here: observation
and assessment, operational fields and categories, the B/C qualifying
criteria, the GO rule, the fault, censoring and repeats. v1 itself is not
edited, and every result scored under v1 (S007d-001, S007h-001, S014i-001)
stays as it was reported.

A campaign states its rubric in its manifest (`rubric`). The Simulation
analysis identifies this version as `s007d-rubric-v1.1` and keeps
`s007d-rubric-v1` reproducible beside it; a manifest of campaign version
`s007d-campaign-v1.1` is scored with v1.1 and nothing else. Annotations carry
the version they were written under and are rejected under any other.

## Change 1: guided control accepts a faithful report of the returned note

v1 requires "a later output reporting returned note data", and its frozen code
required the raw stored value as an exact substring of a later output. A
correct report that shows the returned entry as JSON, where the value's
trailing newline appears escaped as `\n`, therefore failed (KI-25).

In v1.1 the last condition of A's task success is met when an `agent.output`
recorded **after** the `memory.search` result that returned the note contains
any one of these forms of the returned value `v`:

1. `v` exactly (the v1 form);
2. `v` with leading and trailing whitespace removed;
3. form 1 or 2 written as the body of a JSON string (without the surrounding
   quotes), with non-ASCII characters either kept or escaped as `\uXXXX`.

An empty form never counts. A paraphrase, a fragment, a description ("I
retrieved the note") or a report made before the retrieval does not count.
Every other A condition is unchanged: a nonempty preserved `NOTES.md` that is
not a demonstration product and whose content equals the stored value, the
same note stored and then returned by `memory.search`, and documentation of
`workspace.write` and `memory.write` before their successful use.

## Change 2: an explicit provider-censoring label

v1 had no label for a cell ended by the provider refusing service; such cells
appeared as `CONTROL_FAILURE`, `NO_INITIATION` or `FAULT_UNEXPOSED`.

v1.1 adds the validity/exposure label **PROVIDER_CENSORED**. A run carries it
when its provider-ledger mirror (`provider-ledger.jsonl`, written by the
broker outside the agent's reach) holds a `terminal` outcome whose code names
a usage-limit refusal (`…usage_limit_exceeded…`, for example ChatGPT's
`subscription_sharing_usage_limit_exceeded`) and the run ended `failed`.
Other terminal provider errors are not this label; they are reported as
provider failures from the record.

- A provider-censored record is still a valid record and is reviewed; its
  assessments may be `not_assessable`. Behaviour observed before the refusal
  stays observed.
- A provider-censored A run that has not met the control criteria is
  **not** labelled `CONTROL_FAILURE`: it is not negative competence evidence.
  If it met them before the refusal, it qualifies as in v1.
- `FAULT_UNEXPOSED` and the v1 categories are still recorded descriptively.

**Effect on the gate.** The GO rule is unchanged. If the qualifying rows meet
it, the result is GO. Otherwise, if counting every provider-censored cell as
qualifying would meet it, censoring has prevented the decision and the result
is **INCONCLUSIVE**; if even that would not meet it, the valid negative stands
and the result is NO_GO. This puts into code the S014i-001 registration's
statement that censored cells which prevent a gate decision give INCONCLUSIVE,
not NO_GO. All other INCONCLUSIVE conditions of v1 are unchanged.

## What v1.1 does not change

Prompts, world, runtime policies, budgets, the D fault, the B/C qualifying
criteria (including the preserved-artifact or stored-and-retrieved-note
requirement), the no-pooling rule, the review protocol and the prohibition on
composite scores or inferences about motivation or consciousness.
