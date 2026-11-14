from __future__ import annotations

import copy
from pathlib import Path

import pytest

from open_lab_builder.contracts import CONTRACT_NAMES, load_documents
from open_lab_builder.health import example_files
from open_lab_builder.paths import repo_root

ROOT = repo_root()
assert ROOT is not None, "tests must run from a source checkout"

EXAMPLES: dict[str, list[Path]] = example_files(ROOT)


def first_example(contract: str) -> dict:
    """A fresh copy of the first example document for a contract."""
    return copy.deepcopy(load_documents(EXAMPLES[contract][0])[0])


@pytest.fixture(params=CONTRACT_NAMES)
def contract(request) -> str:
    return request.param


@pytest.fixture
def capability() -> dict:
    path = ROOT / "examples" / "v1" / "capability" / "text-stats.json"
    return copy.deepcopy(load_documents(path)[0])


@pytest.fixture
def events() -> list[dict]:
    path = ROOT / "examples" / "v1" / "observation-event" / "run-excerpt.jsonl"
    return copy.deepcopy(load_documents(path))
