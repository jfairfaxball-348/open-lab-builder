# Habitat v2 — a universe worth inhabiting

Adopted for planning 2026-11-16 under [ADR-0027](../decisions/ADR-0027-habitat-v2.md).
S020a is implemented in Habitat 1.1.0; [component evidence](demos/S020a.md).
The remaining phases are planned. Active phases and acceptance are in
[ROADMAP.md](../roadmap/ROADMAP.md); [next session](../../NEXT_SESSION.md).

## Ambition and evidence

Provide tools, information, materials, time and persistent projects so the
inhabitant can choose mathematical, scientific, software, artistic or unexpected
interests without continuous human instruction. Examples below are engineering
acceptance fixtures, never an inhabitant task list or initial prompt.
Tool discovery remains search/describe/demonstrate/invoke; availability creates
no duty. Keep the 6×6 field available as an optional system, without expanding it.

[S012-002](../experiments/2026-11-16-s012-002.md) is a positive result: 3587 s
of sustained activity, 151 successful calls, 35 memory writes, one saved skill
and repeated project/handover notes under an assigned objective. Preserve the
report's caveats and unsupported field claims. It establishes sustained prompted
work, not independent goals, consciousness or cross-session cognitive continuity.
S012-001 and S012-002 remain historical records, byte-for-byte untouched here.

**Development freeze on experiments:** no Lunar/full inhabitant runs, survival
studies, comparisons, endurance or behavioural campaigns, exploratory hosted
inference or staged experiments. Use offline engineering checks and fake models.
No inference or downloads in this planning session. After approved provisioning, local model
admission uses bounded offline component checks; the next Lunar run needs a separate owner
decision after v2 is useful. Retain existing hosted profile/effort/limits.

## Current implementation audit

Fetched all remotes on 2026-11-16: only local/remote main branches, clean and
equal at Builder `8ae516f`, Simulation `7fdc97c`, Window `3a88970` before edits.
Read current architecture, contracts, isolation, manifests, Habitat v1,
ADR-0018/0022–0026, both S012 reports and the relevant runtime/Window code.

| Requested freedom | Exists now | Composition or new work |
| --- | --- | --- |
| Mathematics/science | math.evaluate, stats.describe/regress; Python standard library | Fractions, decimal, statistics, algorithms and small simulations compose now. S020a installs NumPy/SciPy/SymPy/pandas/Matplotlib in a digest-bound sandbox image; host packages remain unavailable to Habitat |
| Software creation | workspace write/list/read/edit; python.run; stdout, stderr, tracebacks, timeouts; projects can import their own modules | Already permits write/debug/reuse, JSON/CSV/SQLite and unittest. S020a adds installed-package discovery/docstrings, headless plotting and artifact revision checks; no arbitrary host shell or runtime pip |
| Skills/tools/continuation | skills.save/list/get, tools.create, memory.*, checkpoints, operator data-only lineage | Reuse directly. Child runs inherit files/memory, not trusted registrations, authority or conversation; saved source must be revalidated to register a tool |
| Images | Binary files can be written by Python; Window previews recognised raster formats | S020a delivers Pillow/Matplotlib PNG, diagrams and raster editing. AI generation, editing and inhabitant visual understanding are absent. Window viewing does not give Lunar vision |
| Audio/music | Python wave/struct can write PCM; existing file capture | Procedural composition/DSP compose from Python; add scientific stack, soundfile, FFmpeg, local speech/transcription and optional music model. No playback or audio AI capability today |
| Animation/video | Python can compute frames; Window recognises GIF | Add Pillow animation, FFmpeg assembly/editing/frame extraction, audio muxing and read-only playback. No video AI today |
| Research/library | Workspace reading, SQLite and memory search; registry searches tools, not knowledge | Add licensed offline content and bounded source/page search/read. memory.search is personal notes, not a reference corpus |
| Local delegation | S007e models.ask in minimal world; supervisor specialist.py and finite GPU lease | Single pinned llama3.2:3b only, external/scripted orchestrator, bounded 1–32 calls, ≤6000 input/output chars, ≤1024 output tokens, ≤120 s/call, ≤600 s lease. No models.list or model selection; absent from Habitat |
| Observation | Versioned artifacts, protected archive and read-only text/raster Window | Reuse. Add WAV and one supported video format, basic native controls; no dashboard, execution, conversion or write path in Window |

