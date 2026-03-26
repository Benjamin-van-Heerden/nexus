"""State management for nexus.

State is stored in state.toml and tracks mutable runtime data
like topic selection history.
"""

import tomllib
from dataclasses import dataclass, field
from datetime import date

import tomli_w

from src.utils.paths import get_state_path


@dataclass
class TopicEntry:
    week: date
    topic: str


@dataclass
class LearnState:
    current_topic: str = ""
    current_week: date | None = None
    history: list[TopicEntry] = field(default_factory=list)


@dataclass
class State:
    learn: LearnState = field(default_factory=LearnState)


def load_state() -> State:
    """Load state from state.toml. Returns empty state if file doesn't exist."""
    state_path = get_state_path()
    if not state_path.exists():
        return State()

    with open(state_path, "rb") as f:
        raw = tomllib.load(f)

    learn_raw = raw.get("learn", {})
    history = [
        TopicEntry(week=entry["week"], topic=entry["topic"])
        for entry in learn_raw.get("history", [])
    ]

    current_week = learn_raw.get("current_week")

    return State(
        learn=LearnState(
            current_topic=learn_raw.get("current_topic", ""),
            current_week=current_week,
            history=history,
        )
    )


def save_state(state: State) -> None:
    """Write state to state.toml."""
    state_path = get_state_path()

    data: dict = {
        "learn": {
            "current_topic": state.learn.current_topic,
            "current_week": state.learn.current_week,
            "history": [
                {"week": entry.week, "topic": entry.topic}
                for entry in state.learn.history
            ],
        }
    }

    with open(state_path, "wb") as f:
        tomli_w.dump(data, f)
