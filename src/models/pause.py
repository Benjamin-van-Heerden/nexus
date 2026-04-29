"""Pause configuration model.

Maps to: pause.toml
"""

from datetime import date

from pydantic import BaseModel


class PauseEntry(BaseModel):
    active: bool = False
    resume_date: date | None = None
    reason: str | None = None


class PauseConfig(BaseModel):
    learn: PauseEntry = PauseEntry()
    self: PauseEntry = PauseEntry()
    manage: PauseEntry = PauseEntry()
    archive: PauseEntry = PauseEntry()
    news: PauseEntry = PauseEntry()
