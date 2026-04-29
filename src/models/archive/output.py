"""Output (synthesis) frontmatter model.

Maps to: archive/outputs/<slug>.md (YAML frontmatter block)
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel

OutputStatus = Literal["pending_review", "integrated", "archived"]


class OutputFrontmatter(BaseModel):
    slug: str
    query: str
    created: date
    status: OutputStatus = "pending_review"
    cites: list[str] = []
    novelty: str = ""
