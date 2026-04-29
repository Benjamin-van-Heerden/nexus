"""News system utilities.

Handles TOML I/O for news config/records/stories, slug helpers,
and RSS feed fetching.
"""

import asyncio
import re
import tomllib
from datetime import date, datetime
from pathlib import Path

import feedparser
import httpx
import tomli_w

from src.models.news.config import NewsConfig, SourceEntry
from src.models.news.digest import DailyDigest
from src.models.news.story import TrackedStory
from src.utils.paths import get_news_dir

# -- Path helpers --


def get_news_config_path() -> Path:
    return get_news_dir() / "config.toml"


def get_records_dir() -> Path:
    return get_news_dir() / "records"


def get_stories_dir() -> Path:
    return get_news_dir() / "stories"


def get_record_path(day: date) -> Path:
    return get_records_dir() / f"{day.isoformat()}.toml"


def get_story_path(slug: str) -> Path:
    return get_stories_dir() / f"{slug}.toml"


# -- TOML I/O --


def _load_toml(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _save_toml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(data, f, multiline_strings=True)


# -- News config --


def load_news_config() -> NewsConfig:
    raw = _load_toml(get_news_config_path())
    return NewsConfig(**raw)


def save_news_config(config: NewsConfig) -> None:
    _save_toml(
        get_news_config_path(), config.model_dump(mode="json", exclude_none=True)
    )


# -- Daily digests --


def load_daily_digest(day: date) -> DailyDigest | None:
    path = get_record_path(day)
    if not path.exists():
        return None
    return DailyDigest(**_load_toml(path))


def save_daily_digest(digest: DailyDigest) -> None:
    _save_toml(
        get_record_path(digest.date),
        digest.model_dump(mode="json", exclude_none=True),
    )


def load_recent_records(n: int = 3) -> list[DailyDigest]:
    paths = sorted(get_records_dir().glob("*.toml"), reverse=True)
    records: list[DailyDigest] = []
    for path in paths:
        if len(records) >= n:
            break
        try:
            records.append(DailyDigest(**_load_toml(path)))
        except Exception:
            continue
    return records


# -- Tracked stories --


def load_tracked_story(slug: str) -> TrackedStory:
    path = get_story_path(slug)
    if not path.exists():
        raise FileNotFoundError(f"Tracked story not found: '{slug}'")
    return TrackedStory(**_load_toml(path))


def save_tracked_story(story: TrackedStory) -> None:
    _save_toml(
        get_story_path(story.slug),
        story.model_dump(mode="json", exclude_none=True),
    )


def list_tracked_stories(active_only: bool = False) -> list[TrackedStory]:
    stories: list[TrackedStory] = []
    for path in sorted(get_stories_dir().glob("*.toml")):
        try:
            story = TrackedStory(**_load_toml(path))
        except Exception:
            continue
        if active_only and not story.active:
            continue
        stories.append(story)
    return stories


# -- Slug helper --


def slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


# -- RSS fetching --


def _parse_entry_date(entry: feedparser.FeedParserDict) -> str:
    for field in ("published", "updated", "created"):
        value = entry.get(field)
        if value:
            return str(value)
    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if struct:
        try:
            return datetime(*struct[:6]).isoformat()
        except (TypeError, ValueError):
            pass
    return ""


async def _fetch_one_feed(
    client: httpx.AsyncClient, source: SourceEntry
) -> list[dict]:
    try:
        resp = await client.get(
            source.url, timeout=15.0, follow_redirects=True, headers={"User-Agent": "nexus-news/0.1"}
        )
        resp.raise_for_status()
    except Exception as exc:
        print(f"  [warn] {source.name}: fetch failed ({exc})")
        return []

    parsed = feedparser.parse(resp.content)
    if parsed.bozo and not parsed.entries:
        reason = getattr(parsed, "bozo_exception", "unknown parse error")
        print(f"  [warn] {source.name}: parse failed ({reason})")
        return []

    headlines = []
    for entry in parsed.entries:
        title = entry.get("title", "").strip()
        if not title:
            continue
        headlines.append(
            {
                "title": title,
                "source_name": source.name,
                "source_lean": source.lean,
                "link": entry.get("link", ""),
                "published": _parse_entry_date(entry),
                "category": source.category,
                "summary": entry.get("summary", "").strip(),
            }
        )
    return headlines


async def fetch_all_feeds(sources: list[SourceEntry]) -> list[dict]:
    if not sources:
        return []
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(_fetch_one_feed(client, s) for s in sources),
            return_exceptions=False,
        )
    headlines: list[dict] = []
    for batch in results:
        headlines.extend(batch)
    return headlines


def fetch_all_feeds_sync(sources: list[SourceEntry]) -> list[dict]:
    return asyncio.run(fetch_all_feeds(sources))
