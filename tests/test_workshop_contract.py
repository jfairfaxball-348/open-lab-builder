"""Scientific image identity is part of the verified release, not tool input."""

import json
from pathlib import Path

import pytest

from open_lab_builder.contracts import validate_document
from open_lab_builder.worlds.release import build_world, content_digest, digest_files

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples/v1/world-release/workshop-world.json"


@pytest.mark.parametrize("image", ["latest", "localhost/w:tag", "../x", "sha256:abc",
                                   "sha256:" + "A" * 64, "sha256:" + "a" * 64 + "\n"])
def test_only_immutable_image_ids_are_valid(image):
    document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    document["environment"]["container_image"] = image
    assert validate_document(document)


def test_image_binding_needs_container_and_new_schema():
    document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert validate_document(document) == []
    document["environment"]["isolation"]["minimum_tier"] = "process"
    assert validate_document(document)
    document["environment"]["isolation"]["minimum_tier"] = "container"
    document["schema_version"] = "1.0.0"
    assert validate_document(document)


def test_built_release_binds_selected_image(tmp_path):
    result = build_world(ROOT / "worlds/habitat", tmp_path)
    manifest = result.manifest
    assert manifest["schema_version"] == "1.1.0"
    assert manifest["environment"]["container_image"].startswith("sha256:")
    before = manifest["content_digest"]["value"]
    manifest["environment"]["container_image"] = "sha256:" + "0" * 64
    assert content_digest(digest_files(result.release_dir), manifest) != before
