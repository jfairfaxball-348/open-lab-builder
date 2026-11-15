"""The two shipped capabilities and the build-time invoker."""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from conftest import ROOT
from open_lab_builder.capabilities import (
    CAPABILITY_ERROR,
    EXECUTION_ERROR,
    INVALID_INPUT,
    INVALID_OUTPUT,
    TIMEOUT,
    UNSUPPORTED_INTERFACE,
    invoke,
    run_self_test,
)
from open_lab_builder.contracts import validate_document

CAPABILITIES = ROOT / "worlds" / "minimal" / "capabilities"


def test_specialist_build_self_test_is_explicitly_fake_and_direct_use_is_refused():
    manifest, directory = load("models.ask")
    assert validate_document(manifest) == []
    assert run_self_test(manifest, directory) == []
    result = invoke(manifest, directory, {"prompt": "Hello"})
    assert result.error_kind == UNSUPPORTED_INTERFACE
    received = []

    def service(arguments):
        received.append(arguments)
        return {"text": "Fake reply"}

    assert invoke(manifest, directory, {"prompt": "Hello"}, service=service).output == {
        "text": "Fake reply"}
    assert received == [{"prompt": "Hello"}]
    assert invoke(manifest, directory, {"prompt": "x" * 6001},
                  service=service).error_kind == INVALID_INPUT
    assert len(received) == 1
    assert invoke(manifest, directory, {"prompt": "Hello"},
                  service=lambda _: {"text": "x" * 6001}).error_kind == INVALID_OUTPUT


def load(capability_id: str) -> tuple[dict, Path]:
    directory = CAPABILITIES / capability_id
    return json.loads((directory / "capability.json").read_text(encoding="utf-8")), directory


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


math_evaluate = load_module(CAPABILITIES / "math.evaluate" / "math_evaluate.py")
text_stats = load_module(CAPABILITIES / "text.stats" / "text_stats.py")


# --- text.stats -------------------------------------------------------------

@pytest.mark.parametrize(
    "text, expected",
    [
        ("", (0, 0, 0)),
        ("hello world\ngoodbye", (19, 3, 2)),
        ("one line\n", (9, 2, 1)),
        ("\n\n", (2, 0, 2)),
        ("a\r\nb\r\n", (6, 2, 2)),
        ("a\rb", (3, 2, 2)),
        ("  spaced   out  ", (16, 2, 1)),
        ("naïve café", (10, 2, 1)),
    ],
)
def test_text_stats_counts(text, expected):
    result = text_stats.run({"text": text})
    assert (result["characters"], result["words"], result["lines"]) == expected


def test_text_stats_through_the_invoker():
    manifest, directory = load("text.stats")
    result = invoke(manifest, directory, {"text": "hello world\ngoodbye"})
    assert result.ok
    assert result.output == {"characters": 19, "words": 3, "lines": 2}


# --- math.evaluate ----------------------------------------------------------

@pytest.mark.parametrize(
    "expression, expected",
    [
        ("1/2 + 1/4", Fraction(3, 4)),
        ("0.1 + 0.2", Fraction(3, 10)),
        ("2 ** 10", Fraction(1024)),
        ("2 ** -2", Fraction(1, 4)),
        ("-(3 - 5) * +2", Fraction(4)),
        ("7 % 3", Fraction(1)),
        ("7.5 % 2", Fraction(3, 2)),
        ("1e3 + 1", Fraction(1001)),
        ("1_000 * 2", Fraction(2000)),
        ("0x10 + 1", Fraction(17)),
        ("  (1 + 2) * 3  ", Fraction(9)),
        ("2 ** 1000", Fraction(2**1000)),
        # Deep but legal nesting must be answered, not crash the evaluator.
        ("-" * 499 + "1", Fraction(-1)),
        ("(" * 150 + "1" + ")" * 150, Fraction(1)),
    ],
)
def test_math_evaluates_exactly(expression, expected):
    assert math_evaluate.evaluate(expression) == expected


@pytest.mark.parametrize(
    "expression, message",
    [
        ("x + 1", "names are not allowed"),
        ("abs(-1)", "function calls are not allowed"),
        ("__import__('os').system('echo hi')", "function calls are not allowed"),
        ("(1).real", "attribute access is not allowed"),
        ("(1).__class__", "attribute access is not allowed"),
        ("2 ** 1001", "exponent too large"),
        ("2 ** 3 ** 9", "exponent too large"),
        ("2 ** 0.5", "exponent must be a whole number"),
        ("(10 ** 1000) ** 1000", "result too large"),
        ("1e999999999", "number too large"),
        ("1e-999999999", "decimal exponent too large"),
        ("1 / 0", "division by zero"),
        ("1 % 0", "division by zero"),
        ("0 ** -1", "division by zero"),
        ("'a' * 3", "only numbers are allowed"),
        ("True + 1", "only numbers are allowed"),
        ("1j", "only numbers are allowed"),
        ("1 // 2", "unsupported operator"),
        ("1 << 200", "unsupported operator"),
        ("~1", "unsupported syntax"),
        ("[1, 2]", "unsupported syntax"),
        ("lambda: 1", "unsupported syntax"),
        ("1 if 1 else 2", "unsupported syntax"),
        ("1 +", "not a valid arithmetic expression"),
        ("1; 2", "not a valid arithmetic expression"),
        ("import os", "not a valid arithmetic expression"),
        ("(" * 300 + "1" + ")" * 300, "expression too long"),
    ],
)
def test_math_rejects_everything_else(expression, message):
    with pytest.raises(math_evaluate.EvaluationError) as raised:
        math_evaluate.evaluate(expression)
    assert message in str(raised.value)


def test_math_result_too_large_for_a_float_is_an_error():
    with pytest.raises(math_evaluate.EvaluationError, match="too large"):
        math_evaluate.run({"expression": "10 ** 400"})


