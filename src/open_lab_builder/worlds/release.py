"""Build a world source tree into an immutable release, and verify a release.

Release layout and the digest algorithm are specified in
``docs/architecture/CONTRACTS.md`` ("World release"). The functions here are
the reference implementation of that text.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .. import __version__
from ..capabilities import entrypoint_file, run_self_test
from ..capabilities.registry import INDEX_PATH, build_index, documentation
from ..contracts import CONTRACT_NAMES, load_schema, validate_document
from ..paths import repo_root, schemas_dir

MANIFEST_NAME = "world-release.json"
SOURCE_NAME = "world.json"
# Shared definitions are bundled too: the contract schemas refer to them.
BUNDLED_SCHEMAS = (*CONTRACT_NAMES, "common")
# Manifest fields that describe the build, not the world. Two builds of the
# same source differ in these and must still have the same digest.
VOLATILE_FIELDS = ("created_at", "builder", "content_digest")
SOURCE_REQUIRED = (
    "world_id", "version", "name", "description",
    "environment", "default_limits", "default_permissions",
)
SOURCE_OPTIONAL = ("notes",)


class BuildError(Exception):
    """The source cannot be turned into a release. ``problems`` lists every reason found."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass
class Capability:
    directory: Path
    manifest: dict[str, Any]


@dataclass
class WorldSource:
    root: Path
    description: dict[str, Any]
    capabilities: list[Capability] = field(default_factory=list)
    models: list[tuple[Path, dict[str, Any]]] = field(default_factory=list)


@dataclass
class BuildResult:
    release_dir: Path
    manifest: dict[str, Any]
    # True when an identical release was already there and was left untouched.
    reused: bool = False


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_build_residue(relative: Path) -> bool:
    return "__pycache__" in relative.parts or relative.suffix in {".pyc", ".pyo"}


def _files_under(directory: Path) -> list[Path]:
    """Every file below ``directory`` as a relative path. Symbolic links are refused."""
    found = []
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise BuildError([f"{path.name}: symbolic links are not allowed in a world"])
        if path.is_file():
            found.append(path.relative_to(directory))
    return found


def digest_files(release_dir: Path) -> dict[str, str]:
    """Forward-slash relative path to SHA-256, for every file except the manifest."""
    return {
        relative.as_posix(): file_sha256(release_dir / relative)
        for relative in _files_under(release_dir)
        if relative.as_posix() != MANIFEST_NAME
    }


