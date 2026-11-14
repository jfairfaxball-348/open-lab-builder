"""Check real shipped workspace tools, including path boundary refusals."""
from datetime import UTC, datetime

import pytest

from open_lab_builder.capabilities import invoke, run_self_test
from test_capabilities import load, load_module


def module(capability_id):
    _, directory = load(capability_id)
    return load_module(directory / "implementation.py")


@pytest.mark.parametrize("capability_id", ["workspace.write", "workspace.list", "time.now"])
def test_new_capability_self_tests(capability_id, monkeypatch, tmp_path):
    monkeypatch.setenv("OPEN_LAB_WORKSPACE", str(tmp_path))
    manifest, directory = load(capability_id)
    assert run_self_test(manifest, directory) == []
    assert list(tmp_path.iterdir()) == [], "self-tests must use their own disposable workspace"


def test_write_utf8_overwrite_and_list(tmp_path):
    manifest, directory = load("workspace.write")
    result = invoke(manifest, directory, {"path": "notes/a.txt", "text": "café\n"},
                    workspace=tmp_path)
    assert result.output == {"path": "notes/a.txt", "bytes_written": 6}
    assert (tmp_path / "notes/a.txt").read_bytes() == "café\n".encode()
    assert not invoke(manifest, directory, {"path": "notes/a.txt", "text": "new"},
                      workspace=tmp_path).ok
    assert invoke(manifest, directory, {"path": "notes/a.txt", "text": "new", "overwrite": True},
                  workspace=tmp_path).ok
    assert (tmp_path / "notes/a.txt").read_bytes() == b"new"
    manifest, directory = load("workspace.list")
    assert invoke(manifest, directory, {}, workspace=tmp_path).output == {
        "entries": [{"path": "notes", "kind": "directory"}]}
    assert invoke(manifest, directory, {"path": "notes"}, workspace=tmp_path).output == {
        "entries": [{"path": "notes/a.txt", "kind": "file"}]}


@pytest.mark.parametrize("path", ["../escape", "/absolute", "C:/outside", "a\\b", "a/../b",
                                   "//server/share", "a:stream", "NUL.txt", "trailing.",
                                   "a//b", "a/./b", "bad\x00name", "bad\nname"])
@pytest.mark.parametrize("capability_id", ["workspace.write", "workspace.list"])
def test_invalid_paths_are_refused(tmp_path, monkeypatch, path, capability_id):
    monkeypatch.setenv("OPEN_LAB_WORKSPACE", str(tmp_path))
    with pytest.raises(ValueError):
        module(capability_id).run({"path": path, "text": "no"})
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("capability_id", ["workspace.write", "workspace.list"])
def test_missing_workspace_is_an_error(monkeypatch, capability_id):
    monkeypatch.delenv("OPEN_LAB_WORKSPACE", raising=False)
    with pytest.raises(ValueError, match="not configured"):
        module(capability_id).run({"path": "x", "text": "no"})


def test_directory_order_missing_path_and_size_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("OPEN_LAB_WORKSPACE", str(tmp_path))
    listing = module("workspace.list")
    for name in ("z", ".hidden", "a"):
        (tmp_path / name).touch()
    assert [e["path"] for e in listing.run({})["entries"]] == [".hidden", "a", "z"]
    with pytest.raises(ValueError, match="cannot list"):
        listing.run({"path": "missing"})
    for n in range(998):
        (tmp_path / str(n)).touch()
    with pytest.raises(ValueError, match="1000"):
        listing.run({})


def test_links_are_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("OPEN_LAB_WORKSPACE", str(tmp_path))
    target = tmp_path / "original"
    target.write_text("unchanged")
    import os
    os.link(target, tmp_path / "hardlink")
    with pytest.raises(ValueError, match="hard links"):
        module("workspace.write").run({"path": "hardlink", "text": "bad", "overwrite": True})
    assert target.read_text() == "unchanged"
    # Exercise the link rejection branch without requiring Windows symlink privilege.
    monkeypatch.setattr(type(target), "is_symlink", lambda p: p.name == "link")
    for capability_id in ("workspace.write", "workspace.list"):
        with pytest.raises(ValueError, match="links"):
            module(capability_id).run({"path": "link/file", "text": "no"})


def test_time_is_utc_between_host_clock_samples():
    before = datetime.now(UTC).replace(microsecond=0)
    result = module("time.now").run({})
    after = datetime.now(UTC)
    assert before <= datetime.fromisoformat(result["utc"]) <= after
