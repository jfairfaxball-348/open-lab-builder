"""Collect machine facts using only read-only probes and the standard library.

``collect()`` returns the raw report, which includes resolved executable paths
and must stay on the local machine. ``sanitise()`` strips everything that could
identify the user or the host, and is the only form that may be printed into
documentation or committed.
"""

from __future__ import annotations

import ctypes
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROBE_TIMEOUT_S = 15

# (executable, arguments that print a version). Grouped by what the tool enables.
TOOLS: dict[str, list[tuple[str, list[str]]]] = {
    "version_control": [("git", ["--version"]), ("gh", ["--version"])],
    "python": [("python", ["--version"]), ("uv", ["--version"]), ("pipx", ["--version"]),
               ("conda", ["--version"])],
    "isolation": [("docker", ["--version"]), ("podman", ["--version"])],
    "model_serving": [("ollama", ["--version"]), ("llama-server", ["--version"]),
                      ("lms", ["version"])],
    "media": [("ffmpeg", ["-version"]), ("ffprobe", ["-version"]), ("sox", ["--version"]),
              ("magick", ["-version"]), ("tesseract", ["--version"]),
              ("espeak-ng", ["--version"])],
    "science_and_maths": [("lean", ["--version"]), ("lake", ["--version"]),
                          ("z3", ["--version"]), ("julia", ["--version"]),
                          ("Rscript", ["--version"]), ("octave", ["--version"]),
                          ("maxima", ["--version"]), ("gnuplot", ["--version"]),
                          ("pandoc", ["--version"]), ("pdflatex", ["--version"])],
    "languages_and_build": [("node", ["--version"]), ("npm", ["--version"]),
                            ("rustc", ["--version"]), ("cargo", ["--version"]),
                            ("gcc", ["--version"]), ("clang", ["--version"]),
                            ("cmake", ["--version"]), ("go", ["version"]),
                            ("java", ["-version"])],
    "agent_tooling": [("claude", ["--version"]), ("codex", ["--version"])],
    "gpu": [("nvidia-smi", ["--version"])],
}

# Distribution names looked up in the base Python interpreter.
PYTHON_PACKAGES = [
    "numpy", "scipy", "sympy", "pandas", "matplotlib", "scikit-learn", "networkx", "z3-solver",
    "torch", "torchaudio", "torchvision", "tensorflow", "jax", "onnxruntime",
    "transformers", "diffusers", "accelerate", "llama_cpp_python", "ollama", "openai",
    "anthropic", "mcp", "langchain", "faster-whisper", "openai-whisper", "demucs", "librosa",
    "soundfile", "pillow", "opencv-python", "playwright", "pyautogui", "jupyter",
    "fastapi", "uvicorn", "pydantic", "jsonschema", "psutil", "pytest", "ruff",
]

OLLAMA_URL = "http://127.0.0.1:11434"


