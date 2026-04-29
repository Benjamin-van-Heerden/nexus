"""Daily news digest model.

Maps to: news/records/YYYY-MM-DD.toml
"""

from datetime import date

from pydantic import BaseModel


class PerspectiveEntry(BaseModel):
    lean: str
    source: str
    summary: str


class StoryCluster(BaseModel):
    slug: str
    headline: str
    category: str
    summary: str
    perspectives: list[PerspectiveEntry] = []
    tracked_story: str | None = None
    sources_count: int = 1


class TrackedStoryUpdate(BaseModel):
    slug: str
    headline: str
    development: str


class DailyDigest(BaseModel):
    date: date
    generated_at: str
    story_clusters: list[StoryCluster] = []
    x_trending_global: str = ""
    x_trending_sa: str = ""
    tracked_story_updates: list[TrackedStoryUpdate] = []
