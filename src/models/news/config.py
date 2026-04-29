"""News configuration model.

Maps to: news/config.toml
"""

from pydantic import BaseModel


class SourceEntry(BaseModel):
    name: str
    url: str
    category: str
    lean: str = "center"


class NewsConfig(BaseModel):
    sources: list[SourceEntry] = []
    xai_model: str = "grok-4.20-reasoning"
    synthesis_model: str = "grok-4.20-reasoning"
    history_days: int = 3
    categories: list[str] = [
        "science",
        "technology",
        "economics",
        "us_politics",
        "international",
        "entertainment",
        "sa_local",
    ]