def test_math_through_the_invoker():
    manifest, directory = load("math.evaluate")
    result = invoke(manifest, directory, {"expression": "1/2 + 1/4"})
    assert result.ok
    assert result.output == {"value": 0.75, "exact": "3/4"}


@pytest.mark.parametrize(
    "expression, message",
    [
        ("1 / 0", "division by zero"),
        ("x + 1", "names are not allowed: 'x'"),
        ("open('f')", "function calls are not allowed"),
        ("(1).real", "attribute access is not allowed"),
        ("9 ** 99999", "exponent too large (limit 1000)"),
    ],
)
def test_math_reports_refusals_as_error_results(expression, message):
    manifest, directory = load("math.evaluate")
    result = invoke(manifest, directory, {"expression": expression})
    assert (result.status, result.error_kind, result.message) == (
        "error", CAPABILITY_ERROR, message
    )


@pytest.mark.parametrize("capability_id", ["text.stats", "math.evaluate"])
def test_shipped_capability_passes_its_self_test(capability_id):
    manifest, directory = load(capability_id)
    assert validate_document(manifest) == []
    assert run_self_test(manifest, directory) == []


# --- the invoker, against throwaway capabilities -----------------------------

def make_capability(tmp_path: Path, code: str, **changes) -> tuple[dict, Path]:
    """A valid capability whose implementation is ``code``; it takes {"n": integer}."""
    directory = tmp_path / "probe.tool"
    directory.mkdir()
    (directory / "probe.py").write_text(code, encoding="utf-8")
    manifest, _ = load("text.stats")
    manifest.update(
        id="probe.tool",
        invocation={"interface": "python", "entrypoint": "probe:run"},
        input_schema={
            "type": "object", "required": ["n"], "additionalProperties": False,
            "properties": {"n": {"type": "integer"}},
        },
        output_schema={
            "type": "object", "required": ["n"], "additionalProperties": False,
            "properties": {"n": {"type": "integer"}},
        },
        demonstrations=[{"id": "one", "title": "One", "input": {"n": 1},
                         "expected_output": {"n": 1}}],
        self_test={"demonstrations": ["one"]},
    )
    manifest.update(changes)
    assert validate_document(manifest) == []
    return manifest, directory


MARKER = "from pathlib import Path\nPath('ran.txt').write_text('x')\n"


def test_invalid_arguments_are_rejected_before_any_code_runs(tmp_path):
    manifest, directory = make_capability(
        tmp_path, MARKER + "def run(a):\n    return {'n': a['n']}\n"
    )
    for arguments in ({"n": "one"}, {}, {"n": 1, "extra": 2}, [1], None):
        result = invoke(manifest, directory, arguments)
        assert (result.status, result.error_kind) == ("error", INVALID_INPUT)
    assert not (directory / "ran.txt").exists()

    assert invoke(manifest, directory, {"n": 1}).output == {"n": 1}
    assert (directory / "ran.txt").exists(), "the marker proves the check above was meaningful"


def test_result_violating_output_schema_is_rejected(tmp_path):
    manifest, directory = make_capability(tmp_path, "def run(a):\n    return {'n': 'text'}\n")
    assert invoke(manifest, directory, {"n": 1}).error_kind == INVALID_OUTPUT


def test_value_error_is_a_reported_error_and_other_exceptions_are_crashes(tmp_path):
    code = (
        "def run(a):\n"
        "    if a['n'] == 0:\n"
        "        raise ValueError('n must not be zero')\n"
        "    return {'n': 1 // (a['n'] - 1)}\n"
    )
    manifest, directory = make_capability(tmp_path, code)
    refused = invoke(manifest, directory, {"n": 0})
    assert (refused.error_kind, refused.message) == (CAPABILITY_ERROR, "n must not be zero")
    crashed = invoke(manifest, directory, {"n": 1})
    assert crashed.error_kind == EXECUTION_ERROR
    assert "ZeroDivisionError" in crashed.message


def test_timeout_is_enforced(tmp_path):
    code = "import time\ndef run(a):\n    time.sleep(30)\n    return {'n': 1}\n"
    manifest, directory = make_capability(tmp_path, code)
    assert invoke(manifest, directory, {"n": 1}, timeout_s=1).error_kind == TIMEOUT


def test_missing_entrypoint_and_missing_program_are_execution_errors(tmp_path):
    manifest, directory = make_capability(tmp_path, "")
    manifest["invocation"]["entrypoint"] = "absent:run"
    assert invoke(manifest, directory, {"n": 1}).error_kind == EXECUTION_ERROR
    manifest["invocation"] = {"interface": "subprocess", "command": ["no-such-program-olb"]}
    assert invoke(manifest, directory, {"n": 1}).error_kind == EXECUTION_ERROR


def test_interfaces_the_builder_cannot_run_are_reported_not_faked(tmp_path):
    manifest, directory = make_capability(tmp_path, "")
    manifest["invocation"] = {"interface": "http", "method": "POST", "url": "http://127.0.0.1:9/"}
    assert invoke(manifest, directory, {"n": 1}).error_kind == UNSUPPORTED_INTERFACE


def test_self_test_reports_a_wrong_answer(tmp_path):
    manifest, directory = make_capability(tmp_path, "def run(a):\n    return {'n': a['n'] + 1}\n")
    problems = run_self_test(manifest, directory)
    assert len(problems) == 1
    assert "demonstration 'one'" in problems[0]


def test_invoking_leaves_no_bytecode_behind(tmp_path):
    manifest, directory = make_capability(tmp_path, "def run(a):\n    return a\n")
    assert invoke(manifest, directory, {"n": 1}).ok
    assert sorted(p.name for p in directory.iterdir()) == ["probe.py"]
