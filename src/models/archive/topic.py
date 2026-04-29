"""Topic configuration model.

Maps to: archive/topics/<slug>.toml
"""

from datetime import date

from pydantic import BaseModel


class TopicMember(BaseModel):
    slug: str
    hook: str = ""


class TopicConfig(BaseModel):
    slug: str
    title: str
    summary: str
    parent: str | None = None
    related: list[str] = []
    created: date
    updated: date
    last_maintained: date | None = None
    docs: list[TopicMember] = []