def content_digest(file_digests: dict[str, str], manifest: dict[str, Any]) -> str:
    """The release digest: every bundled file, then the manifest's stable fields."""
    stable = {key: value for key, value in manifest.items() if key not in VOLATILE_FIELDS}
    canonical = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    lines = [
        f"{file_digests[path]}  {path}\n"
        for path in sorted(file_digests, key=lambda p: p.encode("utf-8"))
    ]
    lines.append(f"{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}  {MANIFEST_NAME}\n")
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def _read_json(path: Path, problems: list[str], label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        problems.append(f"{label}: cannot be read as JSON ({type(error).__name__})")
        return None


def load_source(source: Path) -> WorldSource:
    """Read and validate a world source tree without running anything."""
    problems: list[str] = []
    description = _read_json(source / SOURCE_NAME, problems, SOURCE_NAME)
    if not isinstance(description, dict):
        raise BuildError(problems or [f"{SOURCE_NAME}: must be a JSON object"])
    for key in SOURCE_REQUIRED:
        if key not in description:
            problems.append(f"{SOURCE_NAME}: missing '{key}'")
    for key in description:
        if key not in (*SOURCE_REQUIRED, *SOURCE_OPTIONAL):
            problems.append(f"{SOURCE_NAME}: unknown field '{key}'")
    world = WorldSource(source, description)
    tier = description.get("environment", {}).get("isolation", {}).get("minimum_tier")

    capability_root = source / "capabilities"
    directories = sorted(p for p in capability_root.iterdir() if p.is_dir()) \
        if capability_root.is_dir() else []
    for directory in directories:
        label = f"capabilities/{directory.name}/capability.json"
        manifest = _read_json(directory / "capability.json", problems, label)
        if manifest is None:
            continue
        issues = validate_document(manifest)
        if not issues and manifest.get("schema") != "open-lab/capability":
            issues = ["not a capability manifest"]
        if issues:
            problems.extend(f"{label}: {issue}" for issue in issues)
            continue
        if manifest["id"] != directory.name:
            problems.append(f"{label}: id '{manifest['id']}' must equal the directory name")
        if manifest["provenance"]["origin"] != "builder":
            problems.append(f"{label}: only builder-made capabilities ship in a world")
        # Spawning processes on the agent's behalf is only safe inside a container.
        if manifest["permissions"].get("subprocess") and tier != "container":
            problems.append(f"{label}: 'subprocess' permission needs the container isolation tier")
        invocation = manifest["invocation"]
        if invocation["interface"] == "python" and not entrypoint_file(
            directory, invocation["entrypoint"]
        ).is_file():
            problems.append(f"{label}: entrypoint '{invocation['entrypoint']}' has no file")
        world.capabilities.append(Capability(directory, manifest))

    model_root = source / "models"
    for path in sorted(model_root.glob("*.json")) if model_root.is_dir() else []:
        label = f"models/{path.name}"
        manifest = _read_json(path, problems, label)
        if manifest is None:
            continue
        issues = validate_document(manifest)
        if not issues and manifest.get("schema") != "open-lab/model-provider":
            issues = ["not a model provider manifest"]
        problems.extend(f"{label}: {issue}" for issue in issues)
        if not issues:
            world.models.append((path, manifest))

    if problems:
        raise BuildError(problems)
    return world


def _builder_provenance() -> dict[str, str]:
    """Builder version, plus the commit when the checkout has no uncommitted changes."""
    provenance = {"version": __version__}
    root = repo_root()
    if root is None:
        return provenance
    try:
        results = [
            subprocess.run(  # noqa: S603
                ["git", "-C", str(root), *args],
                capture_output=True, text=True, timeout=30, check=False,
            )
            for args in (("status", "--porcelain"), ("rev-parse", "HEAD"))
        ]
    except (OSError, subprocess.TimeoutExpired):
        return provenance
    status, head = results
    # A commit id on a build from modified files would be a false statement.
    if status.returncode == 0 and head.returncode == 0 and not status.stdout.strip():
        provenance["git_commit"] = head.stdout.strip()
    return provenance


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _stage(world: WorldSource, staging: Path) -> None:
    for name in BUNDLED_SCHEMAS:
        file_name = f"{name}.schema.json"
        _copy(schemas_dir() / "v1" / file_name, staging / "contracts" / "v1" / file_name)
    for capability in world.capabilities:
        for relative in _files_under(capability.directory):
            if not _is_build_residue(relative):
                _copy(
                    capability.directory / relative,
                    staging / "capabilities" / capability.directory.name / relative,
                )
    for path, _ in world.models:
        _copy(path, staging / "models" / path.name)
    registry = staging / "registry"
    (registry / "docs").mkdir(parents=True)
    (staging / INDEX_PATH).write_text(
        json.dumps(build_index([c.manifest for c in world.capabilities]),
                   indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    for capability in world.capabilities:
        (registry / "docs" / f"{capability.manifest['id']}.txt").write_text(
            documentation(capability.manifest), encoding="utf-8", newline="\n",
        )


def _manifest(world: WorldSource, digests: dict[str, str], now: datetime) -> dict[str, Any]:
    description = world.description
    capability_paths = {
        c.manifest["id"]: f"capabilities/{c.directory.name}/capability.json"
        for c in world.capabilities
    }
    manifest: dict[str, Any] = {
        "schema": "open-lab/world-release",
        "schema_version": load_schema("world-release")["x-schema-version"],
        "world_id": description["world_id"],
        "version": description["version"],
        "name": description["name"],
        "description": description["description"],
        "created_at": now.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "validated",
        "builder": _builder_provenance(),
        "contracts": {name: load_schema(name)["x-schema-version"] for name in BUNDLED_SCHEMAS},
        "capabilities": [
            {
                "id": c.manifest["id"],
                "version": c.manifest["version"],
                "manifest_path": capability_paths[c.manifest["id"]],
                "sha256": digests[capability_paths[c.manifest["id"]]],
            }
            for c in sorted(world.capabilities, key=lambda c: c.manifest["id"])
        ],
        "model_manifests": [
            {
                "provider_id": model["provider"]["id"],
                "manifest_path": f"models/{path.name}",
                "sha256": digests[f"models/{path.name}"],
            }
            for path, model in world.models
        ],
        "environment": copy.deepcopy(description["environment"]),
        "default_limits": copy.deepcopy(description["default_limits"]),
        "default_permissions": copy.deepcopy(description["default_permissions"]),
    }
    if "notes" in description:
        manifest["notes"] = description["notes"]
    # Informational: lets `verify` name the file that changed. The
    # content_digest is what binds the release.
    manifest["extensions"] = {
        "files": [{"path": path, "sha256": digests[path]} for path in sorted(digests)]
    }
    manifest["content_digest"] = {
        "algorithm": "sha256",
        "value": content_digest(digests, manifest),
    }
    return manifest


def _discard(staging: Path) -> None:
    shutil.rmtree(staging, ignore_errors=True)
    try:
        staging.parent.rmdir()  # only succeeds when this build created it and it is empty
    except OSError:
        pass


def build_world(source: Path, out: Path, *, now: datetime | None = None) -> BuildResult:
    """Build ``source`` into ``<out>/<world_id>/<version>/``.

    The release directory appears only if every check and self-test passed.
    Raises ``BuildError`` otherwise.
    """
    world = load_source(source)
    world_id, version = world.description["world_id"], world.description["version"]
    final = out / world_id / version
    staging = out / world_id / f".building-{version}-{os.getpid()}"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    try:
        _stage(world, staging)
        before = digest_files(staging)

        # Test the staged copies: what is released is exactly what was run.
        problems: list[str] = []
        for capability in world.capabilities:
            staged = staging / "capabilities" / capability.directory.name
            problems.extend(run_self_test(capability.manifest, staged))
        if problems:
            raise BuildError(problems)
        if digest_files(staging) != before:
            raise BuildError(["a self-test changed files inside the release"])

        manifest = _manifest(world, before, now or datetime.now(UTC))
        issues = validate_document(manifest)
        if issues:
            raise BuildError([f"{MANIFEST_NAME}: {issue}" for issue in issues])
        (staging / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )

        if final.exists():
            existing = json.loads((final / MANIFEST_NAME).read_text(encoding="utf-8"))
            if existing.get("content_digest") == manifest["content_digest"]:
                _discard(staging)
                return BuildResult(final, existing, reused=True)
            raise BuildError([
                f"{world_id} {version} already exists with different content. "
                "A release is immutable: change the version in world.json."
            ])
        os.replace(staging, final)
    except BaseException:
        _discard(staging)
        raise
    return BuildResult(final, manifest)


def verify_release(release_dir: Path, *, self_tests: bool = False) -> list[str]:
    """Check a release against its own manifest and bundled contracts.

    Returns the problems found; an empty list means the release is intact.
    """
    problems: list[str] = []
    manifest = _read_json(release_dir / MANIFEST_NAME, problems, MANIFEST_NAME)
    if not isinstance(manifest, dict):
        return problems or [f"{MANIFEST_NAME}: must be a JSON object"]

    # The release is judged by the contracts it carries, as the Simulation will.
    bundled = release_dir / "contracts"
    if not (bundled / "v1").is_dir():
        return [f"{MANIFEST_NAME}: the release bundles no contracts"]
    try:
        issues = validate_document(manifest, bundled)
    except (OSError, KeyError, ValueError) as error:
        return [f"contracts: bundled schemas cannot be loaded ({type(error).__name__})"]
    if issues or manifest.get("schema") != "open-lab/world-release":
        return [f"{MANIFEST_NAME}: {issue}" for issue in issues] or [
            f"{MANIFEST_NAME}: not a world release manifest"
        ]
    if manifest["status"] == "draft":
        return [f"{MANIFEST_NAME}: a draft release cannot be verified"]

    try:
        actual = digest_files(release_dir)
    except BuildError as error:
        return error.problems

    listed = {
        entry["path"]: entry["sha256"]
        for entry in manifest.get("extensions", {}).get("files", [])
        if isinstance(entry, dict) and "path" in entry and "sha256" in entry
    }
    if listed:
        for path in sorted(listed.keys() - actual.keys()):
            problems.append(f"{path}: file is missing")
        for path in sorted(actual.keys() - listed.keys()):
            problems.append(f"{path}: file is not part of the release")
        for path in sorted(listed.keys() & actual.keys()):
            if listed[path] != actual[path]:
                problems.append(f"{path}: content has changed")
    if content_digest(actual, manifest) != manifest["content_digest"]["value"]:
        problems.append("content_digest does not match the release content")

    for name, version in manifest["contracts"].items():
        path = bundled / "v1" / f"{name}.schema.json"
        schema = _read_json(path, problems, f"contracts/v1/{path.name}") if path.is_file() else None
        if not isinstance(schema, dict) or schema.get("x-schema-version") != version:
            problems.append(f"contracts: '{name}' {version} is listed but not bundled")

    capabilities = []
    for entry, kind, key in (
        *((e, "capability", "id") for e in manifest["capabilities"]),
        *((e, "model-provider", "provider_id") for e in manifest["model_manifests"]),
    ):
        path = entry["manifest_path"]
        if actual.get(path) != entry["sha256"]:
            problems.append(f"{path}: digest differs from the manifest entry")
            continue
        document = _read_json(release_dir / path, problems, path)
        if document is None:
            continue
        issues = validate_document(document, bundled)
        problems.extend(f"{path}: {issue}" for issue in issues)
        if issues:
            continue
        identity = document.get("id") or document.get("provider", {}).get("id")
        if document["schema"] != f"open-lab/{kind}" or identity != entry[key]:
            problems.append(f"{path}: is not the {kind} '{entry[key]}'")
        elif kind == "capability":
            capabilities.append(Capability((release_dir / path).parent, document))

    if self_tests and not problems:
        for capability in capabilities:
            problems.extend(run_self_test(capability.manifest, capability.directory))
        if digest_files(release_dir) != actual:
            problems.append("a self-test changed files inside the release")
    return problems
