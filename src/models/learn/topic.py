"""Topic configuration model.

Maps to: learn/<topic>/topic.toml
"""

from pydantic import BaseModel


class TopicConfig(BaseModel):
    name: str
    current_subtopic: str = ""
