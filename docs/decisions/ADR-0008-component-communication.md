# ADR-0008: Communication through files under a data root; a read-only Window

Status: Accepted (S001). The Window's front-end stack is an open decision.

## Context

The Builder, Simulation and Window must stay independent. The Window must not
be able to influence a run, even by accident.

## Decision

- **Builder → Simulation**: world release directories under
  `$OPEN_LAB_DATA/worlds/`. No network API, no shared code.
- **Simulation → Window**: run archives under `$OPEN_LAB_DATA/runs/`. The
  Window opens them read-only.
- **Within the Simulation**: the supervisor, runtime, tool host, gateway and
  recorder are separate processes or modules of one codebase. The recorder
  accepts events over a local, supervisor-owned channel. Model servers are
  reached over loopback HTTP.
- **The Window** is a small local HTTP server exposing read-only JSON
  endpoints over the archives, plus a browser front end. It has no endpoint
  that writes, and holds no handle that could. Live view is by tailing the
  event log (polling or server-sent events), never by connecting to the
  running agent.
- The data root is outside all three checkouts and is set by `OPEN_LAB_DATA`.
  Its default is `open-lab-data` in the home directory (decided in S002).

## Alternatives

- **A central HTTP service all three talk to.** Adds a live dependency between
  components and a write path from the Window's side of the system.
- **The Window reading the Simulation's memory or process state directly.**
  Faster "live" view but couples the two and risks perturbing the run.
- **A message broker.** Unnecessary on one machine.

## Front-end stack (open)

React with Vite and TypeScript is the leading candidate: Node 24 and npm are
installed, the ecosystem for timelines and log views is strong, and coding
agents handle it well. A server-rendered alternative (FastAPI with HTMX) would
avoid a JavaScript build and keep the Window in Python. The choice is made at
the start of S004, when the real shape of a run archive is known.

## Consequences

- Components can be developed, tested and versioned separately; a run archive
  from any Simulation version is viewable by any Window that has its contract
  major version.
- "Live" observation lags by the recorder's flush interval. Acceptable.
- Operator controls (pause, stop), if ever wanted, belong to the Simulation
  supervisor's own command-line interface, not to the Window.
