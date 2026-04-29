"""Pause system utilities."""

from datetime import date
from typing import Literal

import tomli_w

from src.models.pause import PauseConfig, PauseEntry
from src.utils.paths import get_project_root


def get_pause_config_path():
    return get_project_root() / "pause.toml"


def load_pause_config() -> PauseConfig:
    path = get_pause_config_path()
    if not path.exists() or path.stat().st_size == 0:
        return PauseConfig()
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)
    return PauseConfig(**data)


def save_pause_config(config: PauseConfig) -> None:
    path = get_pause_config_path()
    with open(path, "wb") as f:
        tomli_w.dump(config.model_dump(mode="json", exclude_none=True), f)


def check_pause(feature: Literal["learn", "self", "manage", "archive", "news"]) -> PauseEntry | None:
    config = load_pause_config()
    entry = getattr(config, feature)

    if not entry.active:
        return None

    if entry.resume_date and entry.resume_date <= date.today():
        entry.active = False
        save_pause_config(config)
        return None

    return entry


def pause_feature(
    feature: Literal["learn", "self", "manage", "archive", "news"],
    resume_date: date,
    reason: str | None = None,
) -> None:
    config = load_pause_config()
    entry = getattr(config, feature)
    entry.active = True
    entry.resume_date = resume_date
    entry.reason = reason
    save_pause_config(config)


def resume_feature(feature: Literal["learn", "self", "manage", "archive", "news"]) -> None:
    config = load_pause_config()
    entry = getattr(config, feature)
    entry.active = False
    entry.resume_date = None
    entry.reason = None
    save_pause_config(config)
