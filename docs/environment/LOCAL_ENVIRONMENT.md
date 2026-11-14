# Local environment

Sanitised audit of the development machine, taken on 2026-11-13 during S001
with read-only probes. It contains no user names, paths, host names or file
inventories. Nothing was installed or downloaded apart from this project's own
Python dependencies in its virtual environment.

Re-run the audit at any time:

```bash
uv run olb diagnose
```

`--json` prints the same sanitised data as JSON. `--save-raw` additionally
writes the unsanitised report (with executable paths) under
`.local/diagnostics/`, which Git ignores. Never commit raw output.

## Hardware

| Component | Finding |
| --- | --- |
| Form factor | Laptop |
| CPU | Intel Core i7-11800H, x86-64, 8 cores / 16 threads |
| System RAM | 16 GB (2 × 8 GB); about 6 GB free with a normal desktop session running |
| Discrete GPU | NVIDIA GeForce RTX 3050 Ti Laptop, **4 GB VRAM**, driver 595.97 |
| Integrated GPU | Intel UHD Graphics (shared memory) |
| Storage | One 931 GB volume, about 678 GB free |

## Operating system and isolation

| Item | Finding |
| --- | --- |
| OS | Windows 11 Home, 64-bit, build 26300 (a pre-release channel build) |
| Hypervisor | Present; Virtual Machine Platform feature enabled |
| WSL | Not functional at the S001 audit ("class not registered"). Repaired by the human on 2026-11-14: WSL 3.0.5, Ubuntu on WSL 2 |
| Docker | Not installed |
| Podman | Not installed at the S001 audit. Installed by the human on 2026-11-14 inside WSL 2: 5.7.0, rootless, cgroups v2 (ADR-0014) |
| Windows Sandbox / Hyper-V management | Not available on Home edition |

## Software

