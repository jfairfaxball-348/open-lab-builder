"""Validate the small, immutable text library before packaging a world."""

import hashlib
import json
import re
from pathlib import Path

MAX_FILE = 256 * 1024
MAX_TOTAL = 2 * 1024 * 1024
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SOURCE_FIELDS = {"id", "title", "citation", "url", "revision", "license", "license_url",
                 "path", "notice", "sha256"}


def validate_library(root: Path) -> list[str]:
    try:
        if root.is_symlink() or root.is_junction():
            raise ValueError("library links are forbidden")
        total = 0
        for path in root.rglob("*"):
            if path.is_symlink() or path.is_junction():
                raise ValueError("library links are forbidden")
            if path.is_file():
                total += path.stat().st_size
                if path.stat().st_size > MAX_FILE or total > MAX_TOTAL:
                    raise ValueError("library size limit exceeded")
                if path.suffix not in {".txt", ".csv", ".json"}:
                    raise ValueError("library accepts text, CSV and catalog JSON only")
                path.read_text(encoding="utf-8")
        catalog = json.loads((root / "index.json").read_text(encoding="utf-8"))
        if (set(catalog) != {"format_version", "sources"}
                or catalog.get("format_version") != "1.0.0"
                or not isinstance(catalog["sources"], list)
                or not 1 <= len(catalog["sources"]) <= 32):
            raise ValueError("unsupported library catalog")
        seen = set()
        for entry in catalog["sources"]:
            if set(entry) != SOURCE_FIELDS:
                raise ValueError("unsupported library source fields")
            ident = entry["id"]
            if not SLUG.fullmatch(ident) or ident in seen:
                raise ValueError("invalid/duplicate library id")
            seen.add(ident)
            for key in ("title", "citation", "url", "revision", "license", "license_url"):
                if not isinstance(entry[key], str) or not entry[key]:
                    raise ValueError("missing source provenance")
            for key in ("path", "notice"):
                name = entry[key]
                if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]*\.(?:txt|csv)", name):
                    raise ValueError("library file must be a simple relative text name")
                if not (root / name).is_file():
                    raise ValueError("missing library file")
            actual = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
            if actual != entry["sha256"]:
                raise ValueError("library source hash mismatch")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        return [f"library: {error}"]
    return []
