# ADR-0008: Communication through files under a data root; a read-only Window

Status: Accepted (S001). Front-end stack decided in S004 (see below).

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

## Front-end stack (decided in S004)

**The Window is a Python standard-library HTTP server (`http.server`) serving
a JSON API and a static front end written in plain HTML, CSS and JavaScript:
no framework, no build step, no third-party front-end packages.** Its only
runtime dependency is `jsonschema`, used to check events against the schemas
each archive carries.

Two candidates were on the table at S001: React with Vite and TypeScript, and
server-rendered FastAPI with HTMX. Neither was chosen. The reasons, once the
real shape of a run archive was known:

- **The read-only guarantee has to be small enough to check.** The Window's
  defining property is that it cannot write and cannot reach a run. With one
  handler class answering GET and HEAD, one function that opens files, and no
  dependency that does I/O, that property is verified by tests that scan the
  whole source. A web framework or a JavaScript toolchain puts thousands of
  lines the project does not control on the same path.
- **Archive content is untrusted.** Everything displayed was produced by an
  agent. A front end with no dependencies, no inline script and a
  `default-src 'none'` Content-Security-Policy leaves nothing to audit beyond
  one file that only ever creates text nodes.
- **The views are simple.** Lists, a paginated timeline, paired records and
  previews need no component framework. The archive is flat files; the API is
  eight read-only JSON routes and one for images.
- **Archives must stay viewable for years.** A page with no build step and no
  package lock-file does not rot. A Node toolchain would need hundreds of
  packages installed and kept current for no functional gain at this size.
- It keeps to the project's convention: Python, standard library first.

Costs accepted: no type checking of the front-end code, no component library,
and the front end has no automated tests of its own (the API and the
guarantees are tested; rendering is checked by hand in a browser). If the
front end grows past what plain JavaScript carries comfortably (the run
comparison views of S010 are the likely point), revisit this with a new
decision record. The JSON API is the stable boundary, so a different front
end could replace the static one without touching the reader.

Live view is by polling: the page asks for events after the last sequence
number it has seen. Server-sent events were not needed.

## Consequences

- Components can be developed, tested and versioned separately; a run archive
  from any Simulation version is viewable by any Window that has its contract
  major version.
- "Live" observation lags by the recorder's flush interval. Acceptable.
- Operator controls (pause, stop), if ever wanted, belong to the Simulation
  supervisor's own command-line interface, not to the Window.
