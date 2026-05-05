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
    xai_model: str = "grok-4.3"
    synthesis_model: str = "grok-4.3"
    history_days: int = 3
    max_entries_per_source: int = 30
    max_total_entries: int = 250
    max_entry_age_hours: int = 72
    editorial_profile: str = ""
    categories: list[str] = [
        "science",
        "technology",
        "economics",
        "us_politics",
        "international",
        "entertainment",
        "sa_local",
    ]
