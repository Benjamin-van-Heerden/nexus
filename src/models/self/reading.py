from datetime import date
from typing import Literal

from pydantic import BaseModel


class ReadingSession(BaseModel):
    date: date
    description: str
    summary: str
    takeaway: str


class BookConfig(BaseModel):
    name: str
    author: str
    slug: str
    started: date
    status: Literal["active", "completed"] = "active"
    completion_summary: str = ""
    completion_takeaway: str = ""
    sessions: list[ReadingSession] = []
