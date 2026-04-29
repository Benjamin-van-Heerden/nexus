"""Generated archive index model.

Maps to: archive/index.toml (auto-generated, never hand-edited)
"""

from datetime import datetime

from pydantic import BaseModel


class IndexTopicEntry(BaseModel):
    slug: str
    summary_line: str
    doc_count: int
    parent: str | None = None
    related: list[str] = []
    children: list[str] = []


class IndexFile(BaseModel):
    generated: datetime
    doc_count: int = 0
    topic_count: int = 0
    pending_outputs: int = 0
    orphan_count: int = 0
    stale_count: int = 0
    broken_link_count: int = 0
    topics: list[IndexTopicEntry] = []
