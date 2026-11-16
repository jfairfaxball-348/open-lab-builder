"""Builder checks the interface; only Simulation may run agent-tool examples."""
import json
from pathlib import Path

from open_lab_builder.capabilities import invoke, run_self_test

DIRECTORY = Path(__file__).resolve().parent.parent / "worlds/habitat/capabilities/tools.create"


def test_create_self_test_never_executes_or_registers_source(tmp_path):
    manifest = json.loads((DIRECTORY / "capability.json").read_text(encoding="utf-8"))
    demo = manifest["demonstrations"][0]
    assert run_self_test(manifest, DIRECTORY) == []
    source = tmp_path / demo["input"]["source_path"]
    source.write_text("raise RuntimeError('must never run in Builder')", encoding="utf-8")
    result = invoke(manifest, DIRECTORY, demo["input"], workspace=tmp_path,
                    service=lambda arguments: {"id": arguments["id"], "registered": False})
    assert result.ok and result.output == {"id": "agent.double", "registered": False}
    assert list(tmp_path.iterdir()) == [source]
    assert not invoke(manifest, DIRECTORY, demo["input"], workspace=tmp_path).ok


def test_create_interface_cannot_request_privileges_or_shadow_ids(tmp_path):
    manifest = json.loads((DIRECTORY / "capability.json").read_text(encoding="utf-8"))
    arguments = manifest["demonstrations"][0]["input"]
    for changed in ({**arguments, "permissions": {"network": "allowlist"}},
                    {**arguments, "id": "python.run"}, {**arguments, "examples": []}):
        result = invoke(manifest, DIRECTORY, changed, workspace=tmp_path,
                        service=lambda arguments: {"id": arguments["id"], "registered": False})
        assert not result.ok and result.error_kind == "invalid_input"
    assert list(tmp_path.iterdir()) == []
