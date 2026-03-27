"""Learn system traversal utilities.

Handles loading and saving TOML files at each level of the learn hierarchy:
  learn.toml → topic.toml → subtopic.toml → phase.toml
"""

import tomllib
from pathlib import Path

import tomli_w

from src.models.learn.learn import LearnConfig
from src.models.learn.phase import Goal, PhaseConfig
from src.models.learn.subtopic import SubtopicConfig
from src.models.learn.topic import TopicConfig
from src.utils.paths import get_learn_dir


def _load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _save_toml(path: Path, data: dict) -> None:
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


# -- Load models --


def load_learn_config() -> LearnConfig:
    path = get_learn_dir() / "learn.toml"
    raw = _load_toml(path)
    return LearnConfig(**raw)


def load_topic_config(topic: str) -> TopicConfig:
    path = get_learn_dir() / topic / "topic.toml"
    return TopicConfig(**_load_toml(path))


def load_subtopic_config(topic: str, subtopic: str) -> SubtopicConfig:
    path = get_learn_dir() / topic / subtopic / "subtopic.toml"
    return SubtopicConfig(**_load_toml(path))


def load_phase_config(topic: str, subtopic: str, phase: str) -> PhaseConfig:
    path = get_learn_dir() / topic / subtopic / phase / "phase.toml"
    return PhaseConfig(**_load_toml(path))


# -- Save models --


def save_learn_config(config: LearnConfig) -> None:
    path = get_learn_dir() / "learn.toml"
    _save_toml(path, config.model_dump(mode="json"))


def save_subtopic_config(topic: str, subtopic: str, config: SubtopicConfig) -> None:
    path = get_learn_dir() / topic / subtopic / "subtopic.toml"
    _save_toml(path, config.model_dump(mode="json"))


def save_phase_config(
    topic: str, subtopic: str, phase: str, config: PhaseConfig
) -> None:
    path = get_learn_dir() / topic / subtopic / phase / "phase.toml"
    _save_toml(path, config.model_dump(mode="json"))


# -- Traversal helpers --


def get_active_context() -> (
    tuple[str, TopicConfig, str, SubtopicConfig, str, PhaseConfig] | None
):
    """Walk the full hierarchy and return the active context.

    Returns (topic_name, topic_config, subtopic_name, subtopic_config, phase_name, phase_config)
    or None if no topic is set.
    """
    learn = load_learn_config()
    if not learn.current_topic:
        return None

    topic_name = learn.current_topic
    topic = load_topic_config(topic_name)

    if not topic.current_subtopic:
        return None

    subtopic_name = topic.current_subtopic
    subtopic = load_subtopic_config(topic_name, subtopic_name)

    if not subtopic.current_phase:
        return None

    phase_name = subtopic.current_phase
    phase = load_phase_config(topic_name, subtopic_name, phase_name)

    return (topic_name, topic, subtopic_name, subtopic, phase_name, phase)


def get_topic_dir(topic: str) -> Path:
    return get_learn_dir() / topic


def get_subtopic_dir(topic: str, subtopic: str) -> Path:
    return get_learn_dir() / topic / subtopic


def get_phase_dir(topic: str, subtopic: str, phase: str) -> Path:
    return get_learn_dir() / topic / subtopic / phase


def get_records_dir(topic: str, subtopic: str, phase: str) -> Path:
    return get_phase_dir(topic, subtopic, phase) / "records"


def get_current_goal(phase_cfg: PhaseConfig) -> Goal | None:
    """Get the current goal from a phase config."""
    if not phase_cfg.current_goal:
        return None
    for goal in phase_cfg.goals:
        if goal.name == phase_cfg.current_goal:
            return goal
    return None
