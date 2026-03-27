"""Subtopic configuration model.

Maps to: learn/<topic>/<subtopic>/subtopic.toml
"""

from typing import Literal

from pydantic import BaseModel


class ExerciseTypeConfig(BaseModel):
    description: str = ""


class PhaseEntry(BaseModel):
    name: str
    status: Literal["todo", "in_progress", "completed"] = "todo"


class SubtopicConfig(BaseModel):
    name: str
    current_phase: str = ""
    reference: str = ""
    practical: ExerciseTypeConfig = ExerciseTypeConfig()
    theoretical: ExerciseTypeConfig = ExerciseTypeConfig()
    quiz: ExerciseTypeConfig = ExerciseTypeConfig()
    phases: list[PhaseEntry] = []
