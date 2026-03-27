"""Phase configuration model.

Maps to: learn/<topic>/<subtopic>/<phase>/phase.toml
"""

from typing import Literal

from pydantic import BaseModel


class Task(BaseModel):
    name: str
    type: Literal["practical", "theoretical", "quiz"]
    status: Literal["todo", "completed"] = "todo"


class Goal(BaseModel):
    name: str
    status: Literal["todo", "in_progress", "completed"] = "todo"
    reference: str = ""
    tasks: list[Task] = []


class PhaseConfig(BaseModel):
    name: str
    current_goal: str = ""
    goals: list[Goal] = []