| Area | Present | Absent |
| --- | --- | --- |
| Version control | Git 2.54, GitHub CLI 2.93 (authenticated over HTTPS, `repo` scope); all three remotes reachable and empty | — |
| Python | CPython 3.12.10 (only installation), uv 0.11, pipx | conda, poetry |
| Model serving | Ollama 0.40.16, service running on loopback, four models pulled on 2026-11-14 with authorisation: `llama3.2:3b` (2.0 GB), and in S003c `qwen3.5:2b` (2.7 GB), `qwen3:4b` (2.5 GB) and `granite4.1:3b` (2.1 GB); none fits wholly in VRAM at a 4096-token context (measurements in the world's model manifest); `llama-cpp-python` 0.3 in the base interpreter | LM Studio, llama.cpp server binaries |
| Model files | A small Hugging Face cache (one repository, about 81 MB) | Any GGUF/safetensors language, vision or speech model |
| Deep learning | — | PyTorch, TensorFlow, JAX, ONNX Runtime, transformers, diffusers |
| Scientific Python (base interpreter) | NumPy 1.26, SciPy 1.15, pandas 3.0, scikit-learn 1.9, NetworkX 3.4, z3-solver 5.3 | SymPy, Matplotlib, Jupyter |
| Mathematics and proof | Lean 4.35 with Lake (via elan), Z3 through its Python package | Julia, R, Octave, Maxima, SageMath, Coq, LaTeX, Pandoc, gnuplot |
| Audio / video / image tools | `soundfile` and Pillow Python packages | **FFmpeg**, SoX, ImageMagick, Tesseract, eSpeak, Whisper, any speech or generation model |
| Automation | Playwright Python package (browser binaries unverified), `mcp` SDK 1.28, `openai` and `anthropic` SDKs, FastAPI, Uvicorn | pyautogui, Selenium |
| Languages and build | Node 24, npm 11, Rust 1.97 with Cargo | C/C++ compiler on PATH, CMake, Make, Go, Java |
| Coding agents | Claude Code | Codex CLI |

Packages in the base interpreter are not used by this project and should not be
relied on: each world pins its own dependencies.

## Readiness

"Usable" means the software answered a probe. No capability built on any of
these has been tested yet.

| Capability area | Status | What is needed |
| --- | --- | --- |
| Project tooling (Python, uv, Git, GitHub) | Usable now | — |
| Deterministic Python capabilities | Usable now | Implemented in S002 |
| NVIDIA GPU with current driver | Usable now | — |
| SQLite (3.49 via Python) | Usable now | — |
| Local text model | Available | Four tool-capable models in Ollama. None behaves as an autonomous tool user unprompted; see [the S003b check](../experiments/2026-11-14-local-model-check.md) and [the S003c comparison](../experiments/2026-11-14-orchestrator-candidates.md). Choice open (OD-2) |
| Lean 4 proof checking | Needs validation | Wrap and test as a capability (S008c) |
| Scientific Python stack | Needs validation | Pin into a world environment and test (S008c) |
| Browser automation | Needs validation | Install browser binaries; needs the container tier |
| Container isolation | Usable now | S006c backend (ADR-0015); base image `python:3.12-slim` pulled with authorisation and pinned by digest |
| Vision-language model | Needs installation | Model download; must fit 4 GB VRAM (S007b) |
| Audio/video processing | Needs installation | FFmpeg (S008a) |
| Speech recognition and synthesis | Needs installation | Model and runtime, e.g. a Whisper-family model on CPU or GPU (S008a) |
| Image, music, video generation | Needs installation | PyTorch plus models; image generation is marginal in 4 GB, video generation is not realistic on this machine (S008b) |
| GUI automation | Needs installation | Only meaningful inside a VM or container with a display; not before the container tier |

## Bottlenecks

1. **4 GB of VRAM** is the binding constraint. It holds one quantised model of
   roughly 3–4 billion parameters fully on the GPU, or a 7–8 billion parameter
   model split between GPU and CPU at much lower speed. Two models cannot be
   resident together.
2. **16 GB of system RAM**, of which the desktop already uses about 10 GB.
   CPU-side model layers, the agent runtime, a container VM (WSL 2 reserves
   memory) and capabilities all compete for the remainder.
3. **Container isolation is Windows/WSL 2 only** and adds about 0.3–2 s per
   capability call (S006c). It has no network or GPU path yet.
4. **A laptop** on a pre-release Windows build: sleep, lid closure, thermal
   throttling, forced updates and reboots will interrupt multi-day runs.
   Crash recovery is a requirement, not a refinement.
5. Disk is not a constraint (about 678 GB free), which makes generous
   checkpointing and full artifact preservation affordable.

## Resource strategy

- **One GPU-resident model at a time.** The model gateway serialises GPU use:
  to run a specialist (vision, speech, generation) it unloads the orchestrator,
  loads the specialist, runs, unloads, and reloads the orchestrator. Ollama
  supports unloading on request.
- **Small orchestrator by default**, chosen by measurement in S003b: the
  candidate must fit in VRAM with its context window and still call tools
  reliably. Larger partially offloaded models are an option for slow,
  long-duration experiments.
- **Prefer CPU for small specialists** (for example small speech-recognition
  models) so the orchestrator can stay loaded.
- **Budget RAM explicitly.** Every model manifest and capability declares its
  footprint; the supervisor refuses to start work that cannot fit rather than
  letting the machine swap.
- **Limit context length** for the orchestrator; context memory grows with the
  window and competes with the weights for the same 4 GB.
- **Checkpoint often and cheaply**, and treat every run as resumable, because
  the host will sleep or reboot.
- **Measure, then record.** Footprints in manifests are marked
  `measured: false` until measured on this machine.
- **External model services stay optional.** If local orchestrator quality
  proves inadequate for the research questions, an external provider can be
  enabled per experiment, explicitly, with network access granted in that
  experiment's configuration. This is an open decision, not a plan.

## Human actions that would unlock later milestones

| Action | Unlocks | Needed by |
| --- | --- | --- |
| Authorise pulling one small text model into Ollama | A real local orchestrator | S003b |
| ~~Repair WSL 2 (administrator) and approve a container engine~~ Done 2026-11-14 (ADR-0014) | Container isolation tier | S006c, then S008d and S009 |
| Authorise installing FFmpeg | Audio/video capabilities | S008a |
| Review power and update settings for long runs | Multi-day experiments | S011 |