def _run(command: list[str], timeout: int = PROBE_TIMEOUT_S) -> tuple[int | None, bytes]:
    """Run a probe. Returns (None, b"") if it cannot start or does not finish in time."""
    try:
        done = subprocess.run(  # noqa: S603 - fixed argument vectors, no shell
            command, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, b""
    return done.returncode, done.stdout or done.stderr


def _first_line(raw: bytes) -> str | None:
    for line in raw.decode("utf-8", errors="replace").splitlines():
        if line.strip():
            return line.strip()[:160]
    return None


def _probe_tools() -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for group, tools in TOOLS.items():
        result[group] = {}
        for name, args in tools:
            path = shutil.which(name)
            entry: dict[str, Any] = {"found": path is not None}
            if path:
                entry["path"] = path
                code, out = _run([path, *args])
                entry["version"] = _first_line(out) if code == 0 else None
            result[group][name] = entry
    return result


def _memory() -> dict[str, float | None]:
    total = available = None
    if sys.platform == "win32":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            total, available = status.ullTotalPhys, status.ullAvailPhys
    elif Path("/proc/meminfo").exists():
        lines = Path("/proc/meminfo").read_text().splitlines()
        info = dict(line.split(":", 1) for line in lines if ":" in line)
        total = int(info["MemTotal"].split()[0]) * 1024
        available = int(info.get("MemAvailable", "0 kB").split()[0]) * 1024
    else:
        code, out = _run(["sysctl", "-n", "hw.memsize"])
        if code == 0:
            total = int(out.strip())
    to_gb = lambda value: round(value / 2**30, 1) if value else None  # noqa: E731
    return {"total_gb": to_gb(total), "available_gb": to_gb(available)}


def _windows_details() -> dict[str, Any]:
    """CPU cores, display adapters and virtualisation features from CIM (one PowerShell call)."""
    script = (
        "$c=Get-CimInstance Win32_Processor|Select-Object -First 1;"
        "$s=Get-CimInstance Win32_ComputerSystem;"
        "$f=@(Get-CimInstance Win32_OptionalFeature -Filter 'InstallState=1'|"
        "Where-Object{$_.Name -match 'Hyper-V|VirtualMachinePlatform|Subsystem-Linux|Containers'}|"
        "ForEach-Object{$_.Name});"
        "@{cpu=$c.Name.Trim();cores=$c.NumberOfCores;threads=$c.NumberOfLogicalProcessors;"
        "gpus=@(Get-CimInstance Win32_VideoController|ForEach-Object{$_.Name});"
        "hypervisor=$s.HypervisorPresent;features=$f}|ConvertTo-Json -Compress"
    )
    code, out = _run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], 40)
    if code != 0:
        return {}
    try:
        return json.loads(out.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}


def _cpu(windows: dict[str, Any]) -> dict[str, Any]:
    name = windows.get("cpu")
    if not name and Path("/proc/cpuinfo").exists():
        match = re.search(r"model name\s*:\s*(.+)", Path("/proc/cpuinfo").read_text())
        name = match.group(1).strip() if match else None
    return {
        "name": name or platform.processor() or None,
        "architecture": platform.machine(),
        "physical_cores": windows.get("cores"),
        "logical_cores": windows.get("threads") or os.cpu_count(),
    }


def _gpus(windows: dict[str, Any]) -> list[dict[str, Any]]:
    gpus: list[dict[str, Any]] = []
    nvidia = shutil.which("nvidia-smi")
    if nvidia:
        code, out = _run([
            nvidia, "--query-gpu=name,memory.total,memory.used,driver_version",
            "--format=csv,noheader,nounits",
        ])
        if code == 0:
            for line in out.decode("utf-8", errors="replace").splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 4:
                    gpus.append({
                        "name": parts[0], "vendor": "nvidia", "vram_total_mb": int(parts[1]),
                        "vram_used_mb": int(parts[2]), "driver": parts[3],
                    })
    known = {g["name"] for g in gpus}
    for name in windows.get("gpus") or []:
        if name not in known:
            # Windows reports adapter memory in a 32-bit field, so it is not trustworthy.
            gpus.append({"name": name, "vendor": "other", "vram_total_mb": None})
    return gpus


def _disk() -> dict[str, float]:
    usage = shutil.disk_usage(Path.cwd().anchor or "/")
    return {"total_gb": round(usage.total / 2**30), "free_gb": round(usage.free / 2**30)}


def _isolation(tools: dict[str, Any], windows: dict[str, Any]) -> dict[str, Any]:
    wsl: dict[str, Any] = {"found": False, "working": False}
    path = shutil.which("wsl") if sys.platform == "win32" else None
    if path:
        code, out = _run([path, "--status"], 20)
        text = out.decode("utf-16-le", errors="replace") if b"\x00" in out else out.decode(
            "utf-8", errors="replace"
        )
        wsl = {"found": True, "working": code == 0, "status": (_first_line(text.encode()) or "")}
    return {
        "docker": tools["isolation"]["docker"]["found"],
        "podman": tools["isolation"]["podman"]["found"],
        "wsl": wsl,
        "hypervisor_present": windows.get("hypervisor"),
        "windows_features": windows.get("features") or [],
    }


