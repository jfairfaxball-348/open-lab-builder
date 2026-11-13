"""The capability manifest must be internally consistent, not merely well shaped."""

from __future__ import annotations

from open_lab_builder.contracts import validate_document


def messages(document) -> str:
    return " | ".join(str(issue) for issue in validate_document(document))


def test_demonstration_input_must_match_input_schema(capability):
    capability["demonstrations"][0]["input"] = {"text": 42}
    assert "violates input_schema" in messages(capability)


def test_demonstration_output_must_match_output_schema(capability):
    capability["demonstrations"][0]["expected_output"]["words"] = "three"
    assert "violates output_schema" in messages(capability)


def test_deterministic_demonstration_needs_expected_output(capability):
    del capability["demonstrations"][0]["expected_output"]
    assert "expected_output" in messages(capability)
    capability["demonstrations"][0]["deterministic"] = False
    assert validate_document(capability) == []


def test_self_test_must_reference_real_demonstrations(capability):
    capability["self_test"]["demonstrations"] = ["does-not-exist"]
    assert "no demonstration 'does-not-exist'" in messages(capability)


def test_duplicate_demonstration_ids_are_rejected(capability):
    capability["demonstrations"].append(dict(capability["demonstrations"][0]))
    assert "duplicate demonstration id" in messages(capability)


def test_input_schema_must_itself_be_a_valid_schema(capability):
    capability["input_schema"]["properties"]["text"]["type"] = "not-a-type"
    assert "not a valid JSON Schema" in messages(capability)


def test_at_least_one_demonstration_is_required(capability):
    capability["demonstrations"] = []
    assert validate_document(capability)


def test_each_invocation_interface_is_accepted(capability):
    for invocation in (
        {"interface": "python", "entrypoint": "pkg.mod:fn"},
        {"interface": "subprocess", "command": ["tool", "--json"]},
        {"interface": "http", "method": "POST", "url": "http://127.0.0.1:8000/run"},
        {"interface": "mcp", "server": "local-tools", "tool": "do_thing"},
    ):
        capability["invocation"] = invocation
        assert validate_document(capability) == [], invocation


def test_invocation_cannot_mix_interfaces(capability):
    capability["invocation"] = {"interface": "python", "command": ["tool"]}
    assert validate_document(capability)


def test_agent_created_capability_must_name_its_run(capability):
    capability["provenance"] = {"origin": "agent"}
    assert validate_document(capability)
    capability["provenance"]["created_in_run"] = "run-01"
    assert validate_document(capability) == []
