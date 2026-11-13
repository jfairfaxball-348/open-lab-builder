"""The diagnostic, health check and CLI work on this machine and leak nothing private."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from open_lab_builder import health
from open_lab_builder.cli import main
from open_lab_builder.diagnostics import assess, collect, render_text, sanitise


@pytest.fixture(scope="module")
def raw_report():
    return collect()


def test_diagnostic_reports_core_hardware(raw_report):
    assert raw_report["cpu"]["logical_cores"] >= 1
    assert raw_report["memory"]["total_gb"] > 0
    assert raw_report["disk"]["free_gb"] >= 0
    assert raw_report["tools"]["version_control"]["git"]["found"]


def test_sanitised_report_contains_no_private_details(raw_report):
    text = json.dumps(sanitise(raw_report)).lower()
    home = Path.home()
    user = os.environ.get("USERNAME") or os.environ.get("USER") or home.name
    assert str(home).lower() not in text
    assert home.as_posix().lower() not in text
    assert json.dumps(str(home)).strip('"').lower() not in text
    assert f"/{user}".lower() not in text
    assert '"path"' not in text
    assert '"repos"' not in text


def test_readiness_assessment_and_text_render(raw_report):
    clean = sanitise(raw_report)
    rows = assess(clean)
    assert {row["status"] for row in rows} <= {"usable", "needs_validation", "needs_install"}
    assert any(row["area"] == "Container isolation" for row in rows)
    assert "Readiness" in render_text(clean)


def test_health_check_passes_on_this_repository():
    failures = {r.name: r.problems for r in health.run_checks() if not r.ok}
    assert failures == {}


def test_health_check_detects_a_state_roadmap_mismatch(tmp_path):
    (tmp_path / "docs" / "roadmap").mkdir(parents=True)
    root = health.repo_root()
    state = json.loads((root / health.STATE_PATH).read_text(encoding="utf-8"))
    state["next_milestone"]["id"] = "S999"
    (tmp_path / health.STATE_PATH).write_text(json.dumps(state), encoding="utf-8")
    (tmp_path / health.ROADMAP_PATH).write_text(
        (root / health.ROADMAP_PATH).read_text(encoding="utf-8"), encoding="utf-8"
    )
    assert any("S999" in problem for problem in health.check_state(tmp_path))


def test_cli_validate_accepts_examples(capsys):
    assert main(["validate"]) == 0
    assert "0 invalid" in capsys.readouterr().out


def test_cli_validate_rejects_a_bad_document(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"schema": "open-lab/capability", "schema_version": "1.0.0"}', encoding="utf-8")
    assert main(["validate", str(bad)]) == 1
    assert "FAIL" in capsys.readouterr().out


def test_cli_state_names_the_next_milestone(capsys):
    assert main(["state"]) == 0
    assert "Next:" in capsys.readouterr().out
