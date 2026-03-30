"""Path resolution utilities.

All paths in TOML files are stored relative to the project root
with a ./ prefix (e.g. ./learn/jax/reference/doc.md). This module
provides functions to resolve them to absolute paths for display,
and to create ./ prefixed paths for storage.
"""

from pathlib import Path

from src.utils.paths import get_project_root


def resolve(stored_path: str | Path) -> Path:
    """Resolve a ./ prefixed path to an absolute path.

    Handles both ./learn/... (stored convention) and bare paths like learn/...
    for backwards compatibility.
    """
    path_str = str(stored_path)
    if path_str.startswith("./"):
        path_str = path_str[2:]
    return (get_project_root() / path_str).resolve()


def resolve_str(stored_path: str | Path) -> str:
    """Resolve a stored path and return as string."""
    return str(resolve(stored_path))


def to_stored_path(absolute_or_relative: str | Path) -> str:
    """Convert any path to the ./ prefixed storage convention.

    Accepts absolute paths or paths relative to the project root.
    Returns a ./ prefixed path relative to the project root.
    """
    path = Path(absolute_or_relative)
    if path.is_absolute():
        try:
            rel = path.relative_to(get_project_root())
            return f"./{rel}"
        except ValueError:
            raise ValueError(f"Path {path} is not under the project root")
    path_str = str(path)
    if path_str.startswith("./"):
        return path_str
    return f"./{path_str}"
