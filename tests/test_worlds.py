"""Building and verifying world releases."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from conftest import ROOT
from open_lab_builder import health
from open_lab_builder.cli import main
from open_lab_builder.contracts import validate_document, validate_file
from open_lab_builder.paths import data_root
from open_lab_builder.worlds import (
    MANIFEST_NAME,
    BuildError,
    build_world,
    load_source,
    verify_release,
)

MINIMAL = ROOT / "worlds" / "minimal"


@pytest.fixture(scope="module")
def release(tmp_path_factory) -> Path:
    """One pristine build of the minimal world. Tests must not modify it."""
    return build_world(MINIMAL, tmp_path_factory.mktemp("out")).release_dir


@pytest.fixture
def copy_of_release(release, tmp_path) -> Path:
    return Path(shutil.copytree(release, tmp_path / "release"))


@pytest.fixture
def source(tmp_path) -> Path:
    """A private, editable copy of the minimal world source."""
    return Path(shutil.copytree(
        MINIMAL, tmp_path / "source", ignore=shutil.ignore_patterns("__pycache__")
    ))


def edit_json(path: Path, change) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    change(document)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")


def everything_under(directory: Path) -> list[str]:
    return sorted(p.relative_to(directory).as_posix() for p in directory.rglob("*"))


# --- build ------------------------------------------------------------------

def test_build_produces_a_validated_release(release):
    manifest = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert validate_file(release / MANIFEST_NAME) == []
    assert manifest["status"] == "validated"
    assert (manifest["world_id"], manifest["version"]) == ("minimal", "0.4.0")
    assert release.parts[-2:] == ("minimal", "0.4.0")
    assert [c["id"] for c in manifest["capabilities"]] == [
        "math.evaluate", "text.stats", "time.now", "workspace.list", "workspace.write"
    ]
    assert [m["provider_id"] for m in manifest["model_manifests"]] == ["ollama-local"]
    for entry in (*manifest["capabilities"], *manifest["model_manifests"]):
        assert validate_file(release / entry["manifest_path"]) == []


def test_release_bundles_the_contracts_it_lists(release):
    manifest = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert len(manifest["contracts"]) == 8  # seven contracts and the shared definitions
    for name, version in manifest["contracts"].items():
        bundled = json.loads(
            (release / "contracts" / "v1" / f"{name}.schema.json").read_text(encoding="utf-8")
        )
        assert bundled["x-schema-version"] == version
    assert not (release / "contracts" / "v1" / "development-state.schema.json").exists()


def test_release_contains_no_build_residue(release):
    names = everything_under(release)
    assert not [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
    assert not [n for n in everything_under(release.parent) if n.startswith(".building")]


def test_building_twice_gives_the_same_digest(release, tmp_path):
    first = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    later = datetime(2030, 1, 1, tzinfo=UTC)
    second = build_world(MINIMAL, tmp_path / "again", now=later).manifest
    assert second["created_at"] == "2030-01-01T00:00:00Z"
    assert second["created_at"] != first["created_at"]
    assert second["content_digest"] == first["content_digest"]


def test_rebuilding_an_identical_release_in_place_is_a_no_op(source, tmp_path):
    first = build_world(source, tmp_path / "out")
    before = everything_under(tmp_path / "out")
    again = build_world(source, tmp_path / "out", now=datetime(2030, 1, 1, tzinfo=UTC))
    assert again.reused and not first.reused
    assert again.manifest["created_at"] == first.manifest["created_at"]
    assert everything_under(tmp_path / "out") == before


def test_an_existing_release_is_never_overwritten(source, tmp_path):
    first = build_world(source, tmp_path / "out")
    (source / "capabilities" / "text.stats" / "text_stats.py").write_text(
        (source / "capabilities" / "text.stats" / "text_stats.py").read_text(encoding="utf-8")
        + "\n# changed\n", encoding="utf-8", newline="\n",
    )
    with pytest.raises(BuildError, match="immutable"):
        build_world(source, tmp_path / "out")
    assert verify_release(first.release_dir) == []
    assert everything_under(tmp_path / "out" / "minimal")[0] == "0.4.0"
    assert not [n for n in everything_under(tmp_path / "out") if ".building" in n]


def test_any_source_change_changes_the_digest(source, tmp_path, release):
    original = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    edit_json(source / "world.json", lambda d: d["default_permissions"].update(network="none"))
    changed = build_world(source, tmp_path / "out").manifest
    assert changed["content_digest"] != original["content_digest"]


def test_failing_demonstration_fails_the_build_and_leaves_nothing(source, tmp_path):
    def wrong(document):
        document["demonstrations"][0]["expected_output"]["words"] = 99

    edit_json(source / "capabilities" / "text.stats" / "capability.json", wrong)
    out = tmp_path / "out"
    with pytest.raises(BuildError) as raised:
        build_world(source, out)
    assert "text.stats demonstration 'two-lines'" in raised.value.problems[0]
    assert everything_under(out) == [], "no release, no staging directory, no world directory"


def test_crashing_capability_fails_the_build(source, tmp_path):
    (source / "capabilities" / "text.stats" / "text_stats.py").write_text(
        "def run(arguments):\n    raise RuntimeError('broken')\n", encoding="utf-8"
    )
    with pytest.raises(BuildError, match="execution_error"):
        build_world(source, tmp_path / "out")
    assert everything_under(tmp_path / "out") == []


@pytest.mark.parametrize(
    "path, change, expected",
    [
        ("world.json", lambda d: d.pop("default_limits"), "missing 'default_limits'"),
        ("world.json", lambda d: d.update(surprise=1), "unknown field 'surprise'"),
        ("world.json", lambda d: d.update(version="one"), "version"),
        ("capabilities/text.stats/capability.json", lambda d: d.update(id="text.other"),
         "must equal the directory name"),
        ("capabilities/text.stats/capability.json", lambda d: d.pop("summary"), "summary"),
        ("capabilities/text.stats/capability.json",
         lambda d: d["invocation"].update(entrypoint="absent:run"), "has no file"),
        ("capabilities/text.stats/capability.json",
         lambda d: d.update(provenance={"origin": "agent", "created_in_run": "run-1"}),
         "only builder-made capabilities"),
        ("capabilities/math.evaluate/capability.json",
         lambda d: d["permissions"].update(subprocess=True), "container isolation tier"),
        ("models/ollama-local.json", lambda d: d.pop("models"), "models"),
    ],
)
def test_malformed_source_is_refused(source, tmp_path, path, change, expected):
    edit_json(source / path, change)
    with pytest.raises(BuildError) as raised:
        build_world(source, tmp_path / "out")
    assert expected in " | ".join(raised.value.problems)
    assert not (tmp_path / "out").exists() or everything_under(tmp_path / "out") == []


def test_source_without_world_json_is_refused(tmp_path):
    with pytest.raises(BuildError):
        load_source(tmp_path)


# --- verify -----------------------------------------------------------------

def test_fresh_release_verifies_with_self_tests(release):
    before = everything_under(release)
    assert verify_release(release, self_tests=True) == []
    assert everything_under(release) == before


@pytest.mark.parametrize(
    "relative",
    [
        "capabilities/math.evaluate/math_evaluate.py",
        "capabilities/text.stats/capability.json",
        "contracts/v1/observation-event.schema.json",
        "models/ollama-local.json",
    ],
)
def test_changing_one_byte_fails_verification(copy_of_release, relative):
    target = copy_of_release / relative
    data = bytearray(target.read_bytes())
    # Swap one space for a tab: still valid JSON or Python, so only the digest can catch it.
    data[data.index(b" ")] = ord("\t")
    target.write_bytes(bytes(data))
    problems = verify_release(copy_of_release)
    assert f"{relative}: content has changed" in problems
    assert "content_digest does not match the release content" in problems


def test_added_and_removed_files_fail_verification(copy_of_release):
    (copy_of_release / "capabilities" / "text.stats" / "extra.py").write_text("x = 1\n")
    (copy_of_release / "models" / "ollama-local.json").unlink()
    problems = verify_release(copy_of_release)
    assert "capabilities/text.stats/extra.py: file is not part of the release" in problems
    assert "models/ollama-local.json: file is missing" in problems


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d["default_permissions"].update(network="allowlist", network_allowlist=["x.org"]),
        lambda d: d["default_limits"].update(wall_clock_s=999999),
        lambda d: d["environment"]["isolation"].update(minimum_tier="container"),
        lambda d: d["capabilities"].pop(),
        lambda d: d["extensions"]["files"].pop(),
        lambda d: d.update(name="Another world"),
    ],
)
def test_editing_the_manifest_fails_verification(copy_of_release, change):
    edit_json(copy_of_release / MANIFEST_NAME, change)
    assert "content_digest does not match the release content" in verify_release(copy_of_release)


def test_build_details_are_not_part_of_the_digest(copy_of_release):
    edit_json(copy_of_release / MANIFEST_NAME,
              lambda d: d.update(created_at="2031-05-05T05:05:05Z"))
    assert verify_release(copy_of_release) == []


def test_tampering_cannot_hide_behind_an_edited_file_list(copy_of_release):
    target = copy_of_release / "capabilities" / "text.stats" / "text_stats.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8", newline="\n")
    edit_json(copy_of_release / MANIFEST_NAME, lambda d: d["extensions"].pop("files"))
    assert verify_release(copy_of_release) == ["content_digest does not match the release content"]


def test_verification_fails_without_a_usable_manifest_or_contracts(copy_of_release, tmp_path):
    assert verify_release(tmp_path)
    edit_json(copy_of_release / MANIFEST_NAME, lambda d: d.update(status="draft"))
    assert verify_release(copy_of_release)
    shutil.rmtree(copy_of_release / "contracts")
    assert verify_release(copy_of_release) == [
        f"{MANIFEST_NAME}: the release bundles no contracts"
    ]


def test_self_test_rerun_catches_a_broken_implementation(source, tmp_path):
    """A release whose digests are consistent but whose code no longer works."""
    built = build_world(source, tmp_path / "out").release_dir
    assert verify_release(built, self_tests=True) == []
    code = built / "capabilities" / "text.stats" / "text_stats.py"
    code.write_text("def run(arguments):\n    return {}\n", encoding="utf-8")
    assert verify_release(built, self_tests=True)


# --- command line, data root, repository consistency --------------------------

def test_cli_build_then_verify(tmp_path, capsys):
    assert main(["world", "build", str(MINIMAL), "--out", str(tmp_path)]) == 0
    assert "content digest: sha256:" in capsys.readouterr().out
    built = tmp_path / "minimal" / "0.4.0"
    assert main(["world", "verify", str(built), "--self-test"]) == 0
    (built / "models" / "ollama-local.json").write_text("{}", encoding="utf-8")
    assert main(["world", "verify", str(built)]) == 1
    assert "FAILED" in capsys.readouterr().out


def test_cli_build_failure_exits_non_zero(source, tmp_path, capsys):
    edit_json(source / "world.json", lambda d: d.pop("name"))
    assert main(["world", "build", str(source), "--out", str(tmp_path / "out")]) == 1
    assert "no release was written" in capsys.readouterr().out


def test_cli_publish_builds_into_the_data_root(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OPEN_LAB_DATA", str(tmp_path / "data"))
    assert main(["world", "build", str(MINIMAL), "--publish"]) == 0
    assert (tmp_path / "data" / "worlds" / "minimal" / "0.4.0" / MANIFEST_NAME).is_file()


def test_data_root_comes_from_the_environment_or_the_home_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("OPEN_LAB_DATA", str(tmp_path))
    assert data_root() == tmp_path
    monkeypatch.delenv("OPEN_LAB_DATA")
    assert data_root() == Path.home() / "open-lab-data"


def test_capability_examples_mirror_the_world_source():
    pairs = (("text-stats", "text.stats"), ("math-evaluate", "math.evaluate"))
    for example, capability_id in pairs:
        shipped = MINIMAL / "capabilities" / capability_id / "capability.json"
        shown = ROOT / "examples" / "v1" / "capability" / f"{example}.json"
        assert json.loads(shown.read_text(encoding="utf-8")) == json.loads(
            shipped.read_text(encoding="utf-8")
        )


def test_world_release_example_names_what_the_build_produces(release):
    example = json.loads(
        (ROOT / "examples" / "v1" / "world-release" / "minimal-world.json").read_text("utf-8")
    )
    built = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert validate_document(example) == []
    for key in ("world_id", "version", "environment", "default_limits", "default_permissions"):
        assert example[key] == built[key]
    paths = lambda m: sorted(c["manifest_path"] for c in m["capabilities"])  # noqa: E731
    assert paths(example) == paths(built)


def test_health_check_covers_world_sources(source):
    assert health.check_world_sources(ROOT) == []
    worlds = source.parent / "repo" / "worlds"
    worlds.mkdir(parents=True)
    shutil.move(str(source), worlds / "broken")
    edit_json(worlds / "broken" / "world.json", lambda d: d.pop("version"))
    assert health.check_world_sources(worlds.parent) == [
        "worlds/broken: world.json: missing 'version'"
    ]
