from datetime import date

from pydantic import BaseModel


class LearningSession(BaseModel):
    date: date
    did_learn: bool
    notes: str = ""


class LearningLog(BaseModel):
    sessions: list[LearningSession] = []
