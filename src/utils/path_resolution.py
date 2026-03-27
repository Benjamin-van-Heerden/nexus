"""Path resolution utilities.

All paths in TOML files are stored relative to the project root.
This module provides functions to resolve them to absolute paths
for display and agent consumption.
"""

from pathlib import Path

from src.utils.paths import get_project_root


def resolve(relative_path: str | Path) -> Path:
    """Resolve a path relative to the nexus project root to an absolute path."""
    return (get_project_root() / relative_path).resolve()


def resolve_str(relative_path: str | Path) -> str:
    """Resolve a relative path and return as string."""
    return str(resolve(relative_path))
