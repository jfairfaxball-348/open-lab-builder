"""Release discovery data is reproducible and useful on fixed vocabulary."""
import json

import pytest

from conftest import ROOT
from open_lab_builder.capabilities.registry import build_index, documentation, search, tokens
from open_lab_builder.worlds import build_world, load_source

SOURCE = ROOT / "worlds" / "minimal"


@pytest.fixture
def manifests():
    return [c.manifest for c in load_source(SOURCE).capabilities]


@pytest.mark.parametrize("query, expected", [
    ("count words", "text.stats"), ("arithmetic fractions", "math.evaluate"),
    ("save notes", "workspace.write"), ("browse folder", "workspace.list"),
    ("current UTC clock", "time.now"), ("WORKSPACE.WRITE", "workspace.write"),
])
def test_fixed_query_relevance(manifests, query, expected):
    assert search(build_index(manifests), query)[0]["id"] == expected


def test_tokenization_filters_limits_and_empty_queries(manifests):
    index = build_index(manifests)
    assert tokens("CAFÉ café workspace.write foo_bar") == [
        "bar", "café", "foo", "workspace", "write"
    ]
    assert search(index, "?!") == search(index, "unfindable") == []
    assert search(index, "write", category="time") == []
    assert len(search(index, "workspace", category="workspace", limit=1)) == 1
    assert search(index, "workspace", limit=0) == []
    assert search(index, "write write") == search(index, "write")
    index["format_version"] = "99.0.0"
    with pytest.raises(ValueError, match="unsupported"):
        search(index, "write")


def test_order_is_independent_of_input_and_ties_use_id(manifests):
    assert build_index(manifests) == build_index(list(reversed(manifests)))
    first = dict(manifests[0], id="a.tool", name="same", summary="uniquequery")
    second = dict(first, id="b.tool")
    index = build_index([second, first])
    assert [r["id"] for r in search(index, "uniquequery")] == ["a.tool", "b.tool"]


def test_documentation_preserves_every_manifest_section(manifests):
    # Include all optional sections, even ones absent from the minimal world.
    manifest = dict(manifests[0], dependencies={"capabilities": ["text.stats"]},
                    extensions={"example": {"nested": ["value"]}})
    rendered = documentation(manifest)
    sections = rendered.split("\n\n## ")[1:]
    recovered = {}
    for section in sections:
        key, body = section.split("\n\n", 1)
        body = body.rstrip("\n")
        recovered[key] = body if isinstance(manifest[key], str) else json.loads(body)
    assert recovered == manifest
    assert documentation(dict(reversed(list(manifest.items())))) == rendered


def test_generated_release_bytes_and_digest_are_deterministic(tmp_path):
    first = build_world(SOURCE, tmp_path / "one")
    second = build_world(SOURCE, tmp_path / "two")
    assert first.manifest["content_digest"] == second.manifest["content_digest"]
    for path in (first.release_dir / "registry").rglob("*"):
        if path.is_file():
            relative = path.relative_to(first.release_dir)
            assert path.read_bytes() == (second.release_dir / relative).read_bytes()
            assert relative.as_posix() in {
                f["path"] for f in first.manifest["extensions"]["files"]
            }
    index = json.loads((first.release_dir / "registry/index.json").read_text())
    assert len(index["capabilities"]) == 11
    for capability in load_source(SOURCE).capabilities:
        path = first.release_dir / "registry/docs" / f"{capability.manifest['id']}.txt"
        assert path.read_bytes() == documentation(capability.manifest).encode("utf-8")
