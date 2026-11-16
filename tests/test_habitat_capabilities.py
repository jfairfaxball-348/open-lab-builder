"""S015: the Habitat's read, edit and run capabilities, tested on the host.

These exercise the capability code itself. That python.run is only ever offered
inside a container, with no network and the workspace as the only writable
directory, is enforced and tested by the Simulation (container tier).
"""
import importlib.util
import json
import sys
import textwrap
import time
from pathlib import Path

import pytest

from open_lab_builder.capabilities import invoke, run_self_test

ROOT = Path(__file__).resolve().parent.parent
HABITAT = ROOT / "worlds" / "habitat"
CAPABILITIES = HABITAT / "capabilities"


def load(capability_id):
    directory = CAPABILITIES / capability_id
    return json.loads((directory / "capability.json").read_text(encoding="utf-8")), directory


def call(capability_id, workspace, **arguments):
    manifest, directory = load(capability_id)
    return invoke(manifest, directory, arguments, workspace=workspace)


def module(capability_id):
    path = CAPABILITIES / capability_id / "implementation.py"
    spec = importlib.util.spec_from_file_location(f"habitat_{capability_id}", path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_world_is_container_tier_with_broker_only_model_services():
    world = json.loads((HABITAT / "world.json").read_text(encoding="utf-8"))
    assert world["world_id"] == "habitat"
    assert world["environment"]["isolation"]["minimum_tier"] == "container"
    names = sorted(p.name for p in CAPABILITIES.iterdir() if p.is_dir())
    assert {"models.ask", "models.list"} <= set(names)
    for ident in ("models.ask", "models.list"):
        manifest, _ = load(ident)
        assert manifest["invocation"] == {
            "interface": "mcp", "server": "supervisor-gateway", "tool": ident}
        assert manifest["permissions"] == {"filesystem": "none", "network": "none", "gpu": False}
    assert {"workspace.read", "workspace.edit", "python.run"} <= set(names)
    for name in names:
        manifest, _ = load(name)
        assert manifest["permissions"]["network"] == "none"
        assert not manifest["permissions"].get("gpu")
    assert load("python.run")[0]["permissions"]["subprocess"] is True


@pytest.mark.parametrize("capability_id", ["workspace.read", "workspace.edit", "python.run"])
def test_self_tests_pass(capability_id):
    manifest, directory = load(capability_id)
    assert run_self_test(manifest, directory) == []


@pytest.mark.parametrize("ident", ["models.list", "models.ask"])
def test_local_assistant_contract_self_tests_use_only_builder_fakes(ident, tmp_path):
    manifest, directory = load(ident)
    assert run_self_test(manifest, directory) == []
    args = {} if ident == "models.list" else {"model_id": "granite-text", "prompt": "Task"}
    assert not invoke(manifest, directory, args, workspace=tmp_path).ok
    fake = ({"models": [], "context_tokens": 2048, "max_output_tokens": 512,
             "max_prompt_utf8_bytes": 1280} if ident == "models.list" else
            {"text": "Labelled fake reply", "truncated": False})
    result = invoke(manifest, directory, args, workspace=tmp_path, service=lambda _: fake)
    assert result.ok
    if ident == "models.list":
        assert result.output["models"] == []
    else:
        assert result.output["truncated"] is False
    assert list(tmp_path.iterdir()) == []


def test_local_assistant_selector_contract_rejects_endpoint_arguments(tmp_path):
    assert not call("models.ask", tmp_path, model_id="http://localhost", prompt="Task").ok
    assert not call("models.ask", tmp_path, model_id="granite-text", prompt="Task",
                    endpoint="http://localhost").ok


# --- workspace.read -----------------------------------------------------------------


def test_read_whole_file_pages_and_missing(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes/a.txt").write_bytes(b"one\ntwo\nthree\nfour")
    whole = call("workspace.read", tmp_path, path="notes/a.txt").output
    assert whole == {"path": "notes/a.txt", "exists": True, "text": "one\ntwo\nthree\nfour",
                     "start_line": 1, "end_line": 4, "total_lines": 4, "truncated": False}
    page = call("workspace.read", tmp_path, path="notes/a.txt", start_line=2,
                max_lines=2).output
    assert (page["text"], page["end_line"], page["truncated"]) == ("two\nthree\n", 3, True)
    past = call("workspace.read", tmp_path, path="notes/a.txt", start_line=9).output
    assert (past["text"], past["truncated"]) == ("", False)
    assert call("workspace.read", tmp_path, path="nope.md").output == {
        "path": "nope.md", "exists": False}


def test_read_refuses_directories_binary_and_escapes(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "b.bin").write_bytes(b"\xff\xfe\x00")
    assert "directory" in call("workspace.read", tmp_path, path="d").message
    assert "UTF-8" in call("workspace.read", tmp_path, path="b.bin").message
    for bad in ("../x", "/etc/passwd", "a\\b", "C:/x"):
        assert not call("workspace.read", tmp_path, path=bad).ok


def test_read_caps_returned_characters(tmp_path):
    (tmp_path / "big.txt").write_text("x" * 150_000, encoding="utf-8", newline="")
    result = call("workspace.read", tmp_path, path="big.txt").output
    assert len(result["text"]) == 100_000 and result["truncated"] is True


# --- workspace.edit -----------------------------------------------------------------


def test_edit_replaces_exactly_once_and_reports(tmp_path):
    (tmp_path / "p.py").write_text("pritn('hi')\n", encoding="utf-8", newline="")
    result = call("workspace.edit", tmp_path, path="p.py", old_text="pritn(",
                  new_text="print(")
    assert result.output == {"path": "p.py", "replacements": 1, "bytes_written": 12}
    assert (tmp_path / "p.py").read_text(encoding="utf-8") == "print('hi')\n"
    assert [p.name for p in tmp_path.iterdir()] == ["p.py"]  # no temporary left behind


def test_edit_refuses_ambiguity_and_absence_unless_asked(tmp_path):
    (tmp_path / "t.txt").write_text("a a a", encoding="utf-8", newline="")
    ambiguous = call("workspace.edit", tmp_path, path="t.txt", old_text="a", new_text="b")
    assert "occurs 3 times" in ambiguous.message
    assert (tmp_path / "t.txt").read_text(encoding="utf-8") == "a a a"
    assert "not found" in call("workspace.edit", tmp_path, path="t.txt", old_text="zz",
                               new_text="b").message
    every = call("workspace.edit", tmp_path, path="t.txt", old_text="a", new_text="b",
                 replace_all=True)
    assert every.output["replacements"] == 3
    assert "does not exist" in call("workspace.edit", tmp_path, path="new.txt",
                                    old_text="a", new_text="b").message


def test_edit_append_creates_and_extends(tmp_path):
    call("workspace.edit", tmp_path, path="log/j.md", append_text="one\n")
    call("workspace.edit", tmp_path, path="log/j.md", append_text="two\n")
    assert (tmp_path / "log/j.md").read_text(encoding="utf-8") == "one\ntwo\n"


@pytest.mark.parametrize("arguments", [
    {"path": "x.txt"},
    {"path": "x.txt", "old_text": "a"},
    {"path": "x.txt", "old_text": "a", "new_text": "b", "append_text": "c"},
])
def test_edit_needs_exactly_one_form(tmp_path, arguments):
    (tmp_path / "x.txt").write_text("a", encoding="utf-8", newline="")
    assert not call("workspace.edit", tmp_path, **arguments).ok
    assert (tmp_path / "x.txt").read_text(encoding="utf-8") == "a"


def test_edit_refuses_escapes(tmp_path):
    for bad in ("../x", "/abs", "a/../b"):
        assert not call("workspace.edit", tmp_path, path=bad, append_text="x").ok
    assert list(tmp_path.iterdir()) == []


# --- python.run ---------------------------------------------------------------------


def write(workspace, name, source):
    path = workspace / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(source), encoding="utf-8", newline="")


def test_run_saved_program_with_args_stdin_and_files(tmp_path):
    write(tmp_path, "greet.py", """
        import sys
        name = sys.stdin.read().strip()
        print(f"hello {name} {sys.argv[1:]}")
        open("out.txt", "w").write("saved")
    """)
    result = call("python.run", tmp_path, path="greet.py", args=["a", "b"],
                  stdin="world").output
    assert result["exit_code"] == 0 and result["ran"] == "greet.py"
    assert result["stdout"] == "hello world ['a', 'b']\n"
    assert (tmp_path / "out.txt").read_text() == "saved"


def test_a_failure_returns_the_traceback_and_a_fix_can_follow(tmp_path):
    write(tmp_path, "bug.py", "print(1/0)\n")
    failed = call("python.run", tmp_path, path="bug.py").output
    assert failed["exit_code"] == 1 and "ZeroDivisionError" in failed["stderr"]
    assert call("workspace.edit", tmp_path, path="bug.py", old_text="1/0",
                new_text="1/2").ok
    fixed = call("python.run", tmp_path, path="bug.py").output
    assert (fixed["exit_code"], fixed["stdout"]) == (0, "0.5\n")


def test_own_modules_import_each_other(tmp_path):
    write(tmp_path, "tools/geometry.py", "def area(w, h):\n    return w * h\n")
    write(tmp_path, "tools/use.py", "from geometry import area\nprint(area(3, 4))\n")
    assert call("python.run", tmp_path, path="tools/use.py").output["stdout"] == "12\n"
    write(tmp_path, "lib.py", "VALUE = 7\n")
    snippet = call("python.run", tmp_path, code="import lib; print(lib.VALUE)").output
    assert snippet["stdout"] == "7\n"


def test_timeout_kills_the_program_and_its_children(tmp_path):
    write(tmp_path, "child.py", """
        import pathlib, time
        while True:
            pathlib.Path("alive").write_text(str(time.time()))
            time.sleep(0.1)
    """)
    write(tmp_path, "spin.py", """
        import subprocess, sys, time
        subprocess.Popen([sys.executable, "child.py"])
        time.sleep(60)
    """)
    started = time.monotonic()
    result = call("python.run", tmp_path, path="spin.py", timeout_s=2).output
    assert result["timed_out"] is True and result["exit_code"] is None
    assert time.monotonic() - started < 20
    time.sleep(0.5)
    before = (tmp_path / "alive").stat().st_mtime if (tmp_path / "alive").exists() else None
    time.sleep(1.0)
    after = (tmp_path / "alive").stat().st_mtime if (tmp_path / "alive").exists() else None
    assert before == after, "a descendant kept running after the timeout"


def test_output_is_capped_and_flagged(tmp_path):
    result = call("python.run", tmp_path,
                  code="import sys; sys.stdout.write('x' * 200000); sys.stderr.write('e')").output
    assert len(result["stdout"]) == 64_000 and result["stdout_truncated"] is True
    assert (result["stderr"], result["stderr_truncated"]) == ("e", False)


def test_host_environment_does_not_reach_the_program(tmp_path, monkeypatch):
    monkeypatch.setenv("OPEN_LAB_SECRET_PROBE", "should-not-leak")
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    code = ("import os, sys; print(os.environ.get('OPEN_LAB_SECRET_PROBE'), "
            "os.environ.get('OPEN_LAB_WORKSPACE'), sys.flags.ignore_environment)")
    assert call("python.run", tmp_path, code=code).output["stdout"] == "None None 1\n"


def test_run_refuses_bad_targets(tmp_path):
    write(tmp_path, "notes.txt", "print(1)")
    assert "existing .py" in call("python.run", tmp_path, path="notes.txt").message
    assert "existing .py" in call("python.run", tmp_path, path="missing.py").message
    assert not call("python.run", tmp_path, path="../outside.py").ok
    assert not call("python.run", tmp_path).ok
    assert not call("python.run", tmp_path, path="a.py", code="print(1)").ok


def test_missing_workspace_is_refused(monkeypatch):
    monkeypatch.delenv("OPEN_LAB_WORKSPACE", raising=False)
    with pytest.raises(ValueError, match="not configured"):
        module("python.run").run({"code": "print(1)"})


def test_interpreter_is_the_capabilitys_own(tmp_path):
    result = call("python.run", tmp_path, code="import sys; print(sys.version_info[:2])")
    assert result.output["stdout"] == f"{tuple(sys.version_info[:2])}\n"