Specific implementation anchors: Simulation container.py now selects the verified world image or the original
legacy base, and still has no GPU/network path; python.run currently allows 1–60 s and defaults
to 10 s; artifact preservation defaults to 50 MiB/file. Habitat defaults are
1 GiB per capability and 256 MiB workspace, unsuitable as implicit media limits.
The image selector, timeout hierarchy, archive size and resource policy must be
addressed explicitly, without silently raising existing experiment limits.

## Live hardware and deployment feasibility

Read-only probes: olb diagnose --json --save-raw, CIM, nvidia-smi, ollama list/ps,
WSL inventory, Podman images, read-only Ollama /api/show metadata and Simulation
Backend().probe(). Raw diagnostics
remain ignored under .local/. No inference, model loading or container run.

| Resource | Verified on 2026-11-16 |
| --- | --- |
| CPU | Intel i7-11800H, 8 physical cores / 16 threads |
| RAM | 15.7 GiB reported total; 5.9 GiB available at audit, variable |
| GPU | RTX 3050 Ti Laptop, 4096 MiB total, 3962 MiB free, driver 595.97; Intel integrated GPU also present |
| Disk | 931 GiB volume, 659 GiB free; checkpoint/media growth still needs quotas |
| Isolation | Windows 11 build 26300, WSL 2 Ubuntu running; rootless Podman 5.7.0, cgroups v2; pinned python:3.12-slim present and backend probe passes |
| Local text runtime | Ollama 0.40.16 running; no resident models at audit |
| Installed models | llama3.2:3b Q4_K_M 1926 MiB; qwen3:4b Q4_K_M 2382 MiB; qwen3.5:2b Q8_0 2559 MiB; granite4.1:3b Q4_K_M 2002 MiB (on-disk sizes, not RAM/VRAM peaks). /api/show advertises vision for installed Qwen3.5; that is metadata, not tested image inference |
| Host Python only | NumPy 1.26.4, SciPy 1.15.3, pandas 3.0.5, Pillow 12.1.1, soundfile 0.13.1; NetworkX, scikit-learn and Z3 also detected |
| Missing in audited interpreters/PATH | SymPy, Matplotlib, PyTorch, transformers, diffusers, ONNX Runtime, Whisper; FFmpeg/ffprobe, SoX, ImageMagick, Tesseract and eSpeak absent from Windows PATH and WSL PATH |

Not a whole-disk software search: private project environments and non-PATH media
tools are unknown and must not be reused by assumption. Exact runtime/model
compatibility, WSL GPU support, media latency and peak RAM/VRAM are unmeasured.
No throughput estimate below is a measurement of this laptop.

Refresh commands: `uv run olb diagnose --json --save-raw`,
`nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv`,
`ollama list`, `ollama ps`, `wsl -d Ubuntu --exec podman info --format json`.
For an owner-identified candidate executable use `Get-Command <name>` and
`<name> --version`; inspect its package metadata without importing/loading models.
In the implementation session, after approved provisioning, measure a fixed
bounded local fixture directly
through its worker, recording duration, peak resident RAM/VRAM, output validity
and cancellation; never launch an inhabitant simulation to measure feasibility.

## Choices and constraints

All candidates need pinned versions/revisions, hashes and notices at provisioning.
Numbers marked **budget** below are provisional admission ceilings, not measured
requirements or guarantees. Refuse operation if measured peaks plus host reserve
cannot fit; disk weight size alone is insufficient.

