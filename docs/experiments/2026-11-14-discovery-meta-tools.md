# S005b discovery meta-tools: engineering acceptance

Date: 2026-11-14. This is a directed engineering check, not an experiment
about autonomous behaviour. The default remains `llama3.2:3b`; OD-2 is still
deferred. No model was downloaded and no system software was installed.

## Implementation and release

The Simulation now offers only `capabilities.search`, `.describe`,
`.demonstrate` and `.invoke`. It independently implements the published
registry ranking protocol, reads the generated release documentation, and
checks permissions and capability restrictions before returning documentation
or executing code. Demonstrations use real inputs and real execution results
in the actual workspace. Scripted tests exercise all four interfaces, side
effects, denials, malformed requests, unknown ids and unsafe registry paths.

The generic system preamble is recorded before the first model call as
`environment.message(kind=preamble)`. Observation-event **1.2.0** adds that
kind; minimal world **0.5.0** bundles it. Build, verify with self-tests, and
publish all succeeded, with content digest:

```text
21474d3b0b84a6bb0829a08e9c5fd18fb983292749c0533b8afd08f71cfbff0c
```

The Simulation fixture was copied from the built release, never hand edited.
Capabilities, registry format and model manifests are unchanged from 0.4.0.
Existing experiment configurations select 0.5.0; scripted calls now use the
invocation meta-tool. Historical archives are untouched. The Window already
renders other environment-message kinds generically; no Window change was
needed.

The real trials exposed two runtime issues fixed here: the context guard
could blank freshly returned documentation before it reached the model, and
original structured tool arguments were not preserved separately from repaired
execution arguments. The latest assistant/tool group is now retained while
older turns are dropped; both initial messages remain protected. Emitted
tool-call names and argument strings are archived under
`agent.output.payload.extensions.raw_tool_calls` and remain unchanged in the
conversation. No reasoning channel is recorded.

Two syntactic repairs are supported for the invocation meta-tool: decode a
JSON-encoded input object, or unwrap one exact extra `arguments` envelope
containing both `id` and `arguments`. Missing fields and identifiers are never
invented, unexpected fields are not dropped, and schema/permission checks
still apply. Repairs are counted in `model.call`.

## Scripted run

```text
uv run ols run experiments/scripted-discovery.json
```

Two archived runs completed with 23 events each:
`run-20261114t094416z-5ba973` and `run-20261114t094950z-a3b493`.
Both searched, described, executed a shipped writing demonstration and invoked
the discovered writer, preserving two real text artifacts. The automated
suite repeats this against the shipped capabilities and verifies the archives.

## Real model: failed attempts and bounded acceptance

The first launch was refused before creating an archive because Ollama was
not running. The existing installed server was started; no model or setting
was changed. The following trials all ended by their step limits and all
archives verified as intact. Prompts, seeds, limits and runtime fixes varied
during debugging, so these are not repeated samples for a success-rate claim.

| Run | Events | Observed result |
| --- | ---: | --- |
| `run-20261114t094033z-f0bd58` | 40 | Search and invoke succeeded, without describe; counted text included trailing instructions |
| `run-20261114t094138z-84b536` | 88 | Search and describe succeeded; repeated descriptions after fresh documentation was blanked |
| `run-20261114t094321z-48946d` | 87 | With the context fix, search and describe succeeded; invocation inputs remained malformed |
| `run-20261114t094446z-8f51ea` | 59 | Clock discovery/description succeeded; encoded and misplaced input objects failed validation |
| `run-20261114t094558z-4ccfb6` | 43 | Malformed textual calls; no successful tool call |
| `run-20261114t094657z-a07c7f` | 59 | Generic one-tool-at-a-time guidance; discovery succeeded, invocation inputs remained wrong |
| `run-20261114t094746z-dd211e` | 59 | Structured input schema/example added to describe; extra argument wrapping still failed |
| `run-20261114t094842z-2d80e7` | 57 | Complete clock search/describe/invoke sequence with recorded wrapper repairs |
| `run-20261114t095156z-b9ca4b` | 59 | After adding original-call archive logging, discovery succeeded but invocation failed |
| `run-20261114t095258z-e4887e` | 58 | A different prompt/seed found and described the clock but supplied output fields as inputs |
| `run-20261114t095356z-fc27df` | 54 | Final runtime: complete clock search/describe/invoke sequence with explicitly guided argument structure |

The committed `experiments/discovery-check.json` reproduces the **configuration**
of the final check: existing `orchestrator-small` / `llama3.2:3b`, temperature 0,
seed 3, output limit 512, 12 steps, 120-second deadline. This does not promise
an identical model trajectory. Its initial prompt contains no world capability
ids or meta-tool names:

> Discover a capability for the current UTC time and read its documentation.
> Then execute it. Put the discovered identifier in the top-level id field and
> the empty object {} in the top-level arguments field. These are sibling
> fields. The clock needs no input; utc is an output field. Report the returned
> timestamp.

In the final archive, search at **seq 23** returned the clock capability;
describe at **seq 27** returned its documentation, input schema and example;
invoke at **seq 31**, with `id=time.now` and an empty input object, returned
`2026-11-14T09:54:02Z` at **seq 32**. Seq 30 preserves the original structured
arguments, including the input encoded as the string `"{}"`; the client decoded
it and recorded the repair. There were four repaired calls across the run.
It also made an earlier invocation before a successful description and later
repeated the proper sequence; these events remain in the record.

All **13 archives** (11 real-model trials and two scripted runs) passed
`ols verify` / the same `verify_archive` implementation, including hash chains,
bundled schemas and preserved artifacts. They remain under the local data root;
no raw archive, personal path or diagnostic log is committed.

## Validation and limits

Simulation: `uv run ruff check .` passed; `uv run pytest` **126 passed** using
scripted replies and a fake model server. Builder: `uv run ruff check .`
passed; `uv run olb check --tests` **299 passed**, with all six health checks.
The state file records the final validation commands.

The final directed run meets the S005b acceptance criterion. It does **not**
establish unprompted autonomy, reliability on other tasks, or dependable use
of nested inputs. KI-11 and OD-2 remain open; the initial prompt supplies strong
procedural guidance, and execution used recorded repairs. Linux execution,
container isolation and long-run behaviour remain unverified. Next: **S006a —
Durable Memory and Checkpoints**.
