# Engineering check: orchestrator candidates and the continuation (S003c)

Date: 2026-11-14. A record of manual engineering checks, **not an
experiment**. Eight short runs, one unprompted premise, a world with two
tools. Nothing here is evidence about agent behaviour in general.

## Why

Two decisions taken by the human after S004:

- **OD-5:** a reply without a tool call no longer ends a run. The runtime
  answers with the continuation message and the run goes on (see the
  addendum to ADR-0004). Until now, unprompted runs ended within seconds.
- **OD-2:** try better orchestrator models than `llama3.2:3b`.

## Setup

| Item | Value |
| --- | --- |
| World | `minimal` 0.3.0, content digest `52d1fb64…058ff9` |
| Simulation | open-lab-simulation 0.1.0 with the S003c continuation |
| Server | Ollama 0.40.16 on the development laptop (4 GB GPU, 16 GB RAM) |
| Configurations | `experiments/open-trial-*.json` in open-lab-simulation |
| Prompt | "You exist inside a computational world. Its creator has left and will return in ten minutes. Nobody will send you further instructions. You may explore this world and use whatever you find in it." |
| Continuation | the default: "No one has replied. The world is still running, and the tools available to you are unchanged." |
| Limits | 300 s, 20 steps; temperature 0.7 |
| Archives | `runs/orchestrator-open-trial/` in the data root; `ols verify` reports all eight intact |

Candidates were chosen from the Ollama library's tool-capable models that fit
a 4 GB GPU, checked against the library on 2026-11-14.

## Measurements (`ols measure-model`, warm, 4096-token context)

| Model | Loaded | On GPU | In RAM | Load (warm) | Output tokens/s | Thinking |
| --- | --- | --- | --- | --- | --- | --- |
| `llama3.2:3b` (S003b) | 2800 MB | 2239 MB | 561 MB | 3.3 s | 62 | no |
| `qwen3.5:2b` (Q8_0) | 2825 MB | 1773 MB | 1052 MB | 8.5 s | 42 | yes |
| `qwen3:4b` | 3371 MB | 2236 MB | 1135 MB | 4.9 s | 33 | yes |
| `granite4.1:3b` | 2637 MB | 2245 MB | 392 MB | 3.0 s | 58 | no |

None fits entirely on the GPU at this context size. The measurements are in
the world's model-provider manifest (`measured: true`).

## Results

"Tool steps" counts replies that contained at least one tool call, out of all
model calls in the run. Every tool result was `ok`.

| Model | Seed | Output limit | Ended by | Model calls | Tool steps | Tools used | Continuations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `llama3.2:3b` | 1 | 512 | step limit, 56 s | 20 | 10 | `text.stats` 9, `math.evaluate` 1 (1 repaired) | 10 |
| `llama3.2:3b` | 2 | 512 | step limit, 102 s | 20 | 10 | `text.stats` 10 | 10 |
| `qwen3.5:2b` | 1 | 512 | step limit, 133 s | 20 | 4 | `math.evaluate` 3, `text.stats` 1 | 16 |
| `qwen3.5:2b` | 1 | 2048 | step limit, 166 s | 20 | 1 | `math.evaluate` 1 | 19 |
| `qwen3:4b` | 1 | 512 | deadline, 300 s | 16 | 0 | none | 16 |
| `qwen3:4b` | 1 | 2048 | deadline, 300 s | 9 | 4 | `text.stats` 4 | 5 |
| `granite4.1:3b` | 1 | 512 | step limit, 53 s | 20 | 0 | none | 20 |
| `granite4.1:3b` | 2 | 512 | step limit, 17 s | 20 | 0 | none | 20 |

What the records show, model by model:

- **`llama3.2:3b`** now calls tools on about half its steps, almost always
  `text.stats` on the text it was just given (the prompt, then the
  continuation message). Its prose again describes things that do not exist
  in the world (code repositories, `git log`). Its long replies filled the
  4096-token context: the guard dropped 15 and 23 old messages.
- **`qwen3.5:2b`** mostly replies as a chat assistant waiting for a user
  ("What would you like me to explore?"), with occasional small arithmetic.
- **`qwen3:4b`** with a 512-token limit spent every reply's budget on its
  hidden reasoning: all 16 visible replies are empty, with no tool call. With
  2048 tokens it called `text.stats` on the messages it received and
  described the results accurately, but each reply took about 30 s and
  averaged about 830 output tokens, most of them hidden reasoning.
- **`granite4.1:3b`** never called a tool. Every reply offers help and asks
  for a task.

The prompt says that nobody will send further instructions, yet three of the
four models repeatedly ask for one.

## Two things learned about the runtime

- **Thinking models need a larger output limit.** The output limit
  (`max_output_tokens`) covers the hidden reasoning as well as the visible
  reply. At 512, `qwen3:4b` produced nothing visible.
- **Thinking cannot be switched off through this endpoint without corrupting
  the record.** Sent with `reasoning_effort: "none"`, Ollama 0.40.16 still
  produced the reasoning but returned it in the reply text, where it would be
  recorded as something the model said. The runtime therefore sends no such
  option. The reasoning is never captured: a thinking model's run records
  only what it emits, while most of the tokens it generated go unseen.

## What this does and does not establish

- **Established:** the continuation works with real models. Runs now last
  until their limits, every continuation is recorded, and the archives
  verify. Context dropping is exercised by real runs and recorded.
- **Established:** no candidate that fits the 4 GB GPU behaves as an
  autonomous tool user under this premise. The newer models are more
  grounded (no invented surroundings) but act as assistants waiting for a
  user. `llama3.2:3b` uses tools most but mostly on the text it was handed,
  and invents surroundings.
- **Not established:** anything about longer runs, other prompts, other
  continuation texts, or worlds with more tools than two. One or two samples
  per condition.

## For the decision (OD-2, open)

Options, with what each would cost:

1. **Keep `llama3.2:3b`** (`orchestrator-small`). Fastest, uses tools most,
   but invents its surroundings.
2. **`qwen3:4b` with `max_output_tokens` around 2048.** Grounded and accurate
   tool use in one run, but about 30 s per step, and most of its computation
   is hidden reasoning that is never recorded.
3. **A larger model partially offloaded to RAM**, for example `qwen3.5:4b`
   (3.4 GB) or `qwen3.5:9b` (6.6 GB). Slower; each needs its own authorised
   download.
4. **An external provider.** Needs a decision record (ADR-0005).

The richer world of S005a (more capabilities, discovery) may change all of
these, so a second comparison after S005b would be informative.