| Domain | Recommended route and resource envelope | Licence / readiness |
| --- | --- | --- |
| Scientific workshop | Python 3.12 Linux wheels: NumPy arrays, SciPy integration/optimisation/FFT/statistics, SymPy algebra and mpmath, pandas tables, Matplotlib Agg plots, Pillow drawing. Start ≤2 GiB/call, ≤2 CPU cores; cap BLAS threads. Small jobs fit CPU; large arrays/solvers remain bounded | BSD-family scientific libraries, Matplotlib licence, Pillow HPND. Resolve a compatible set rather than copy mismatched host versions. [NumPy](https://numpy.org/doc/stable/license.html), [SciPy](https://scipy.org/), [SymPy](https://www.sympy.org/en/index.html), [pandas](https://pandas.pydata.org/docs/getting_started/overview.html), [Matplotlib](https://matplotlib.org/stable/users/project/license.html), [Pillow](https://pillow.readthedocs.io/en/stable/about.html) |
| Procedural sound/video | NumPy/SciPy + wave first; soundfile/libsndfile for formats, librosa for analysis if needed. FFmpeg/ffprobe inside the approved image: bounded clips, streams, no network protocols. PNG/GIF, PCM WAV, WebM VP8/Vorbis as initial interoperable targets | [FFmpeg](https://www.ffmpeg.org/legal.html) is LGPL with GPL/nonfree build options: record exact build/codec configuration. [librosa](https://librosa.org/doc/latest/index.html) adds dependencies; add when an actual analysis needs it. No weights required |
| Optional local text | Expose all installed, approved compatible profiles equally. Start context ceiling 2048, output ≤512 tokens, ≤120 s, serial calls, ≤16/run as configurable proposal; model-specific reasoning limits explicit. CPU partial offload acceptable | No new download. Read-only installed metadata confirms Llama 3.2 Community License and Apache-2.0 for both Qwen profiles and Granite; retain exact bundled notices with pinned digests. [Qwen3](https://huggingface.co/Qwen/Qwen3-4B), [Granite](https://huggingface.co/ibm-granite/granite-4.1-3b), [Llama](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct). Failed old autonomy gates do not disqualify bounded text assistance. Hidden reasoning can exhaust Qwen output before visible text; disclose this limitation |
| Image understanding | First assess installed Qwen3.5:2b vision through Ollama: avoids another download/runtime; batch 1, 512-pixel input, short context, serial lease, full peak memory unmeasured and fit not guaranteed. Smaller alternative if needed: SmolVLM-256M-Instruct, 512-pixel bounded input, short local description; CPU first, isolated worker with PyTorch/transformers, no remote code. **Budget** ≤2 GiB RAM, ≤1 GiB VRAM if GPU admitted | [Installed Qwen architecture](https://huggingface.co/Qwen/Qwen3.5-2B), Apache-2.0; local /api/show advertises vision. SmolVLM [model card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct), Apache-2.0; [paper](https://arxiv.org/abs/2504.05299) reports <1 GB GPU inference for smallest model, not every resolution/configuration. SmolVLM needs download/runtime; Qwen needs broker support and bounded local admission only. Modest descriptions, unreliable OCR/math/precise spatial claims; numeric pixel inspection complements it |
| Image generation/editing | SD 1.5 at 512×512, batch 1, ~20 steps; stable-diffusion.cpp prebuilt CPU/Vulkan worker first, approved CUDA build if needed. Text-to-image and img2img plus Pillow crop/composite; masked inpainting only after a compatible pinned checkpoint/backend is verified. **Budget** ≤3 GiB VRAM, ≤3 GiB resident RAM; CPU fallback may be painfully slow | [SD1.5 card](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5): CreativeML OpenRAIL-M restrictions; [runtime](https://github.com/leejet/stable-diffusion.cpp) MIT, CPU/CUDA/Vulkan. Weight quantisation/offload/backend support must match the pinned release. First realistic candidate, not confirmed to fit this host. Avoid a full UI server and large PyTorch diffusion stack initially |
| Speech/transcription | faster-whisper tiny/base CPU int8 first; small only with admission room. Piper single licensed English voice through CPU ONNX. **Budget** ≤2 GiB for transcription, ≤1 GiB speech synthesis, short clips, no concurrent models | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) MIT; upstream small/int8 CPU example uses ~1477 MB and 1m42s on its own benchmark hardware, not this laptop. [Piper](https://github.com/OHF-Voice/piper1-gpl) GPL-3.0, voice licences separate. [whisper.cpp](https://github.com/ggml-org/whisper.cpp) MIT is lower-dependency CPU alternative |
| Neural music/sound | MusicGen-small 300M, 5–10 s mono excerpts, CPU fallback; prefer transformers worker over a full studio stack. **Budget** ≤3 GiB RAM, ≤3 GiB VRAM; admit only after real peak/latency check. Procedural synthesis remains available regardless | [Model card](https://huggingface.co/facebook/musicgen-small): CC-BY-NC-4.0 weights, noncommercial restriction; short music candidate, not a general sound-effects understanding model. Requires download/runtime; slow generation and poor long-form structure expected, no real-time promise |
| AI video generation | Wan2.1-T2V-1.3B considered, excluded from v2 core: upstream quotes 8.19 GB VRAM and ~4 min for 5 s on RTX4090. SVD-XT img2vid considered, no credible 4 GB/available-RAM admission demonstrated | [Wan](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B), Apache-2.0; [SVD-XT](https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt), custom community terms. Quantisation/offload could make tiny jobs technically possible but likely painfully slow; no download or promise. v2 video is generated frames, motion, edits and FFmpeg composition |

**Delivery classes:** usable immediately through composition: small standard-
library maths/software, WAV synthesis and simple raster data. Short engineering
work with approved packages: science/plots, PNG/GIF, reference search, FFmpeg
editing/composition, local text brokerage. Downloads and substantial worker work:
vision, SD1.5, transcription, speech and optional neural music. Painfully slow:
CPU diffusion/neural music and heavily offloaded models. Not presently viable as
a useful supported feature: mainstream neural video generation, large concurrent
models, real-time high-quality generative media. No hardware purchases assumed.

## Information worth exploring

Ship a small versioned offline library with discoverable `library.search/read`
and stable source ids, titles, revisions, licences, hashes and page/section
references. Start with Python and installed-package manuals, an introductory
algebra/calculus/statistics reference, programming text and a few licensed small
CSV datasets. Synthetic mathematical datasets with documented generators are
useful, but include genuine licensed reference material too. Keyword/SQLite FTS
retrieval is enough initially; no embedding model, vector database or internet.

[Python documentation](https://docs.python.org/3/license.html) has PSF terms;
[Think Python 3](https://greenteapress.com/wp/think-python-3rd-edition/) has
CC-BY-NC-SA-4.0; [OpenStax licensing](https://help.openstax.org/s/article/Licensing-information-of-OpenStax-textbooks)
currently states CC-BY-NC-SA. Check each book/edition and third-party material,
retain attribution and adaptation terms; do not assume all textbooks are CC-BY.
Starter candidates: [Calculus Volume 1](https://openstax.org/details/books/calculus-volume-1)
and [Introductory Statistics 2e](https://openstax.org/details/books/introductory-statistics-2e);
verify the acquired editions and their own notices at provisioning.
[UCI Iris](https://archive.ics.uci.edu/dataset/53/iris) is a small CC-BY-4.0
structured-data candidate with an explicit source citation.
No indiscriminate book scraping or unlicensed paper corpus. Download only after
approval. Initial library can be copied into the immutable release under a
read-only directory; do not add arbitrary host mounts. Inhabitant notes, source
comparisons, diffs and citations live in its persistent workspace. Papers can
be Markdown with formula source, plots and citations; PDF typesetting is optional.

## Architecture and concrete security work

- **Workshop:** bind an approved image digest to the verified release/config and
  archive it; refuse missing/mismatched images, never pull at runtime. Keep the
  legacy constant for legacy worlds. Define the additive contract before code,
  version schemas/examples/changelog when it changes their shape. Dependencies
  are preinstalled read-only; package imports cannot fetch the internet. Writable
  Matplotlib/cache/temp paths stay in bounded workspace or tmpfs. No Jupyter
  server, browser control, arbitrary host shell or exposed app listener.
- **Project interfaces:** programs may generate static HTML, source and small
  applications as files. Do not render agent HTML/SVG/JavaScript in Window's
  origin. A future interactive preview needs its own isolated viewer; not core v2.
- **Brokers:** use existing supervisor IPC/reservation/admission patterns. Add
  models.list over frozen approved profiles; models.ask takes a bounded id and
  prompt, never a URL/path/command. Local media worker inputs are validated bounded
  bytes/artifact ids, not arbitrary host filenames. Copy to private staging;
  fixed worker command and model hash, no tools or privileges from model replies.
  Broker-owned output goes through normal workspace containment, artifact capture
  and quotas; no returned path can reach archives or protected resources.
- **Isolation:** model/decode workers run separately from recorder with restricted
  filesystem, no outbound network and finite process lifetime. CPU workers should
  use the container tier where practical; a host GPU worker needs explicit
  restricted-process provisioning and tests, not trust in loopback alone. Sandbox
  Python never gets GPU/network or a broker socket. Malformed media, decompression
  bombs, traversal, symlinks, prompt injection and forged service calls are tests.
- **Scheduling:** extend the existing one-owner lease across Ollama and media;
  one heavyweight job at a time, CPU as well as GPU when RAM is scarce. Initial
  host reserve 2 GiB beyond observed baseline; admission sums measured peaks,
  WSL/decoder overhead and active tasks, then rechecks before dispatch. Proposed
  2–3 GiB worker ceilings require measurement. Fail busy/resource-unavailable,
  never kill unrelated applications, swap by design or silently choose another
  model. Cooperative lock is not hard VRAM isolation; external clients can race.
- **Limits:** reserve calls before dispatch, bound context/pixels/frames/duration,
  samples/output bytes, wall time, RAM and threads. Model operations may need
  minutes; design explicit worker timeouts/cancellation plus supervisor liveness,
  rather than bypassing python.run's 60 s cap. Partial outputs stay labelled;
  failed jobs consume reservations. Expire/unload on stop, bounded keep-alive
  after crashes; resume never grants new resources or resets budgets.
- **Persistence/observation:** preserve source, seeds, parameters, hashes and
  finished bytes with revisions. Keep supported outputs below the existing
  50 MiB capture cap initially, or explicitly version a bounded preservation
  policy before larger artifacts. Confirm final checkpoint and lineage retain
  binary files. Window adds signature-validated WAV/WebM playback, no autoplay,
  bounded streaming/range handling, CSP media-src self, nosniff; no transcoder,
  active document execution, filesystem writes or calls back into Simulation.
  Lunar uses local vision, audio metrics/transcripts and sampled-frame summaries
  to inspect outputs; hosted orchestration receives text, never media payloads.

## Delivery sequence and useful-state boundary

1. **S020 Workshop and library:** scientific Python + project reuse, offline
   references, procedural illustration/composition, FFmpeg animation and basic
   observation playback. First bounded slice S020a is the scientific image.
2. **S021 Local assistants and visual creation:** optional installed-model
   delegation and local image understanding/generation/editing, with one bounded
   resource scheduler. Do not postpone images behind research administration.
3. **S022 Sound and audiovisual completion:** local transcription/speech,
   optional short neural music, video frame/audio analysis and finished media.

S020a is a focused cross-repository engineering slice. S020's corpus/media
completion takes additional sessions; S021's image pinning, brokers and restricted
workers are the largest implementation work; S022 reuses those boundaries.
No invented calendar estimates: package provisioning, licence checks and local
admission measurements determine elapsed time.

Useful Habitat v2 means a container world can retain/revise a cited investigation,
software project, data analysis/plot, illustration, composition and simple video;
search/read actual offline references; inspect its media locally; optionally ask
an installed local text model; and recover/transfer the resulting files/memory.
Prove these possibilities with independent offline fixtures and fake broker
integration, never a full inhabitant simulation. Actual media-model availability
additionally requires an isolated local functional check after approved provisioning: do not call
mock-backed routing a working generator. Neural music may remain explicitly
unavailable if it fails admission; procedural composition is mandatory. Neural
video is the declared hardware exception. Image generation/understanding and
speech/transcription remain required unless the owner explicitly revises scope.
Completion never authorises the next Lunar experiment automatically.
