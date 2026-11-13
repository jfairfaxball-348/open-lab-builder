"""Project health check: is the repository in a coherent, committable state?

Each check returns a list of problems; an empty list means it passed. The
checks need a source checkout because they inspect documentation and examples.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .contracts import CONTRACT_NAMES, load_schema, schema_names, validate_document, validate_file
from .paths import repo_root

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/CONTRACTS.md",
    "docs/architecture/OBSERVATION.md",
    "docs/architecture/SAFETY_AND_ISOLATION.md",
    "docs/decisions/README.md",
    "docs/environment/LOCAL_ENVIRONMENT.md",
    "docs/roadmap/ROADMAP.md",
    "docs/roadmap/state.json",
    "docs/development/DEVELOPMENT.md",
]

STATE_PATH = "docs/roadmap/state.json"
ROADMAP_PATH = "docs/roadmap/ROADMAP.md"


@dataclass
class CheckResult:
    name: str
    problems: list[str] = field(default_factory=list)
    skipped: str | None = None

    @property
    def ok(self) -> bool:
        return not self.problems


def example_files(root: Path) -> dict[str, list[Path]]:
    """Example documents by contract name: ``examples/v1/<contract>/*.json[l]``."""
    base = root / "examples" / "v1"
    return {
        name: sorted(p for p in (base / name).glob("*.json*") if p.suffix in {".json", ".jsonl"})
        for name in CONTRACT_NAMES
    }


def check_schemas(root: Path) -> list[str]:
    problems = []
    names = schema_names(1)
    for name in (*CONTRACT_NAMES, "common", "development-state"):
        if name not in names:
            problems.append(f"schemas/v1/{name}.schema.json is missing")
    for name in names:
        schema = load_schema(name)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as error:
            problems.append(f"{name}: not a valid JSON Schema ({error.message})")
        if schema.get("$id") != f"urn:open-lab:schema:{name}:v1":
            problems.append(f"{name}: unexpected $id {schema.get('$id')!r}")
        if not re.fullmatch(r"1\.\d+\.\d+", schema.get("x-schema-version", "")):
            problems.append(f"{name}: x-schema-version must be a 1.x.y version")
        for key in ("title", "description"):
            if not schema.get(key):
                problems.append(f"{name}: missing {key}")
    return problems


def check_examples(root: Path) -> list[str]:
    problems = []
    for name, files in example_files(root).items():
        if not files:
            problems.append(f"no example for contract '{name}'")
        for path in files:
            for issue in validate_file(path):
                problems.append(f"{path.relative_to(root).as_posix()}: {issue}")
    return problems


def check_required_files(root: Path) -> list[str]:
    return [f"{path} is missing" for path in REQUIRED_FILES if not (root / path).is_file()]


def roadmap_milestones(root: Path) -> list[str]:
    text = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    return re.findall(r"^### (S\d{3}[a-z]?) ", text, flags=re.MULTILINE)


def check_state(root: Path) -> list[str]:
    path = root / STATE_PATH
    if not path.is_file() or not (root / ROADMAP_PATH).is_file():
        return ["state or roadmap file missing"]
    state = json.loads(path.read_text(encoding="utf-8"))
    problems = [f"{STATE_PATH}: {issue}" for issue in validate_document(state)]
    if problems:
        return problems
    milestones = roadmap_milestones(root)
    done = [m["id"] for m in state["completed_milestones"]]
    for milestone in (*done, state["next_milestone"]["id"]):
        if milestone not in milestones:
            problems.append(f"{STATE_PATH}: milestone {milestone} is not defined in {ROADMAP_PATH}")
    if state["next_milestone"]["id"] in done:
        problems.append(f"{STATE_PATH}: next milestone is already marked complete")
    if state["last_session"] not in done:
        problems.append(f"{STATE_PATH}: last_session is not among the completed milestones")
    return problems


def _git(root: Path, *args: str) -> str | None:
    try:
        done = subprocess.run(  # noqa: S603
            ["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


def _committable_files(root: Path) -> list[Path] | None:
    """Tracked files plus untracked files that are not ignored."""
    listing = _git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    if listing is None:
        return None
    return [root / line for line in listing.splitlines() if (root / line).is_file()]


def check_privacy(root: Path) -> list[str]:
    """Nothing committable may contain the local home directory, user name path or host name."""
    files = _committable_files(root)
    if files is None:
        raise RuntimeError("git is unavailable")
    problems = []
    if _git(root, "check-ignore", "-q", ".local/probe") is None:
        problems.append(".local/ is not ignored by Git")

    home = Path.home()
    user = os.environ.get("USERNAME") or os.environ.get("USER") or home.name
    needles = {str(home).lower(), home.as_posix().lower(),
               f"users\\{user}".lower(), f"users/{user}".lower(), f"home/{user}".lower()}
    host = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or ""
    if len(host) > 3:
        needles.add(host.lower())
    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in {".gguf", ".safetensors", ".onnx", ".pt", ".bin"}:
            problems.append(f"{relative}: model weights must not be committed")
            continue
        if path.stat().st_size > 2_000_000:
            problems.append(f"{relative}: unexpectedly large file")
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            continue
        if any(needle in text for needle in needles):
            problems.append(f"{relative}: contains a local path, user name or host name")
    return problems


CHECKS: list[tuple[str, Callable[[Path], list[str]]]] = [
    ("Contract schemas are well formed", check_schemas),
    ("Every contract has valid examples", check_examples),
    ("Required documents exist", check_required_files),
    ("Development state matches the roadmap", check_state),
    ("No private or oversized content is committable", check_privacy),
]


def run_checks() -> list[CheckResult]:
    root = repo_root()
    if root is None:
        raise RuntimeError("The health check must be run from a source checkout.")
    results = []
    for name, check in CHECKS:
        try:
            results.append(CheckResult(name, check(root)))
        except RuntimeError as error:
            results.append(CheckResult(name, skipped=str(error)))
    return results
