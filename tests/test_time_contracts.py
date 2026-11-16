"""Time manifests are data-only services with explicitly unavailable Builder fakes."""
import json
from pathlib import Path

import pytest

from open_lab_builder.capabilities import invoke, run_self_test

CAPS = Path(__file__).resolve().parent.parent / "worlds/habitat/capabilities"


@pytest.mark.parametrize("ident", ["time.remaining", "time.sleep"])
def test_time_interface_fake_neither_waits_nor_invents_budget(ident, tmp_path):
    directory = CAPS / ident
    manifest = json.loads((directory / "capability.json").read_text(encoding="utf-8"))
    assert manifest["permissions"] == {"filesystem": "none", "network": "none"}
    assert manifest["invocation"] == {"interface": "mcp", "server": "supervisor-time",
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
    ("time.remaining", {"budget_ms": 999999}), ("time.sleep", {"seconds": 0}),
    ("time.sleep", {"seconds": 3601}), ("time.sleep", {"seconds": True}),
    ("time.sleep", {"seconds": 1, "permissions": "all"}),
])
def test_invalid_time_data_never_reaches_a_service(ident, arguments, tmp_path):
    directory = CAPS / ident
    manifest = json.loads((directory / "capability.json").read_text(encoding="utf-8"))

    def unreachable(arguments):
        pytest.fail("invalid time data reached service")

    result = invoke(manifest, directory, arguments, workspace=tmp_path, service=unreachable)
    assert not result.ok and result.error_kind == "invalid_input"
