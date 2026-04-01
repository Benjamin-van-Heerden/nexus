"""Manage index models.

Maps to: manage/index.toml
"""

from datetime import date, datetime

from pydantic import BaseModel


class IndexEntry(BaseModel):
    slug: str
    name: str
    path: str
    due: datetime | date | None = None
    parent: str = ""


class ManageIndex(BaseModel):
    tasks: list[IndexEntry] = []
