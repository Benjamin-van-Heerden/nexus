"""Phase configuration model.

Maps to: learn/<topic>/<subtopic>/<phase>/phase.toml
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel


class Task(BaseModel):
    name: str
    type: Literal["practical", "theoretical", "quiz"]
    created: date
    status: Literal["todo", "completed"] = "todo"
    completed: date | None = None
    relevant_files: list[str] = []


class Goal(BaseModel):
    name: str
    reference: str
    status: Literal["todo", "in_progress", "completed"] = "todo"
    tasks: list[Task] = []


class PhaseConfig(BaseModel):
    name: str
    current_goal: str = ""
    goals: list[Goal] = []
