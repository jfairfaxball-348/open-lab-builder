from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from open_lab_builder.contracts import (
    CONTRACT_NAMES,
    RESEARCH_CONTRACT_NAMES,
    load_schema,
    validate_document,
)
from open_lab_builder.worlds.release import BUNDLED_SCHEMAS

ROOT = Path(__file__).resolve().parents[1]


def example(name):
    path = next((ROOT / "examples/v1" / name).glob("*.json"))
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", RESEARCH_CONTRACT_NAMES)
def test_research_examples_versions_and_closed_fields(name):
    document = example(name)
    assert validate_document(document) == []
    changed = copy.deepcopy(document)
    changed["schema_version"] = "1.0.7"
    assert validate_document(changed) == []
    changed["schema_version"] = "1.1.0"
    assert validate_document(changed)
    changed = copy.deepcopy(document)
    changed["surprise"] = True
    assert validate_document(changed)
    for required in load_schema(name)["required"]:
        changed = copy.deepcopy(document)
        del changed[required]
        assert validate_document(changed)


def test_research_contracts_do_not_change_world_packaging():
    assert len(CONTRACT_NAMES) == 7
    assert not set(RESEARCH_CONTRACT_NAMES) & set(BUNDLED_SCHEMAS)


@pytest.mark.parametrize("path", ["../secret", "/root/file", "a/../b", "C:/file", "a\\b"])
def test_study_paths_are_relative_and_confined(path):
    doc = example("study-manifest")
    doc["cells"][0]["configuration"]["path"] = path
    assert validate_document(doc)


def test_prospective_label_needs_commit_and_outcomes_do_not_fabricate_archives():
    doc = example("study-manifest")
    doc["registration"]["kind"] = "prospective"
    assert validate_document(doc)
    doc["registration"]["commit"] = "a" * 40
    assert validate_document(doc) == []
    doc["cells"][0]["outcome"]["status"] = "recorded"
    assert validate_document(doc)
    doc["cells"][0]["outcome"]["archive"] = {"experiment_id": "example", "run_id": "run-example"}
    assert validate_document(doc) == []
    doc["cells"][0]["outcome"]["status"] = "not_started"
    assert validate_document(doc)
