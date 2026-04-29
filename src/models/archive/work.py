"""Work queue models.

Maps to: archive/work.toml
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

WorkKind = Literal[
    "broken_link",
    "pending_output",
    "orphan",
    "stale",
    "contradiction",
    "needs_topic_review",
]


class WorkItem(BaseModel):
    kind: WorkKind
    slug: str
    detail: str = ""
    created: datetime


class WorkQueue(BaseModel):
    items: list[WorkItem] = []
