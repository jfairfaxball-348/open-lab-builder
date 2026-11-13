"""Turn a diagnostic report into readiness judgements and readable text."""

from __future__ import annotations

from typing import Any

USABLE = "usable"
NEEDS_VALIDATION = "needs_validation"
NEEDS_INSTALL = "needs_install"


def _found(report: dict[str, Any], group: str, name: str) -> bool:
    return bool(report["tools"].get(group, {}).get(name, {}).get("found"))


def _package(report: dict[str, Any], name: str) -> str | None:
    return report["python"]["packages"].get(name)


def assess(report: dict[str, Any]) -> list[dict[str, str]]:
    """Classify capability areas as usable, needing validation, or needing installation.

    The rules only look at what the probes found. 'usable' means the software
    answered a probe, not that a capability built on it has been tested.
    """
    rows: list[dict[str, str]] = []

    def add(area: str, status: str, note: str) -> None:
        rows.append({"area": area, "status": status, "note": note})

    ollama = report["ollama"]
    if ollama["running"] and ollama["models"]:
        add("Local text models", NEEDS_VALIDATION,
            f"Ollama serving {len(ollama['models'])} model(s); none validated by this project yet.")
    elif ollama["installed"]:
        state = "running" if ollama["running"] else "installed but not running"
        add("Local text models", NEEDS_INSTALL, f"Ollama {state}; no models pulled.")
    elif _package(report, "llama_cpp_python"):
        add("Local text models", NEEDS_INSTALL, "llama-cpp-python present; no model files found.")
    else:
        add("Local text models", NEEDS_INSTALL, "No model server found.")

    nvidia = [g for g in report["gpus"] if g.get("vendor") == "nvidia"]
    if nvidia:
        vram = nvidia[0]["vram_total_mb"]
        add("GPU acceleration", USABLE, f"{nvidia[0]['name']} with {vram} MiB VRAM.")
    else:
        add("GPU acceleration", NEEDS_INSTALL, "No NVIDIA GPU detected; CPU inference only.")

    iso = report["isolation"]
    if iso["docker"] or iso["podman"]:
        add("Container isolation", NEEDS_VALIDATION, "Container engine on PATH.")
    elif iso["wsl"]["working"]:
        add("Container isolation", NEEDS_INSTALL, "WSL works; no container engine installed.")
    else:
        add("Container isolation", NEEDS_INSTALL,
            "No container engine; WSL absent or not functional.")

    add("Python tooling", USABLE if _found(report, "python", "uv") else NEEDS_VALIDATION,
        f"Python {report['python']['version']}"
        + ("; uv available." if _found(report, "python", "uv") else "; uv not found."))

    science = [n for n in ("numpy", "scipy", "pandas", "scikit-learn", "networkx", "z3-solver")
               if _package(report, n)]
    add("Scientific Python", NEEDS_VALIDATION if science else NEEDS_INSTALL,
        ("In base interpreter: " + ", ".join(science) + ". Must be pinned into a world.")
        if science else "No scientific packages in the base interpreter.")

    add("Formal proof (Lean)",
        NEEDS_VALIDATION if _found(report, "science_and_maths", "lean") else NEEDS_INSTALL,
        "Lean toolchain on PATH." if _found(report, "science_and_maths", "lean")
        else "Lean not found.")

    add("Audio/video processing",
        NEEDS_VALIDATION if _found(report, "media", "ffmpeg") else NEEDS_INSTALL,
        "FFmpeg on PATH." if _found(report, "media", "ffmpeg") else "FFmpeg not found.")

    add("Deep-learning runtime",
        NEEDS_VALIDATION if _package(report, "torch") else NEEDS_INSTALL,
        f"PyTorch {_package(report, 'torch')}." if _package(report, "torch")
        else "PyTorch not installed; needed by most vision, speech and generation models.")

    add("Browser automation",
        NEEDS_VALIDATION if _package(report, "playwright") else NEEDS_INSTALL,
        "Playwright package present; browser binaries unverified."
        if _package(report, "playwright") else "Playwright not installed.")

    add("MCP tooling", NEEDS_VALIDATION if _package(report, "mcp") else NEEDS_INSTALL,
        f"mcp SDK {_package(report, 'mcp')}." if _package(report, "mcp") else "mcp SDK not found.")

    add("Git and GitHub",
        USABLE if _found(report, "version_control", "git") else NEEDS_INSTALL,
        "git" + (" and gh" if _found(report, "version_control", "gh") else "") + " on PATH.")
    return rows


def render_text(report: dict[str, Any]) -> str:
    """Human-readable summary of a sanitised report."""
    cpu, mem, disk = report["cpu"], report["memory"], report["disk"]
    lines = [
        f"Open Laboratory environment diagnostic ({report['generated_at']})",
        "",
        f"OS       {report['os']['system']} {report['os']['release']} "
        f"{report['os']['edition'] or ''} ({report['os']['version']})",
        f"CPU      {cpu['name']} | {cpu['architecture']} | "
        f"{cpu['physical_cores'] or '?'} cores / {cpu['logical_cores']} threads",
        f"RAM      {mem['total_gb']} GB total, {mem['available_gb']} GB available",
        f"Disk     {disk['free_gb']} GB free of {disk['total_gb']} GB",
    ]
    for gpu in report["gpus"]:
        vram = f"{gpu['vram_total_mb']} MiB VRAM" if gpu.get("vram_total_mb") else "shared memory"
        lines.append(f"GPU      {gpu['name']} ({vram})")
    iso = report["isolation"]
    lines.append(
        f"Isolate  docker={iso['docker']} podman={iso['podman']} "
        f"wsl_working={iso['wsl']['working']} hypervisor={iso['hypervisor_present']}"
    )
    ollama = report["ollama"]
    models = ", ".join(m["name"] for m in ollama["models"]) or "none"
    lines.append(f"Ollama   installed={ollama['installed']} running={ollama['running']} "
                 f"models: {models}")

    lines += ["", "Tools"]
    for group, tools in report["tools"].items():
        found = [f"{name} ({entry.get('version') or 'version unknown'})"
                 for name, entry in tools.items() if entry["found"]]
        missing = [name for name, entry in tools.items() if not entry["found"]]
        lines.append(f"  {group}")
        for item in found:
            lines.append(f"    + {item}")
        if missing:
            lines.append(f"    - missing: {', '.join(missing)}")

    packages = report["python"]["packages"]
    present = [f"{n} {v}" for n, v in packages.items() if v]
    absent = [n for n, v in packages.items() if not v]
    lines += ["", f"Base Python {report['python']['version']} packages",
              "  + " + ", ".join(present), "  - missing: " + ", ".join(absent)]

    lines += ["", "Readiness"]
    for row in assess(report):
        lines.append(f"  [{row['status']:<16}] {row['area']}: {row['note']}")
    return "\n".join(lines)
