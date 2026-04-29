"""Path resolution for nexus project."""

from pathlib import Path


def get_project_root() -> Path:
    """Get the nexus project root directory.

    Walks up from this file to find the directory containing config.toml.
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "config.toml").exists():
            return parent
    raise FileNotFoundError("Could not find nexus project root (no config.toml found)")


def get_config_path() -> Path:
    return get_project_root() / "config.toml"


def get_state_path() -> Path:
    return get_project_root() / "state.toml"


def get_learn_dir() -> Path:
    return get_project_root() / "learn"


def get_self_dir() -> Path:
    return get_project_root() / "self"


def get_manage_dir() -> Path:
    return get_project_root() / "manage"


def get_archive_dir() -> Path:
    return get_project_root() / "archive"
