# S005a registry and real text artifact check

Date: 2026-11-14. Engineering validation only: the scripted replies are fixed;
this provides no evidence about autonomous model behaviour.

Minimal world **0.4.0** contains `text.stats`, `math.evaluate`,
`workspace.write`, `workspace.list` and `time.now`. It adds the generated
`registry/index.json` and `registry/docs/<id>.txt`. No schema version or model
selection changed. Runtime discovery is S005b, not part of this check.

The Builder ran:

```text
uv run olb world build worlds/minimal
uv run olb world verify releases/minimal/0.4.0 --self-test
uv run olb world build worlds/minimal --publish
```

Both builds passed their self-tests and had content digest
`8d22ba1fe4bf3aa96cb8cb87b711778d9608d17cfa3ffac423dc1e15ab44d66f`.
The local release verified with self-tests. The Simulation fixture was copied
from that built release, replacing 0.3.0; no bundled file was edited by hand.
All committed Simulation experiment configurations now select 0.4.0. Historical
archives retain their original frozen worlds and configurations.

## Real archive

In the Simulation:

```text
uv run ols run experiments/scripted-workspace.json
uv run ols verify <data root>/runs/scripted-workspace/run-20261114t092522z-097b71
```

The run completed with **15 events**, three successful calls and one
`artifact.created` event. The shipped `workspace.write` wrote
`notes/laboratory.txt`; `workspace.list` listed `notes`; `time.now` returned UTC.
The recorded artifact is revision 1, **84 bytes**, produced by
`tool (workspace.write)`. The archive verified as intact. Preserved text:

```text
Open Laboratory workspace check.
Written by the shipped workspace.write capability.
```

The Window was served with `uv run olw serve --port 8765`. A browser opened the
real archive, selected **Artifacts (1)** and opened `notes/laboratory.txt`.
The table showed its path, revision, byte count, media type, producer and event
sequence (#7); the preview displayed both lines above. All **16 archive files**
had identical SHA-256 digests before and after artifact browsing, and a second
`ols verify` passed. Local snapshots remain under the Simulation's ignored
`.local/`; raw archives and diagnostic paths are not committed.

KI-13 is resolved for a real text artifact. Image previews still have only
synthetic-archive coverage. Linux execution, OS containment of process-tier
capabilities and real-model use of these tools remain unverified. No model was
called, downloaded or changed in this session.

## Automated verification

Builder: **297 passed** through `uv run olb check --tests`, all six health checks
passed; `uv run ruff check .` passed. Tests cover fixed-query relevance, token
normalisation, filtering/limits, stable ties, deterministic index/doc bytes and
release digest, complete manifest rendering including optional fields, UTF-8
writing/overwrite, listing, UTC timestamps, path refusals and self-test workspace
separation. Simulation and Window final suite results are recorded in
`docs/roadmap/state.json`.
