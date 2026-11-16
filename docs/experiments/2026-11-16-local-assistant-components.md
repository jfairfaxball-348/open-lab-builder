# S021a — local text assistant component evidence

Engineering verification, 2026-11-16; no inhabitant, behavioural experiment or
quality comparison. S021 was split before implementation into S021a text and
required S021b visual work. Parent S021 remains incomplete.

Habitat 1.3.0 adds neutral models.list and explicit-id models.ask using ADR-0028.
Release digest: `122e50d3778b2205841545a12e02a4947e5c21e1685ffa3e14162bea50f533fb`.
The scientific/reference/FFmpeg image is unchanged. Builder self-tests use fakes;
Simulation's generated fixture is copied byte-for-byte, including upstream texts.

## Bounded installed-model checks

Exactly one direct text request per installed profile: “Reply with exactly LOCAL.”
Each returned LOCAL, truncated=false, unloaded and stopped its service thread.
No new weights, runtime install, hosted request or primary configuration change.
These establish availability, not quality or autonomy. Profiles have no tools.

| Profile | Seconds including load/unload | Reported CPU allocation MiB | Reported VRAM allocation MiB |
| --- | ---: | ---: | ---: |
| granite-text / granite4.1:3b | 8.297 | 0 | 2228.85 |
| llama-text / llama3.2:3b | 4.641 | 0 | 2216.36 |
| qwen3-text / qwen3:4b | 12.219 | 851.24 | 2231.91 |
| qwen35-text / qwen3.5:2b | 18.578 | 984.90 | 1808.05 |

Exact pinned digests/licences are in worlds/habitat/models/ollama-assistants.json.
No model is preferred; past orchestrator performance does not disqualify an
assistant. Llama's community licence differs from the Apache-2.0 profiles.

Policy: context 2048; output 1024 tokens / 6000 characters; prompt 512 characters;
120 s timeout; 10 s residency; model budgets RAM 2048 / VRAM 3584 MiB and free
reserves RAM 2048 / VRAM 256 MiB. Pre-load available RAM was 4880–5731 MiB and
VRAM 3962 MiB. After-load samples remained at least RAM 4383 / VRAM 1420 MiB.
Resident contexts matched 2048. Server allocations exclude other host/WSL overhead;
zero CPU allocation does not mean zero process RAM. These are point samples,
not independently measured peaks. Hidden reasoning was discarded. CPU-only
routing is fake-tested; actual CPU speed and larger contexts remain unknown.

## Verification and limits

Direct fake services cover all selections, switching, explicit permissions,
forged/replayed RPC denial, reservation before dispatch and conserved consumed
counts, context/resources/identity refusals, redirects, timeouts, CPU-only
options, truncation and cancellation during headers/body. ToolHost discovery,
list and ask use the actual broker boundary without an inhabitant loop.

The initial Windows header-cancellation check failed: cross-thread socket close
waited for the server. A polling raw reader fixed interruption in the reading
thread; both cancellation assertions pass without relaxing their bounds. An
initial Builder test incorrectly expected ordinary MCP invocation to succeed;
it now verifies refusal without an injected fake and success with that fake.

The cooperative lease cannot enforce hard model-server RAM/VRAM ceilings or stop
unrelated host clients. Abrupt loss relies on finite server keep-alive. Linux
execution remains unverified. Visual understanding/generation/editing are absent
and required next. Full Simulation/scripted inhabitant tests were intentionally
excluded. Final commands/counts are recorded in development-state validation.
