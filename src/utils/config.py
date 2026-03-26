"""Config loading for nexus."""

import tomllib
from dataclasses import dataclass

from src.utils.paths import get_config_path


@dataclass
class LearnConfig:
    window_size: int
    weights: dict[str, int]


@dataclass
class SelfImprovementGoals:
    exercise_sessions_per_week: int
    reading_sessions_per_week: int


@dataclass
class Config:
    learn: LearnConfig
    self_improvement_goals: SelfImprovementGoals


def load_config() -> Config:
    """Load and parse config.toml."""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    learn = raw["learn"]
    si = raw.get("self-improvement", {}).get("goals", {})

    return Config(
        learn=LearnConfig(
            window_size=learn["window_size"],
            weights=learn["weights"],
        ),
        self_improvement_goals=SelfImprovementGoals(
            exercise_sessions_per_week=si.get("exercise_sessions_per_week", 4),
            reading_sessions_per_week=si.get("reading_sessions_per_week", 5),
        ),
    )
