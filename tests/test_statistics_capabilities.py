from __future__ import annotations

import importlib.util
import json
import math
from fractions import Fraction
from pathlib import Path

import pytest

from open_lab_builder.capabilities import INVALID_INPUT, invoke, run_self_test
from open_lab_builder.contracts import validate_document

CAPABILITIES = Path(__file__).resolve().parents[1] / "worlds/minimal/capabilities"


def module(ident):
    path = CAPABILITIES / ident / "implementation.py"
    spec = importlib.util.spec_from_file_location(ident, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


describe = module("stats.describe")
regress = module("stats.regress")


def manifest(ident):
    directory = CAPABILITIES / ident
    return json.loads((directory / "capability.json").read_text(encoding="utf-8")), directory


def test_describe_population_and_inclusive_quartiles():
    result = describe.run({"values": [4, 1, 3, 2]})
    assert result == {"count": 4, "mean": 2.5, "median": 2.5, "variance": 1.25,
                      "stdev": math.sqrt(1.25),
                      "quantiles": {"q1": 1.75, "q2": 2.5, "q3": 3.25}}


def test_describe_singleton_constant_and_cancellation():
    one = describe.run({"values": [7]})
    assert one == {"count": 1, "mean": 7, "median": 7, "variance": 0, "stdev": 0,
                   "quantiles": {"q1": 7, "q2": 7, "q3": 7}}
    assert describe.run({"values": [7] * 10000})["variance"] == 0
    assert describe.run({"values": [1e12, 0.001, -1e12]})["mean"] == pytest.approx(0.001 / 3)
    assert describe.run({"values": [-1e12, 1e12]})["variance"] == 1e24


@pytest.mark.parametrize("values", [[], [1] * 10001, [True], ["1"], [None], [float("nan")],
                                    [float("inf")], [-float("inf")], [1e12 + 1],
                                    [-1e12 - 1], [10**1000], {}, "[1, 2]"])
def test_describe_refuses_invalid_values(values):
    with pytest.raises(ValueError):
        describe.run({"values": values})


@pytest.mark.parametrize("arguments", [{}, {"values": [1], "code": "print(1)"}, None])
def test_describe_closed_arguments(arguments):
    with pytest.raises(ValueError):
        describe.run(arguments)


def test_describe_manifest_and_subprocess_protocol():
    document, directory = manifest("stats.describe")
    assert validate_document(document) == []
    assert run_self_test(document, directory) == []
    assert document["permissions"] == {"filesystem": "none", "network": "none"}
    result = invoke(document, directory, {"values": [2, 4, 6]})
    assert result.ok
    assert result.output["variance"] == pytest.approx(8 / 3)
    assert invoke(document, directory, {"values": [True]}).error_kind == INVALID_INPUT
    assert not invoke(document, directory, {"values": [float("nan")]}).ok


def test_regress_known_line_and_nonperfect_fit_against_exact_arithmetic():
    assert regress.run({"x": [1, 2, 3], "y": [3, 5, 7]}) == {
        "count": 3, "slope": 2, "intercept": 1, "r": 1}
    x, y = [1, 2, 3, 4], [3, 5, 4, 8]
    mx, my = Fraction(sum(x), 4), Fraction(sum(y), 4)
    xx = sum((v - mx) ** 2 for v in x)
    yy = sum((v - my) ** 2 for v in y)
    xy = sum((a - mx) * (b - my) for a, b in zip(x, y, strict=True))
    result = regress.run({"x": x, "y": y})
    assert result["slope"] == pytest.approx(float(xy / xx))
    assert result["intercept"] == pytest.approx(float(my - xy / xx * mx))
    assert result["r"] == pytest.approx(float(xy) / math.sqrt(float(xx * yy)))


def test_regress_constant_y_negative_slope_duplicate_x_and_order_invariance():
    assert regress.run({"x": [1, 1, 2], "y": [7, 7, 7]}) == {
        "count": 3, "slope": 0, "intercept": 7, "r": None}
    expected = {"count": 4, "slope": -3, "intercept": 1, "r": -1}
    assert regress.run({"x": [0, 1, 1, 2], "y": [1, -2, -2, -5]}) == expected
    assert regress.run({"x": [2, 1, 0, 1], "y": [-5, -2, 1, -2]}) == expected


def test_regress_tiny_scales_and_large_offset():
    tiny = regress.run({"x": [0, 1e-200, 2e-200], "y": [0, 2e-200, 4e-200]})
    assert tiny == {"count": 3, "slope": 2, "intercept": 0, "r": 1}
    assert regress.run({"x": [1e12 - 2, 1e12 - 1, 1e12], "y": [1, 3, 5]}) == {
        "count": 3, "slope": 2, "intercept": 5 - 2e12, "r": 1}
    with pytest.raises(ValueError, match="finite floating point"):
        regress.run({"x": [0, 1e-320], "y": [0, 1]})


@pytest.mark.parametrize("arguments", [
    {}, {"x": [1, 2]}, {"x": [1, 2], "y": [1, 2], "expression": "eval"},
    {"x": [1], "y": [2]}, {"x": [1, 2], "y": [1, 2, 3]},
    {"x": [1, 1], "y": [1, 2]}, {"x": [1, 2], "y": [1, True]},
    {"x": [1, 2], "y": [1, "2"]}, {"x": [float("nan"), 2], "y": [1, 2]},
    {"x": [1, 2], "y": [1, float("inf")]}, {"x": [1, 1e12 + 1], "y": [1, 2]},
    {"x": [1] * 10001, "y": [2] * 10001}, None,
])
def test_regress_refuses_invalid_pairs(arguments):
    with pytest.raises(ValueError):
        regress.run(arguments)


def test_regress_manifest_and_subprocess_protocol():
    document, directory = manifest("stats.regress")
    assert validate_document(document) == []
    assert run_self_test(document, directory) == []
    assert document["permissions"] == {"filesystem": "none", "network": "none"}
    result = invoke(document, directory, {"x": [0, 1, 2], "y": [1, 3, 5]})
    assert result.ok
    assert result.output == {"count": 3, "slope": 2, "intercept": 1, "r": 1}
    assert invoke(document, directory, {"x": [True, 2], "y": [1, 2]}).error_kind == INVALID_INPUT
    assert not invoke(document, directory, {"x": [0, float("nan")], "y": [1, 2]}).ok
