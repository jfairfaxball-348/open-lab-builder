"""Phenomena manifests describe data-only supervisor services, not bundled laws."""
import json
from pathlib import Path

import pytest

from open_lab_builder.capabilities import invoke, run_self_test

ROOT = Path(__file__).resolve().parent.parent / "worlds/habitat"


@pytest.mark.parametrize("ident", ["world.observe", "world.act", "world.advance"])
def test_unavailable_build_fake_is_explicit_and_does_not_simulate_a_world(ident, tmp_path):
    directory = ROOT / "capabilities" / ident
    manifest = json.loads((directory / "capability.json").read_text(encoding="utf-8"))
    assert manifest["permissions"] == {"filesystem": "none", "network": "none"}
    assert manifest["invocation"] == {"interface": "mcp", "server": "supervisor-world",
                                      "tool": ident}
    assert run_self_test(manifest, directory) == []
    assert list(directory.iterdir()) == [directory / "capability.json"]
    arguments = manifest["demonstrations"][0]["input"]
    result = invoke(manifest, directory, arguments, workspace=tmp_path,
                    service=lambda arguments: {"available": False})
    assert result.ok and result.output == {"available": False}
    incomplete = invoke(manifest, directory, arguments, workspace=tmp_path,
                        service=lambda arguments: {"available": True})
    assert not incomplete.ok and incomplete.error_kind == "invalid_output"
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("ident, arguments", [
    ("world.observe", {"seed": 3}), ("world.act", {"x": 6, "y": 0, "drive": 3}),
    ("world.act", {"x": 0, "y": 0, "drive": 4}),
    ("world.advance", {"ticks": 0}), ("world.advance", {"ticks": 101}),
    ("world.advance", {"ticks": 1, "code": "print(1)"}),
])
def test_invalid_controls_never_reach_a_service(ident, arguments, tmp_path):
    directory = ROOT / "capabilities" / ident
    manifest = json.loads((directory / "capability.json").read_text(encoding="utf-8"))

    def unreachable(arguments):
        pytest.fail("invalid input reached service")

    result = invoke(manifest, directory, arguments, workspace=tmp_path, service=unreachable)
    assert not result.ok and result.error_kind == "invalid_input"
