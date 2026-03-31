from datetime import date
from typing import Literal

from pydantic import BaseModel


class ReadingSession(BaseModel):
    date: date
    section: str
    summary: str
    takeaway: str
    agent_questions: list[str] = []


class BookConfig(BaseModel):
    name: str
    author: str
    slug: str
    started: date
    status: Literal["active", "completed"] = "active"
    current_section: str = ""
    total_sections: str = ""
    sessions: list[ReadingSession] = []
