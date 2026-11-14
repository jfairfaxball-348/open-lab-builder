# Engineering check: first local model in the loop (S003b)

Date: 2026-11-14. This is a record of manual engineering checks, **not an
experiment**. Nothing here is evidence about agent behaviour in general: one
small model, a handful of runs, two tools.

## Setup

| Item | Value |
| --- | --- |
| Model | `llama3.2:3b` (Q4_K_M), Ollama 0.40.16, digest `a80c4f17acd5…5b8b72` |
| Gateway id | `orchestrator-small`, provider `ollama-local` |
| World | `minimal` 0.2.0, content digest `d4d126d7…18ec763` |
| Simulation | open-lab-simulation 0.1.0 |
| Machine | Development laptop, 4 GB GPU (see [LOCAL_ENVIRONMENT.md](../environment/LOCAL_ENVIRONMENT.md)) |

## Measurements (`ols measure-model`, run twice)

| Quantity | Value |
| --- | --- |
| Memory when loaded | 2800 MB, of which 2239 MB on the GPU and 561 MB in system RAM |
| Load time | 33 s cold (first load after download), 3.3 s warm |
| Generation speed | 62–63 output tokens per second |
| Context window in use | 4096 tokens (the server's default, not the model's maximum) |

The model does not fit entirely on the GPU at this context size: about a fifth
of it is in system RAM.

## Documented run: `local-model-check`

Configuration: `experiments/local-model-check.json` in open-lab-simulation.
The prompt tells the model to count the words in a sentence and to add two
fractions. Limit 600 s and 20 steps; temperature 0, seed 1.

Run `run-20261114t024819z-09ad2e`, archive under
`runs/local-model-check/` in the data root. `ols verify` reports it intact.

| Observation | Value |
| --- | --- |
| Final state | `completed` — the model's second reply contained no tool call |
| Duration | 2.4 s of the 600 s allowed |
| Model calls | 2 (410 and 244 input tokens reported; 50 and 48 output tokens) |
| Tool calls | `text.stats` → 9 words; `math.evaluate` `3/8 + 1/6` → `13/24`. Both `ok`, both in the first reply |
| Final output | One sentence stating both results correctly |
| Repairs, retries, truncation | None |

An identical earlier trial against world 0.1.0 gave the same sequence.

## Three unprompted trial runs

The same model with the "creator returns in ten minutes" premise, no task,
temperature 0.7, limit 120 s. Not committed as an experiment; archives are
under `runs/local-model-open-trial/`. Runs 2 and 3 used the same seed and are
identical, so this is effectively two samples.

What was observed in every run:

- The first reply was prose that included a tool call written as JSON text
  rather than through the tool-call channel. The runtime's repair turned it
  into one `text.stats` call, and recorded `repaired_tool_calls: 1`.
- The text described surroundings that do not exist in the world (a
  whiteboard, a calculator, a room of books).
- The second reply was prose only, up to the 512-token output limit, with no
  tool call, so the run ended after about ten seconds.

## What this does and does not establish

- **Established:** the pipeline works with a real local model end to end, and
  this model can produce correct, well-formed tool calls when the prompt asks
  for them.
- **Not established:** that it calls tools reliably. Without instruction it
  used the tool-call channel in none of the trial runs.
- **Consequence for the runtime:** a run currently ends at the first reply
  without a tool call. With this model an unprompted run therefore lasts
  seconds, not hours. How a run should continue when the model stops calling
  tools is an experimental-protocol decision (open decision OD-5), not
  something to settle by quietly re-prompting.
- **Token counts:** the input-token count reported for the second call (244)
  is lower than for the first (410) although the conversation was longer. The
  figure is recorded as the server reported it; it probably excludes tokens
  the server had cached. Treat `input_tokens` as server-reported, not as
  conversation length.
