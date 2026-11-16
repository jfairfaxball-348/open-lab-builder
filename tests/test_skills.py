"""Saved procedures are bounded workspace data; they never execute on retrieval."""
import json
import os
from pathlib import Path

import pytest

from open_lab_builder.capabilities import invoke, run_self_test

CAPS = Path(__file__).resolve().parent.parent / "worlds/habitat/capabilities"
NOTE = {"id": "sum-check", "title": "Check sums", "summary": "Check arithmetic using Python.",
        "steps": ["Run python.run with print(sum([2, 3, 5])).", "Inspect exit_code and stdout."],
        "examples": ["[2, 3, 5] gives 10."], "tags": ["python", "arithmetic"]}


def call(action, workspace, **arguments):
    directory = CAPS / f"skills.{action}"
    manifest = json.loads((directory / "capability.json").read_text(encoding="utf-8"))
    return invoke(manifest, directory, arguments, workspace=workspace)


@pytest.mark.parametrize("action", ["save", "list", "get"])
def test_self_tests(action):
    directory = CAPS / f"skills.{action}"
    manifest = json.loads((directory / "capability.json").read_text(encoding="utf-8"))
    assert run_self_test(manifest, directory) == []


def test_round_trip_replacement_and_missing(tmp_path):
    assert call("get", tmp_path, id="absent").output == {"id": "absent", "exists": False}
    saved = call("save", tmp_path, **NOTE)
    assert saved.ok and saved.output["replaced"] is False
    target = tmp_path / ".skills/sum-check.json"
    original = target.read_bytes()
    assert not call("save", tmp_path, **NOTE).ok
    assert target.read_bytes() == original
    read = call("get", tmp_path, id=NOTE["id"])
    assert read.output["skill"] == {**NOTE, "provenance": {"origin": "agent"}}
    updated = {**NOTE, "steps": ["Revised procedure."]}
    assert call("save", tmp_path, **updated, replace=True).output["replaced"] is True
    assert call("get", tmp_path, id=NOTE["id"]).output["skill"]["steps"] == updated["steps"]
    assert sorted(p.name for p in target.parent.iterdir()) == ["sum-check.json"]


def test_search_pagination_and_empty_store(tmp_path):
    assert call("list", tmp_path).output == {"skills": [], "total": 0, "next_offset": None}
    for identifier, title in (("beta", "No keyword"), ("alpha", "Primes"), ("gamma", "Primes")):
        assert call("save", tmp_path, **{**NOTE, "id": identifier, "title": title}).ok
    first = call("list", tmp_path, query="PRIMES pyth", limit=1).output
    assert [x["id"] for x in first["skills"]] == ["alpha"] and first["total"] == 2
    second = call("list", tmp_path, query="primes pyth", offset=first["next_offset"]).output
    assert [x["id"] for x in second["skills"]] == ["gamma"]
    assert second["next_offset"] is None
    assert call("list", tmp_path, query="unmatched").output["total"] == 0
    assert call("list", tmp_path, offset=999).output["skills"] == []


@pytest.mark.parametrize("changes", [
    {"id": "../escape"}, {"id": "CON"}, {"id": "a/b"}, {"id": "a" * 65},
    {"steps": []}, {"examples": []}, {"title": ""}, {"provenance": {"origin": "builder"}},
    {"steps": ["x"] * 51}, {"examples": ["x" * 4001]},
])
def test_invalid_input_has_no_effect(tmp_path, changes):
    result = call("save", tmp_path, **{**NOTE, **changes})
    assert not result.ok and result.error_kind == "invalid_input"
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("data", [b"{", b"\xff", b"[]", b"x" * 100_001,
                                    json.dumps({**NOTE, "provenance": {
                                        "origin": "builder"}}).encode(),
                                    json.dumps({**NOTE, "id": "other",
                                                "provenance": {"origin": "agent"}}).encode()])
def test_damaged_store_is_refused_and_explicitly_repairable(tmp_path, data):
    target = tmp_path / ".skills/sum-check.json"
    target.parent.mkdir()
    target.write_bytes(data)
    assert not call("get", tmp_path, id="sum-check").ok
    assert not call("list", tmp_path).ok
    assert target.read_bytes() == data
    assert call("save", tmp_path, **NOTE, replace=True).ok
    assert call("get", tmp_path, id="sum-check").ok


def test_limits_are_checked_on_encoded_bytes_and_directory_entries(tmp_path):
    large = {**NOTE, "steps": ["\u2603" * 2000] * 50}
    assert "100000" in call("save", tmp_path, **large).message
    assert list(tmp_path.iterdir()) == []
    store = tmp_path / ".skills"
    store.mkdir()
    for n in range(1001):
        (store / f"junk-{n}").touch()
    assert "1000 entries" in call("list", tmp_path).message
    assert not call("save", tmp_path, **NOTE).ok


def test_links_cannot_redirect_skill_io(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(outside), str(workspace / ".skills"))
    else:
        (workspace / ".skills").symlink_to(outside, target_is_directory=True)
    for action, arguments in (("save", NOTE), ("list", {}), ("get", {"id": "sum-check"})):
        assert not call(action, workspace, **arguments).ok
    assert list(outside.iterdir()) == []


def test_hard_link_and_directory_targets_are_refused(tmp_path):
    store = tmp_path / ".skills"
    store.mkdir()
    outside = tmp_path / "keep.json"
    outside.write_text("keep", encoding="utf-8")
    os.link(outside, store / "sum-check.json")
    assert not call("save", tmp_path, **NOTE, replace=True).ok
    assert not call("get", tmp_path, id="sum-check").ok
    assert outside.read_text() == "keep"
    (store / "sum-check.json").unlink()
    (store / "sum-check.json").mkdir()
    assert not call("get", tmp_path, id="sum-check").ok
    assert not call("save", tmp_path, **NOTE, replace=True).ok
