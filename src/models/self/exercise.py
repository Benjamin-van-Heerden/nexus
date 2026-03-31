from datetime import date
from typing import Literal

from pydantic import BaseModel


class ExerciseSession(BaseModel):
    date: date
    type: str
    description: str
    intensity: Literal["easy", "moderate", "hard"]
    duration_minutes: int


class ExerciseLog(BaseModel):
    sessions: list[ExerciseSession] = []
