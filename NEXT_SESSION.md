# Next session — S020b reference library and procedural media

**Development only. Do not launch Lunar, model inference or a full inhabitant
simulation.** S020a is complete: Habitat 1.1.0 has a digest-bound scientific
image and python.packages. Read [S020a evidence](docs/habitat/demos/S020a.md),
[Habitat v2](docs/habitat/HABITAT_V2.md), ADR-0027 and
[S020b scope](docs/roadmap/ROADMAP.md#s020b--reference-library-and-procedural-audiovisual-work).

## First task

In Builder, define a small versioned offline reference library with stable source
ids, citations/licences and bounded library.search/read capabilities. Use actual
licensed programming/maths/science material; preserve original provenance and
attribution, no internet retrieval from the inhabitant. Reuse the read-only
world release and existing discovery. Inspect the existing source/release copier
before deciding where immutable library bytes belong. No vector database or
embedding model is necessary. Coordinate Simulation only where runtime support
is strictly needed; Window changes belong only to its read-only previews.

Complete the remaining phase-1 slice: Pillow/NumPy/SciPy procedural sound/images,
FFmpeg composition/editing/frame extraction, and basic safe WAV/WebM playback in
Window. Inspect scope and split in the roadmap before implementation if one
session cannot deliver it safely. Do not begin S021 or add image/audio models.
Specific new system software/model/content acquisitions require the existing
AGENTS.md approval rules. No such acquisitions are authorised by this handoff.

## Reuse and verification

Find sibling checkouts and follow each changed repository's AGENTS. Start with
status/log/fetch, sync, state and baseline checks. S020a built and tested the
scientific image already; do not rebuild or replace it casually. Its ID and
package lock/recipe/notices are described in Simulation workshop/README.md.
Older worlds retain the S006c image. Build new immutable world versions and copy
generated fixture bytes exactly; never normalise or hand-edit release fixtures.

Use direct sandbox, tool-host, recorder/checkpoint components and fake-service
integration, not a scripted inhabitant loop. Test source search/read/citation,
media creation/editing/muxing, output preservation and malformed/path/size/time
bounds. Retain Window GET/HEAD-only, no disk writes/conversion, no active HTML or
calls into a run. Keep initial outputs below the existing 50 MiB capture cap.
Explicit resource grants remain authoritative; do not alter old experiment pins,
model settings or provider limits. All media AI remains local-only in later slices.

Run lint and relevant suites in changed repositories plus Builder
olb check --tests. Record real outcomes/remaining limits in roadmap/state/docs,
then commit and push scoped work. Existing whole-run tests are outside the v2
verification programme; use their direct component alternatives.

## Following work

S021 adds optional local text delegation and local visual creation/understanding;
S022 adds speech, transcription and audiovisual completion. The 4 GB GPU and
~6 GB available RAM remain binding constraints. No automatic return to S012:
only a separate explicit owner decision can authorise a future Lunar experiment.
