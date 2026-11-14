"""Deterministic release catalogue and keyword search; no runtime integration."""

from __future__ import annotations

import json
import re
from typing import Any

INDEX_PATH = "registry/index.json"
FORMAT_VERSION = "1.0.0"
WEIGHTS = {"id": 8, "name": 6, "keywords": 5, "categories": 4,
           "summary": 3, "description": 1}


def tokens(text: str) -> list[str]:
    """Unique Unicode alphanumeric words, case folded, sorted; no stemming."""
    return sorted(set(re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)))


def documentation(manifest: dict[str, Any]) -> str:
    """Render every present manifest field, including optional and extension fields.

    JSON sections preserve exact schema constraints and demonstration values;
    prose strings remain directly readable. Sorted fields make bytes stable.
    """
    sections = [f"# {manifest['name']} ({manifest['id']})"]
    for key, value in sorted(manifest.items()):
        body = value if isinstance(value, str) else json.dumps(
            value, indent=2, sort_keys=True, ensure_ascii=False
        )
        sections.append(f"## {key}\n\n{body}")
    return "\n\n".join(sections) + "\n"


def build_index(manifests: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for manifest in sorted(manifests, key=lambda m: m["id"]):
        fields = {}
        for key in WEIGHTS:
            value = manifest.get(key, "")
            fields[key] = tokens(" ".join(value) if isinstance(value, list) else value)
        entries.append({
            **{key: manifest[key] for key in ("id", "name", "summary", "categories")},
            "keywords": manifest.get("keywords", []),
            "documentation_path": f"registry/docs/{manifest['id']}.txt",
            "tokens": fields,
        })
    return {"format_version": FORMAT_VERSION, "capabilities": entries}


def search(index: dict[str, Any], query: str, *, category: str | None = None,
           limit: int = 10) -> list[dict[str, Any]]:
    """Rank OR matches by weighted token presence; ties sort by capability id.

    Repeated query words count once. Categories filter by exact slug. Empty
    queries, no matches and non-positive limits return no results.
    """
    if index["format_version"] != FORMAT_VERSION:
        raise ValueError("unsupported registry format version")
    wanted = set(tokens(query))
    matches = []
    for entry in index["capabilities"]:
        if category is not None and category not in entry["categories"]:
            continue
        score = sum(weight * len(wanted.intersection(entry["tokens"][key]))
                    for key, weight in WEIGHTS.items())
        if score:
            matches.append({**entry, "score": score})
    return sorted(matches, key=lambda m: (-m["score"], m["id"]))[:max(0, limit)]
