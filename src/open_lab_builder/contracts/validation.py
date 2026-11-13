"""Load the contract schemas and validate documents against them.

A document names its contract in ``schema`` (``"open-lab/<name>"``) and the
contract version it was written against in ``schema_version``. The major
version selects the ``schemas/v<major>/`` directory. See
``docs/architecture/CONTRACTS.md`` for the compatibility rules.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from ..paths import schemas_dir

SCHEMA_PREFIX = "open-lab/"

# The seven public contracts required by the architecture. ``development-state``
# is an internal project file and ``common`` only holds shared definitions.
CONTRACT_NAMES = (
    "world-release",
    "capability",
    "model-provider",
    "experiment-config",
    "observation-event",
    "artifact-metadata",
    "checkpoint-metadata",
)


@dataclass(frozen=True)
class Issue:
    """One validation problem. ``location`` is a JSON-pointer-like path into the document."""

    location: str
    message: str

    def __str__(self) -> str:
        return f"{self.location or '<root>'}: {self.message}"


def _major_dir(major: int) -> Path:
    return schemas_dir() / f"v{major}"


def available_majors() -> list[int]:
    return sorted(
        int(p.name[1:]) for p in schemas_dir().iterdir() if p.is_dir() and p.name[1:].isdigit()
    )


@cache
def _load_major(major: int) -> tuple[dict[str, dict[str, Any]], Registry]:
    directory = _major_dir(major)
    if not directory.is_dir():
        raise FileNotFoundError(f"No schemas for major version {major}")
    schemas: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for path in sorted(directory.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        name = path.name.removesuffix(".schema.json")
        schemas[name] = schema
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return schemas, registry


def schema_names(major: int = 1) -> list[str]:
    """Names of every schema file for a major version, including internal ones."""
    return sorted(_load_major(major)[0])


def load_schema(name: str, major: int = 1) -> dict[str, Any]:
    schemas, _ = _load_major(major)
    if name not in schemas:
        raise KeyError(f"Unknown contract '{name}' for major version {major}")
    return schemas[name]


def _validator(name: str, major: int) -> Draft202012Validator:
    schemas, registry = _load_major(major)
    return Draft202012Validator(schemas[name], registry=registry)


def _pointer(parts: Any) -> str:
    return "".join(f"/{p}" for p in parts)


def _version_tuple(text: str) -> tuple[int, int, int]:
    major, minor, patch = text.split("-")[0].split(".")
    return int(major), int(minor), int(patch)


def validate_document(document: Any) -> list[Issue]:
    """Validate one document. An empty list means the document is valid."""
    if not isinstance(document, dict):
        return [Issue("", "document must be a JSON object")]
    schema_field = document.get("schema")
    if not isinstance(schema_field, str) or not schema_field.startswith(SCHEMA_PREFIX):
        return [Issue("/schema", f"must be a string starting with '{SCHEMA_PREFIX}'")]
    name = schema_field.removeprefix(SCHEMA_PREFIX)
    version = document.get("schema_version")
    try:
        doc_version = _version_tuple(version)
    except (AttributeError, ValueError):
        return [Issue("/schema_version", "must be a MAJOR.MINOR.PATCH string")]
    major = doc_version[0]
    if major not in available_majors():
        return [Issue("/schema_version", f"unsupported major version {major}")]
    if name not in _load_major(major)[0] or name == "common":
        return [Issue("/schema", f"unknown contract '{name}' for major version {major}")]

    schema = load_schema(name, major)
    issues = [
        Issue(_pointer(error.absolute_path), error.message)
        for error in sorted(
            _validator(name, major).iter_errors(document), key=lambda e: list(e.absolute_path)
        )
    ]
    # A document written against a newer minor version may use fields this
    # schema does not know. Refuse rather than silently mis-read it.
    if doc_version[:2] > _version_tuple(schema["x-schema-version"])[:2]:
        issues.append(
            Issue(
                "/schema_version",
                f"document version {version} is newer than the available "
                f"schema {schema['x-schema-version']}",
            )
        )
    if not issues and name == "capability":
        issues.extend(_capability_semantics(document))
    return issues


def _capability_semantics(doc: dict[str, Any]) -> list[Issue]:
    """Checks JSON Schema cannot express: the manifest must be consistent with itself."""
    issues: list[Issue] = []
    validators: dict[str, Draft202012Validator] = {}
    for key in ("input_schema", "output_schema"):
        try:
            Draft202012Validator.check_schema(doc[key])
            validators[key] = Draft202012Validator(doc[key])
        except SchemaError as error:
            issues.append(Issue(f"/{key}", f"not a valid JSON Schema: {error.message}"))

    demo_ids: set[str] = set()
    for index, demo in enumerate(doc["demonstrations"]):
        base = f"/demonstrations/{index}"
        if demo["id"] in demo_ids:
            issues.append(Issue(f"{base}/id", f"duplicate demonstration id '{demo['id']}'"))
        demo_ids.add(demo["id"])
        if "input_schema" in validators:
            for error in validators["input_schema"].iter_errors(demo["input"]):
                issues.append(Issue(f"{base}/input", f"violates input_schema: {error.message}"))
        if "expected_output" in demo and "output_schema" in validators:
            for error in validators["output_schema"].iter_errors(demo["expected_output"]):
                issues.append(
                    Issue(f"{base}/expected_output", f"violates output_schema: {error.message}")
                )
        if demo.get("deterministic", True) and "expected_output" not in demo:
            issues.append(
                Issue(base, "deterministic demonstration must state its expected_output")
            )

    for index, demo_id in enumerate(doc["self_test"]["demonstrations"]):
        if demo_id not in demo_ids:
            issues.append(
                Issue(f"/self_test/demonstrations/{index}", f"no demonstration '{demo_id}'")
            )
    return issues


def validate_event_stream(events: list[Any]) -> list[Issue]:
    """Validate an ordered event log: each event, plus ordering and run consistency."""
    issues: list[Issue] = []
    first: dict[str, Any] | None = None
    for index, event in enumerate(events):
        issues.extend(Issue(f"/{index}{i.location}", i.message) for i in validate_document(event))
        if not isinstance(event, dict):
            continue
        if event.get("schema") != f"{SCHEMA_PREFIX}observation-event":
            issues.append(Issue(f"/{index}/schema", "event stream may only contain events"))
        if first is None:
            first = event
        if event.get("seq") != index:
            issues.append(
                Issue(f"/{index}/seq", f"expected seq {index}, found {event.get('seq')!r}")
            )
        for key in ("experiment_id", "run_id"):
            if event.get(key) != first.get(key):
                issues.append(Issue(f"/{index}/{key}", "differs from the first event in the log"))
    return issues


def load_documents(path: Path) -> list[Any]:
    """Read a ``.json`` document or a ``.jsonl`` log into a list of documents."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return [json.loads(text)]


def validate_file(path: Path) -> list[Issue]:
    """Validate a ``.json`` document or a ``.jsonl`` event log."""
    try:
        documents = load_documents(path)
    except json.JSONDecodeError as error:
        return [Issue("", f"invalid JSON: {error}")]
    if path.suffix == ".jsonl":
        return validate_event_stream(documents)
    return validate_document(documents[0])
