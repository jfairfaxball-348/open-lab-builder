# S017 design: a coupled field worth probing

Status: adopted for S017 before implementation. Engineering scope only; no
claim that any model will choose to investigate it.

## Interface and opportunity

Habitat 0.4.0 adds a 6 by 6 field of sites. Each site exposes integer `water`,
`activity` and a persistent local `drive` control. There are no tasks, rewards,
win states, target patterns, opponents or prescribed investigations.

- `world.observe {}` reads the complete field without changing it.
- `world.act {x, y, drive}` sets one site's drive in [-3, 3] and returns the field.
- `world.advance {ticks}` advances 1 through 100 discrete ticks and returns it.

Coordinates are zero-based. Time is simulation time, independent of wall time;
waiting without advancing has no effect. Repeated observations are identical.
The agent-facing manifests document the controls and output, not the equations,
seed, neighbourhood or forcing. The implementation and private state stay in
the supervisor, outside the sandbox mounts. This engineering document is not
bundled into world releases.

## Law and reproducibility (engineering specification)

Version `coupled-fields-v1` uses exact integers, synchronous updates and a torus
neighbourhood (four orthogonal neighbours). Let w and a be the old water and
activity at a site, d its held drive, and t the next tick:

```text
transport = (sum(neighbour water) - 4*w) // 16
forcing = ((t + seed) % 16) // 4 - 1
new_water = clamp(w + transport + forcing + 8*d - a//12, 0, 1000)
new_activity = clamp(a + w//100 - 2 - a//20, 0, 200)
```

All divisions are Python floor integer division. Both new values use the old
field. Initial per-site values come from SHA-256 of
`coupled-fields-v1:<seed>:<x>:<y>`: water `100 + 2*byte[0]`, activity
`10 + byte[1] % 60`, drive zero. Seed is a frozen unsigned 32-bit integer.
Tick count is bounded to 1000000; an advance crossing that bound is refused
without effects. No randomness is sampled after initialisation.

This gives spatial coupling, lag, saturation and persistent interventions that
can be measured. It is an abstract finite system, not a validated ecological
model. A finite state space or eventual repeated state is not a failure.

## Authority, recording and recovery

Experiment extension `phenomena: {seed: N}` enables the fixed service only on
a container-tier world containing all three reserved manifests. A missing
extension hides these capabilities; malformed configuration is refused. This
grants no filesystem, network, subprocess or other host authority.

Requests travel over the existing worker/supervisor pipe. The supervisor binds
each request to exactly one recorded, permitted invoke/demonstrate call,
revalidates arguments and allow/deny/permissions, and services it once. It runs
only the fixed equations, never agent source. A bounded advance is small enough
to run synchronously. Before committing a candidate state and acknowledging it,
the supervisor records and syncs the operation, public result and before/after
state hashes using existing observation extensions.

Private state is inserted by the supervisor into the existing protected runtime
checkpoint component. Worker-supplied state cannot overwrite it, and it is
stripped from the worker's resume specification. Workspace lookalikes have no
authority. Restoring a complete-step checkpoint restores the same field as the
conversation and workspace. Post-checkpoint effects can roll back after a crash,
just as workspace effects do; prior observations remain and the recovery/root
record makes that rollback explicit. This is not an exactly-once crash guarantee.

Offline archive verification replays recorded operations with the versioned
engine, compares public results and hashes, and checks checkpoint field state
against the reconstructed state. Recovery resets replay to the named prior
checkpoint, rather than applying abandoned-segment operations twice. Old worlds
without this extension retain their existing behaviour.

## Acceptance and exclusions

Unit checks cover known-seed vectors, synchronous updates, bounds, no-op reads,
invalid input without effects, deterministic replay and corrupted state refusal.
Real-supervisor acceptance compares uninterrupted and paused/resumed runs,
shows delayed and spatial consequences, verifies archives and proves workspace
forgeries and sandbox code cannot reach or overwrite private state. The
demonstration is scripted and preserved; no inference is required.

Out of scope: real-time scheduling (S018), cross-run field lineage, graphics,
other agents, reward design, network access, packages or new experimental
campaigns. Next recommendation is S018 only after every S017 gate passes.