def _ollama() -> dict[str, Any]:
    info: dict[str, Any] = {"installed": shutil.which("ollama") is not None, "running": False,
                            "models": []}
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/version", timeout=5) as response:  # noqa: S310
            info["version"] = json.load(response).get("version")
            info["running"] = True
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=10) as response:  # noqa: S310
            for model in json.load(response).get("models", []):
                details = model.get("details", {})
                info["models"].append({
                    "name": model.get("name"),
                    "size_mb": round(model.get("size", 0) / 2**20),
                    "parameter_size": details.get("parameter_size"),
                    "quantization": details.get("quantization_level"),
                })
    except (urllib.error.URLError, OSError, ValueError):
        pass
    return info


def _model_stores() -> dict[str, Any]:
    home = Path.home()
    hub = Path(os.environ.get("HF_HOME", home / ".cache" / "huggingface")) / "hub"
    repos = sorted(p.name.removeprefix("models--").replace("--", "/")
                   for p in hub.glob("models--*")) if hub.is_dir() else []
    return {
        "huggingface_cache": {"present": hub.is_dir(), "path": str(hub), "repos": repos},
        "lm_studio": {"present": (home / ".lmstudio").is_dir()
                      or (home / ".cache" / "lm-studio").is_dir()},
    }


def _base_python_packages() -> dict[str, Any]:
    """Packages in the base interpreter, not this project's virtual environment."""
    base = getattr(sys, "_base_executable", None) or sys.executable
    script = (
        "import json,importlib.metadata as m\n"
        f"names={PYTHON_PACKAGES!r}\nout={{}}\n"
        "for n in names:\n"
        "    try: out[n]=m.version(n)\n"
        "    except m.PackageNotFoundError: out[n]=None\n"
        "print(json.dumps(out))"
    )
    code, out = _run([base, "-c", script], 60)
    packages = json.loads(out) if code == 0 else {}
    return {"interpreter": base, "version": platform.python_version(), "packages": packages}


def collect() -> dict[str, Any]:
    """Run every probe and return the raw (unsanitised) report."""
    windows = _windows_details() if sys.platform == "win32" else {}
    tools = _probe_tools()
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "edition": platform.win32_edition() if sys.platform == "win32" else None,
        },
        "cpu": _cpu(windows),
        "memory": _memory(),
        "gpus": _gpus(windows),
        "disk": _disk(),
        "isolation": _isolation(tools, windows),
        "ollama": _ollama(),
        "model_stores": _model_stores(),
        "python": _base_python_packages(),
        "tools": tools,
    }


def _scrub(value: Any, needles: list[str]) -> Any:
    if isinstance(value, dict):
        return {k: _scrub(v, needles) for k, v in value.items() if k not in {"path", "interpreter"}}
    if isinstance(value, list):
        return [_scrub(v, needles) for v in value]
    if isinstance(value, str):
        for needle in needles:
            value = re.sub(re.escape(needle), "<redacted>", value, flags=re.IGNORECASE)
    return value


def sanitise(raw: dict[str, Any]) -> dict[str, Any]:
    """Drop paths and redact the user name, home directory and host name."""
    home = Path.home()
    needles = [str(home), home.as_posix(), platform.node()]
    user = os.environ.get("USERNAME") or os.environ.get("USER") or home.name
    needles += [f"\\{user}", f"/{user}"]
    clean = _scrub(raw, [n for n in needles if n and len(n) > 2])
    # Repository names in a personal model cache are a private inventory; keep the count.
    cache = clean["model_stores"]["huggingface_cache"]
    cache["repo_count"] = len(cache.pop("repos", []))
    return clean
