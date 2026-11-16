# ADR-0024: Supervisor-owned coupled fields

Status: Accepted (S017). Extends the S007e mediation pattern without changing
the three-repository boundary or adding an execution privilege.

The field specified in [PHENOMENA_V1.md](../habitat/PHENOMENA_V1.md) is owned by
the Simulation supervisor. Builder ships only reserved `supervisor-world`
MCP manifests for `world.observe`, `world.act` and `world.advance`, in Habitat
0.4.0. Rule source, seed and private state are never mounted into the sandbox.
Builder self-tests inject a labelled unavailable fake; real service acceptance
is tested through the supervisor and actual container world.

Every service operation is bound to a recorded permitted call and journalled
before acknowledgement. Pure candidate transitions, strict bounded data and
fixed equations keep arbitrary agent code out of the supervisor. The private
snapshot is added to the existing runtime checkpoint component by the supervisor
and removed from the worker's resume data. Recorded roots, operations and hashes
support deterministic offline replay and explicit checkpoint rollback. Existing
schemas' extension points suffice; no shared schema changes are required.

Storing the world in the workspace was rejected because `python.run` could
rewrite it. Bundling the rule source in the immutable release would expose
the laws to arbitrary sandbox code before investigation. A new world framework,
state database, task system or graphics layer is unnecessary for this slice.
