"""Offline references stay cited, bounded, immutable and discoverable."""

import json
import shutil
from pathlib import Path

import pytest

from open_lab_builder.worlds.library import validate_library
from open_lab_builder.worlds.release import build_world, verify_release
from test_habitat_capabilities import call

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "worlds/habitat/library"


def test_library_has_real_licensed_text_and_csv():
    assert validate_library(LIBRARY) == []
    sources = json.loads((LIBRARY / "index.json").read_text())["sources"]
    assert {s["id"] for s in sources} == {
        "iris", "python-control-flow", "sympy-calculus", "scipy-integration"}
    for source in sources:
        assert (LIBRARY / source["path"]).stat().st_size > 4000
        assert (LIBRARY / source["notice"]).is_file()
        assert source["citation"] and source["license"] and source["revision"]


def test_search_read_pagination_and_citation(tmp_path):
    found = call("library.search", tmp_path, query="integrals", limit=10)
    assert found.ok and found.output["total_matches"] >= 1
    ids = [s["source"]["id"] for s in found.output["matches"]]
    assert "sympy-calculus" in ids
    first = call("library.read", tmp_path, source_id="sympy-calculus", line_count=12)
    assert first.ok and "calculus" in first.output["text"].lower()
    assert first.output["next_line"] == 13
    second = call("library.read", tmp_path, source_id="sympy-calculus", start_line=13,
                  line_count=12)
    assert second.ok and first.output["source"] == second.output["source"]
    dataset = call("library.read", tmp_path, source_id="iris", line_count=200)
    assert dataset.ok and len(dataset.output["text"].splitlines()) == 151
    assert dataset.output["next_line"] is None
    assert "10.24432/C56C76" in dataset.output["source"]["citation"]


@pytest.mark.parametrize("arguments", [{"source_id": "../secret"},
                                      {"source_id": "iris", "line_count": 201},
                                      {"source_id": "iris", "start_line": 0}])
def test_invalid_read_requests_are_refused(tmp_path, arguments):
    assert not call("library.read", tmp_path, **arguments).ok


def test_unknown_id_and_absent_query_are_explicit(tmp_path):
    assert not call("library.read", tmp_path, source_id="unknown").ok
    assert call("library.search", tmp_path, query="uniqueabsentword").output["matches"] == []
    assert call("library.search", tmp_path).output["total_matches"] == 4


@pytest.mark.parametrize("damage", ["hash", "path", "notice", "size", "duplicate", "extra"])
def test_bad_library_is_refused_before_packaging(tmp_path, damage):
    target = tmp_path / "library"
    shutil.copytree(LIBRARY, target)
    catalog = json.loads((target / "index.json").read_text())
    source = catalog["sources"][0]
    if damage == "hash":
        (target / source["path"]).write_text("changed")
    elif damage == "path":
        source["path"] = "../escape.txt"
    elif damage == "notice":
        (target / source["notice"]).unlink()
    elif damage == "size":
        (target / "oversized.txt").write_text("x" * (256 * 1024 + 1))
    elif damage == "duplicate":
        catalog["sources"].append(source)
    else:
        source["unsupported"] = "field"
    (target / "index.json").write_text(json.dumps(catalog))
    assert validate_library(target)


def test_assets_are_packaged_and_digest_bound(tmp_path):
    built = build_world(ROOT / "worlds/habitat", tmp_path)
    assert verify_release(built.release_dir) == []
    for path in LIBRARY.glob("*"):
        assert path.read_bytes() == (built.release_dir / "library" / path.name).read_bytes()
    (built.release_dir / "library/iris.csv").write_bytes(b"tampered")
    assert verify_release(built.release_dir)
