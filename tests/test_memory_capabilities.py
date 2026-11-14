"""Real SQLite memory capabilities, without models or privileged paths."""
import sqlite3

import pytest

from open_lab_builder.capabilities import invoke, run_self_test
from test_capabilities import load


def call(name, workspace, arguments):
    manifest, directory = load("memory." + name)
    return invoke(manifest, directory, arguments, workspace=workspace)


@pytest.mark.parametrize("name", ["write", "search", "list"])
def test_memory_self_tests(name):
    manifest, directory = load("memory." + name)
    assert run_self_test(manifest, directory) == []


def test_memory_updates_searches_and_lists_durable_entries(tmp_path):
    assert call("list", tmp_path, {}).output == {"entries": []}
    assert not (tmp_path / ".memory.sqlite").exists(), "reads must not create a database"
    assert call("write", tmp_path, {"key": "b", "value": "Beta note"}).output == {
        "key": "b", "revision": 1}
    assert call("write", tmp_path, {"key": "a", "value": "Alpha note"}).ok
    assert call("write", tmp_path, {"key": "b", "value": "Updated BETA"}).output == {
        "key": "b", "revision": 2}
    entries = call("list", tmp_path, {}).output["entries"]
    assert [e["key"] for e in entries] == ["a", "b"]
    assert call("search", tmp_path, {"query": "beta"}).output == {"entries": [entries[1]]}
    assert call("search", tmp_path, {"query": "%"}).output == {"entries": []}
    assert len(call("list", tmp_path, {"limit": 1}).output["entries"]) == 1
    with sqlite3.connect(tmp_path / ".memory.sqlite") as connection:
        assert connection.execute("SELECT value FROM notes WHERE key='b'").fetchone() == (
            "Updated BETA",)


def test_memory_sql_characters_are_data_and_schema_limits_apply(tmp_path):
    key = "'); DROP TABLE notes;--"
    assert call("write", tmp_path, {"key": key, "value": "safe"}).ok
    assert call("search", tmp_path, {"query": key}).output["entries"][0]["value"] == "safe"
    assert call("write", tmp_path, {"key": "x", "value": "x" * 20001}).error_kind == "invalid_input"
    assert call("list", tmp_path, {"limit": 101}).error_kind == "invalid_input"


def test_corrupt_memory_is_reported_without_host_paths(tmp_path):
    (tmp_path / ".memory.sqlite").write_bytes(b"not a database")
    for name, arguments in (("write", {"key": "a", "value": "b"}),
                            ("list", {}), ("search", {"query": "a"})):
        result = call(name, tmp_path, arguments)
        assert result.error_kind == "capability_error"
        assert result.message == "memory database is unavailable or invalid"
