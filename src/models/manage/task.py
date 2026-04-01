"""Task configuration model.

Maps to: manage/tasks/<slug>.toml
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class TaskConfig(BaseModel):
    name: str
    slug: str
    description: str = ""
    status: Literal["todo", "in_progress", "completed"] = "todo"
    created: date = date.today()
    due: datetime | date | None = None
    completed_at: date | None = None
    tags: list[str] = []
    recurrence: str = ""
    gcal_event_id: str = ""
    last_modified: datetime = datetime.now()
    has_subtasks: bool = False
    parent: str = ""
