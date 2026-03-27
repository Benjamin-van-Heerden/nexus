"""Top-level learn configuration model.

Maps to: learn/learn.toml
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel


class TopicEntry(BaseModel):
    week: date
    topic: str


class LearnConfig(BaseModel):
    window_size: int = 8
    current_topic: str = ""
    weights: dict[str, int]
    history: list[TopicEntry] = []
