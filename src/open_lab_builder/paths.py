"""Locating the repository and its contract schemas."""

from __future__ import annotations

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent


def repo_root() -> Path | None:
    """Return the source checkout root, or None if the package is not in a checkout."""
    candidate = _PACKAGE_DIR.parent.parent
    if (candidate / "pyproject.toml").is_file() and (candidate / "schemas").is_dir():
        return candidate
    return None


def schemas_dir() -> Path:
    """Return the directory holding the ``v<major>/`` schema folders."""
    root = repo_root()
    if root is None:
        raise FileNotFoundError(
            "Contract schemas not found. The builder runs from a source checkout; other "
            "components read the schemas bundled inside a world release."
        )
    return root / "schemas"
