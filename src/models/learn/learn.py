"""Top-level learn configuration model.

Maps to: learn/learn.toml
"""

from datetime import date

from pydantic import BaseModel


class TopicEntry(BaseModel):
    week: date
    topic: str


class TopicWeight(BaseModel):
    name: str
    weight: int = 1
    active: bool = True


class LearnConfig(BaseModel):
    topics: list[TopicWeight] = []
    current_topic: str = ""
    history: list[TopicEntry] = []

    def active_weights(self) -> dict[str, int]:
        return {t.name: t.weight for t in self.topics if t.active}

    def all_weights(self) -> dict[str, int]:
        return {t.name: t.weight for t in self.topics}
