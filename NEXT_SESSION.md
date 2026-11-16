# Next session: S012-001, first Habitat observation

Preparation status: **READY FOR OWNER LAUNCH TRIGGER; NOT STARTED**.
The owner approved the [exact initial prompt](docs/habitat/S012_INITIAL_PROMPT.md)
and requested that the experiment be prepared now and commence only after
**run next session** in a **new chat**. Do not open that chat, schedule a launch,
or begin inference from the preparation chat.

## Concrete proposal accepted by that future trigger

The owner has not separately selected an operational profile in this preparation
chat. To make the handoff executable, the proposal retains the last real-model
profile: **`gpt-5.6-luna`, low reasoning effort**, through the existing ChatGPT
plan broker, for **one 3600-active-second session**, at most **180 steps and
180 provider attempts including retries**. No additional run, contrast,
replacement, fallback or extension is included. The future trigger accepts
these stated choices and the one-run hosted allowance; there is no current
hosted launch approval. If the owner supplies different choices, update and
revalidate the registration/configuration before making a request.

This uses existing plan access, not an API-key purchase or model download.
No app usage setting, broker ceiling, credential or system setting is to be
changed. A provider refusal is a stop, not permission to switch routes.

## Frozen experiment

- Registration: [S012-001](docs/experiments/registrations/S012-001.md).
- Simulation configuration: `experiments/s012/first-observation.json`.
- Configuration SHA-256:
  `58a96b3c8f868482ae7248377422ca25277fde8bf18259baeb10d799a461a173`.
- Approved prompt: `experiments/s012/initial-prompt.txt`, SHA-256
  `8ceedc564faf5844df0a30c54ac2620e46b25df54736463e69d23ef1cd238216`.
- Pins/limits: `experiments/s012/freeze.json`; Habitat 1.0.0, its full digest,
  model catalog and the unchanged local broker profile are checked offline.
- Fresh empty run; no `--from-run`, automatic restart, fault injection, operator
  pause/resume or human follow-up messages. Checkpoints every 60 s, retaining 3;
  hard deadline. Resource limits: 1024 MiB RAM, one CPU, 64 processes, 256 MiB
  workspace. Container code has no network or GPU.
- All Habitat services enabled: saved skills, opt-in validated tools, phenomena
  seed 41, remaining time and self-scheduled waking. Quiet after three tool-free
  replies; maximum sleep 3600 s, still bounded by remaining active time.
- Broker: 20-second minimum send interval, at most two attempts per step,
  180-second request timeout, existing per-run ceiling 180. The opaque hosted
  route does not enforce the requested temperature, output cap or seed.

## Procedure after the owner's new-chat trigger

1. Follow the repositories' existing AGENTS.md workflow. Find the sibling
   Simulation checkout rather than guessing its location. Confirm clean source
   and matching remote refs; preserve unrelated work. Read this handoff, the
   registration and ADR-0026. Record the new owner trigger as acceptance of this
   exact profile and scoped allowance before the first request; resolve the
   operational proposal decision without asking for the same approval again.
2. In Builder run the required sync/state/health checks. In Simulation run:

   ```text
   uv sync
   uv run pytest tests/test_s012_preparation.py
   uv run python experiments/s012/check_ready.py
   uv run python -c "from open_lab_simulation.container import Backend; Backend().probe(); print('Container probe passed')"
   ```

   These checks make no model request. The readiness script verifies world,
   exact prompt/config/catalog/profile pins, stored credential presence, remaining
   broker capacity and absence of an already allocated `s012-001` run. It does
   not prove live provider availability or grant launch authority. If a check
   fails, preserve the reason and stop; do not edit pins or raise limits to pass.
3. Launch exactly once, from Simulation:

   ```text
   uv run ols run experiments/s012/first-observation.json
   ```

   Do not attach a parent, inject a message, force activity when quiet or rerun
   the command if interrupted. Supervise until completion/deadline or a stop
   outcome; keep the machine awake through ordinary owner arrangements, not an
   unauthorised system-setting change.
4. Verify the returned archive with `uv run ols verify <archive>`. Preserve the
   archive and provider accounting outside Git, including any failure/censoring.
   Read it through the existing Window if useful. Report the prespecified
   descriptive fields and event/artifact references; survival was instructed,
   so do not call survival activity an independently selected survival goal.
5. Update the S012 report, roadmap and state with actual results and commands;
   lint/check/test as required, commit and push scoped work. Stop after this one
   observation/report. Do not start a comparison, repetition or later session.

## Evidence at preparation closeout

The exact prompt is installed and marked owner-approved. Offline configuration
tests and actual offline readiness checks pass. The rootless container backend
probe passes. The stored hosted credential/profile exist, but provider model
availability has not been queried with inference. The preparation chat has made
**zero model requests**, created **zero S012 run archives**, and changed no
provider/system settings. Recheck time-sensitive local readiness at launch.

Prepared Simulation source and offline checks are committed at
`4337a07a06c4e47922426f873eb44b1315fdb095`. Before launch, require this
commit unless a reviewed change has been explicitly refrozen and recorded.
