# Next session — S020a scientific Python workshop

**Development only. Do not launch Lunar or any full inhabitant simulation.**
Owner direction: [ADR-0027](docs/decisions/ADR-0027-habitat-v2.md).
Read [Habitat v2](docs/habitat/HABITAT_V2.md) and the
[S020a scope](docs/roadmap/ROADMAP.md#s020a--digest-bound-scientific-python-workshop).
The earlier S012 launch handoff is obsolete; reports/registrations and historical
Git versions remain intact. Both S012 allowances were spent, not reusable.

## First development task

In Builder specify the additive digest-bound workshop-image contract; in the
sibling Simulation implement its verified image selector/admission in container.py.
Retain the existing pinned base image for old worlds. Refuse missing/mismatched
images without pulling. Then pin/provision the scientific Python image, expose
package inventory/docs and verify actual maths/data/plot programs through direct
sandbox fixtures. This is S020a, not all three phases at once.

Follow both AGENTS.md files; find sibling checkouts, inspect status/log/remote,
uv sync, olb state and baseline checks. Preserve unrelated work. Builder owns
contracts/manifests/releases, Simulation execution, Window observation. Do not
import code between repositories or hand-edit generated world fixtures.

Target packages: NumPy, SciPy, SymPy/mpmath, pandas, Matplotlib Agg and Pillow on
Python 3.12. Resolve compatible pinned Linux wheels and notices, not host packages.
Use workspace-only caches, bounded BLAS threads and explicit RAM/time policies.
Before any new base image/system-software/model/content acquisition, obtain the
specific approval required by AGENTS.md; this planning session authorised none.
Preparing code/contracts with fakes does not require a model/download decision.
If an essential provision is blocked, report it and retain incomplete status.

## Exit and boundaries

Direct offline container fixtures must execute a symbolic identity, numerical
integration, CSV analysis and saved PNG; edit/re-run a project module, inspect
result bytes and verify capture. Test digest refusal and unchanged legacy worlds,
network/host isolation, timeout and quotas. No full scripted supervisor run:
exercise service handlers and capture/checkpoint components directly as needed.
Run relevant suites/lint in changed repositories and Builder olb check --tests;
update roadmap/state/docs with actual results, then commit and push scoped work.
If tests need a new contract version, update examples/changelog and rebuild fixtures.

No inference, experiments, hosted probes, profile/effort/limit changes, runtime
pip, agent network or GPU devices. All future media AI is local-only, including
understanding. Local functional admission checks follow approved provisioning during the
relevant development slice; real Lunar runs need a separate explicit owner decision after v2 is useful.

## Following work

S020b adds the offline library, FFmpeg/procedural media and basic read-only
playback. S021 adds optional local delegation and image AI; S022 adds speech,
audio analysis and audiovisual completion. Do not defer images for campaigns.
Main obstacles: reproducible image binding, 4 GB VRAM/~6 GB available RAM,
restricted local workers, bounded long jobs and media preservation/decoding.
Neural video is outside the current hardware promise. The 6×6 field stays optional.
