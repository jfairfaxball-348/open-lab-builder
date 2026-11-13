"""Contract tests: every schema is sound, every example is valid, bad documents are rejected."""

from __future__ import annotations

import pytest
from jsonschema import Draft202012Validator

from conftest import EXAMPLES, first_example
from open_lab_builder.contracts import (
    CONTRACT_NAMES,
    load_schema,
    schema_names,
    validate_document,
    validate_file,
)

ALL_EXAMPLE_FILES = [path for files in EXAMPLES.values() for path in files]


@pytest.mark.parametrize("name", schema_names(1))
def test_schema_is_valid_and_versioned(name):
    schema = load_schema(name)
    Draft202012Validator.check_schema(schema)
    assert schema["$id"] == f"urn:open-lab:schema:{name}:v1"
    assert schema["x-schema-version"].startswith("1.")
    assert schema["description"]


def test_all_seven_public_contracts_exist():
    assert len(CONTRACT_NAMES) == 7
    assert set(CONTRACT_NAMES) <= set(schema_names(1))


def test_every_contract_has_an_example(contract):
    assert EXAMPLES[contract], f"no example for {contract}"


@pytest.mark.parametrize("path", ALL_EXAMPLE_FILES, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_example_is_valid(path):
    assert [str(issue) for issue in validate_file(path)] == []


def test_every_required_field_is_enforced(contract):
    required = load_schema(contract)["required"]
    for field in required:
        document = first_example(contract)
        del document[field]
        assert validate_document(document), f"{contract}: missing '{field}' was accepted"


def test_every_property_is_documented(contract):
    """Required and optional top-level fields must carry a description or reference one."""
    schema = load_schema(contract)
    assert set(schema["required"]) <= set(schema["properties"])
    assert schema["additionalProperties"] is False


def test_unknown_top_level_field_is_rejected(contract):
    document = first_example(contract)
    document["surprise"] = True
    assert validate_document(document)


def test_extensions_object_accepts_unknown_fields(contract):
    document = first_example(contract)
    document["extensions"] = {"anything": {"goes": [1, 2, 3]}}
    assert validate_document(document) == []


@pytest.mark.parametrize(
    "version, accepted",
    [("1.0.0", True), ("1.0.7", True), ("1.1.0", False), ("2.0.0", False), ("1.0", False)],
)
def test_schema_version_compatibility(contract, version, accepted):
    document = first_example(contract)
    document["schema_version"] = version
    assert (validate_document(document) == []) is accepted


@pytest.mark.parametrize("document", [None, [], "text", {}, {"schema": "other/thing"},
                                      {"schema": "open-lab/nonexistent", "schema_version": "1.0.0"},
                                      {"schema": "open-lab/common", "schema_version": "1.0.0"}])
def test_unidentifiable_documents_are_rejected(document):
    assert validate_document(document)


@pytest.mark.parametrize("path", ["/etc/passwd", "../escape", "a/../../b", "C:/Users/x", "a\\b"])
def test_paths_cannot_leave_their_root(path):
    document = first_example("artifact-metadata")
    document["workspace_path"] = path
    assert validate_document(document)


def test_allowlist_network_requires_hosts():
    document = first_example("experiment-config")
    document["permissions"]["network"] = "allowlist"
    assert validate_document(document)
    document["permissions"]["network_allowlist"] = ["example.org"]
    assert validate_document(document) == []


def test_validated_world_requires_content_digest():
    document = first_example("world-release")
    document["status"] = "validated"
    assert validate_document(document)
    document["content_digest"] = {"algorithm": "sha256", "value": "a" * 64}
    assert validate_document(document) == []


def test_unpreserved_artifact_needs_no_archive_path():
    document = first_example("artifact-metadata")
    del document["archive_path"]
    assert validate_document(document)
    document["preserved"] = False
    assert validate_document(document) == []
