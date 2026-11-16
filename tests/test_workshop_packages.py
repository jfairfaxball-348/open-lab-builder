"""Package discovery and science-runner defaults without heavy host dependencies."""

from importlib.metadata import version

from test_habitat_capabilities import call


def test_distribution_inventory_is_sorted_deduplicated_and_reports_absence(tmp_path):
    result = call("python.packages", tmp_path,
                  names=["jsonschema", "open-lab-missing-package", "jsonschema"])
    assert result.ok
    assert result.output == {"packages": [
        {"name": "jsonschema", "version": version("jsonschema")},
        {"name": "open-lab-missing-package", "version": None},
    ]}


def test_science_defaults_ignore_host_plotting_and_thread_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENBLAS_NUM_THREADS", "500")
    monkeypatch.setenv("MPLBACKEND", "QtAgg")
    result = call("python.run", tmp_path, code='''
import os, pathlib
assert os.environ["OPENBLAS_NUM_THREADS"] == os.environ["OMP_NUM_THREADS"] == "1"
assert os.environ["MPLBACKEND"] == "Agg"
assert pathlib.Path(os.environ["MPLCONFIGDIR"]).is_relative_to(pathlib.Path.cwd())
print("bounded")
''')
    assert result.ok and result.output["exit_code"] == 0
    assert result.output["stdout"] == "bounded\n"
