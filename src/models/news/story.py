"""Tracked story model.

Maps to: news/stories/<slug>.toml
"""

from datetime import date

from pydantic import BaseModel


class TrackedStory(BaseModel):
    slug: str
    description: str
    created: date
    last_updated: date | None = None
    developments: list[str] = []
    active: bool = True
