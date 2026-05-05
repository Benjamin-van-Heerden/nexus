"""News system utilities.

Handles TOML I/O for news config/records/stories, slug helpers,
and RSS feed fetching.
"""

import asyncio
import re
import tomllib
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import httpx
import tomli_w
from pydantic import BaseModel
from xai_sdk import Client as XAIClient
from xai_sdk.chat import system, user
from xai_sdk.tools import web_search, x_search

from env_settings import ENV_SETTINGS
from src.models.news.config import NewsConfig, SourceEntry
from src.models.news.digest import (
    DailyDigest,
    StoryCluster,
    TrackedStoryUpdate,
)
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


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _parse_datetime_string(value: str) -> datetime | None:
    try:
        return _normalize_datetime(parsedate_to_datetime(value))
    except (TypeError, ValueError):
        pass
    try:
        return _normalize_datetime(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except ValueError:
        return None


def _parse_entry_datetime(entry: feedparser.FeedParserDict) -> datetime | None:
    for field in ("published", "updated", "created"):
        value = entry.get(field)
        if value:
            parsed = _parse_datetime_string(str(value))
            if parsed is not None:
                return parsed
    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if struct:
        try:
            return datetime(*struct[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return None
    return None


async def _fetch_one_feed(
    client: httpx.AsyncClient,
    source: SourceEntry,
    max_entries: int,
    cutoff: datetime | None,
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
        published_at = _parse_entry_datetime(entry)
        if cutoff is not None and published_at is not None and published_at < cutoff:
            continue

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
        if max_entries > 0 and len(headlines) >= max_entries:
            break
    return headlines


async def fetch_all_feeds(
    sources: list[SourceEntry],
    max_entries_per_source: int = 30,
    max_total_entries: int = 250,
    max_entry_age_hours: int = 72,
) -> list[dict]:
    if not sources:
        return []
    cutoff = None
    if max_entry_age_hours > 0:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_entry_age_hours)
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(
                _fetch_one_feed(
                    client,
                    s,
                    max_entries=max_entries_per_source,
                    cutoff=cutoff,
                )
                for s in sources
            ),
            return_exceptions=False,
        )
    headlines: list[dict] = []
    for batch in results:
        headlines.extend(batch)
        if max_total_entries > 0 and len(headlines) >= max_total_entries:
            return headlines[:max_total_entries]
    return headlines


def fetch_all_feeds_sync(
    sources: list[SourceEntry],
    max_entries_per_source: int = 30,
    max_total_entries: int = 250,
    max_entry_age_hours: int = 72,
) -> list[dict]:
    return asyncio.run(
        fetch_all_feeds(
            sources,
            max_entries_per_source=max_entries_per_source,
            max_total_entries=max_total_entries,
            max_entry_age_hours=max_entry_age_hours,
        )
    )


# -- xAI integration --


def _get_xai_client() -> XAIClient:
    return XAIClient(api_key=ENV_SETTINGS.xai_api_key)


_X_GLOBAL_PROMPT = (
    "You are a news desk researcher. Use X Search to find what is happening "
    "globally right now. Look at the last 24 hours.\n\n"
    "Cover: world politics, geopolitics, US politics, economics, science, "
    "technology, entertainment, and any conspiracy theories or fringe topics "
    "gaining traction.\n\n"
    "Return a compact summary organized by topic. For each major story:\n"
    "- a one-line factual headline\n"
    "- 2-3 bullets describing what is being said and which accounts or "
    "communities are driving it\n"
    "- note if there is meaningful disagreement between camps\n\n"
    "Do not speculate. Report only what is actually being said. Avoid "
    "marketing language and editorializing. Skip stories with no real "
    "engagement."
)


_X_LOCAL_PROMPT_TEMPLATE = (
    "You are a news desk researcher. Use X Search to find what is happening "
    "in {region} right now. Look at the last 24 hours.\n\n"
    "Cover: politics, economics, social issues, crime and safety, business, "
    "sports, entertainment, and any major events being discussed locally.\n\n"
    "Return a compact summary organized by topic. For each major story:\n"
    "- a one-line factual headline\n"
    "- 2-3 bullets describing what is being said and which accounts or "
    "communities are driving it\n\n"
    "Do not speculate. Report only what is actually being said. Skip stories "
    "that are purely global news without a local angle."
)


_WEB_GAPS_PROMPT = (
    "You are a news desk researcher. Use Web Search to find important news "
    "from the last 24 hours that mainstream wire feeds may underreport.\n\n"
    "Focus on:\n"
    "- breaking events that are still developing\n"
    "- international stories under-covered by US-centric media\n"
    "- significant developments in science, technology, and economics\n"
    "- long-running stories that had a meaningful update today\n\n"
    "Return a compact summary organized by category. For each story:\n"
    "- a one-line factual headline\n"
    "- 2-3 bullets with the key facts and the most authoritative source\n\n"
    "Skip celebrity gossip, listicles, and SEO filler. Be terse."
)


def _format_tracked_topics_for_search(stories: list[TrackedStory]) -> str:
    active = [s for s in stories if s.active]
    if not active:
        return ""
    lines = [
        "",
        "Also explicitly check for meaningful new developments on these tracked stories.",
        "Include them only if there is a real update; say if the topic is quiet.",
    ]
    for story in active:
        lines.append(f"- {story.slug}: {story.description}")
    return "\n".join(lines)


def _xai_search_call(
    model: str,
    system_prompt: str,
    user_prompt: str,
    tool,
    tracked_stories: list[TrackedStory] | None = None,
) -> str:
    client = _get_xai_client()
    chat = client.chat.create(model=model, tools=[tool])
    chat.append(system(system_prompt))
    tracked_block = _format_tracked_topics_for_search(tracked_stories or [])
    chat.append(user(f"{user_prompt}{tracked_block}"))
    response = chat.sample()
    return response.content or ""


def x_search_global(
    model: str, tracked_stories: list[TrackedStory] | None = None
) -> str:
    return _xai_search_call(
        model=model,
        system_prompt="You are a concise news researcher. Output plain text only.",
        user_prompt=_X_GLOBAL_PROMPT,
        tool=x_search(),
        tracked_stories=tracked_stories,
    )


def x_search_local(
    model: str,
    region: str = "South Africa",
    tracked_stories: list[TrackedStory] | None = None,
) -> str:
    return _xai_search_call(
        model=model,
        system_prompt="You are a concise news researcher. Output plain text only.",
        user_prompt=_X_LOCAL_PROMPT_TEMPLATE.format(region=region),
        tool=x_search(),
        tracked_stories=tracked_stories,
    )


def web_search_gaps(
    model: str, tracked_stories: list[TrackedStory] | None = None
) -> str:
    return _xai_search_call(
        model=model,
        system_prompt="You are a concise news researcher. Output plain text only.",
        user_prompt=_WEB_GAPS_PROMPT,
        tool=web_search(),
        tracked_stories=tracked_stories,
    )


# -- Synthesis --


class _SynthesisOutput(BaseModel):
    """LLM-fillable subset of DailyDigest. We attach date + generated_at after."""

    story_clusters: list[StoryCluster] = []
    x_trending_global: str = ""
    x_trending_sa: str = ""
    tracked_story_updates: list[TrackedStoryUpdate] = []


_SYNTHESIS_SYSTEM = (
    "You are the editor-in-chief of a personal daily newspaper. Your job is "
    "to take raw inputs from RSS feeds, X discourse, and web search, and "
    "produce a clean, deduplicated, perspective-aware daily digest.\n\n"
    "Hard rules:\n"
    "1. Cluster headlines about the same event into a single story_cluster, "
    "even when they come from different sources or languages. Do not merge "
    "unrelated stories merely because they share a source, category, "
    "institution, country, person, or broad theme.\n"
    "2. For each cluster, write a neutral synthesized headline and a short "
    "summary (2-4 sentences) that captures what actually happened.\n"
    "3. Populate the perspectives list when sources of different lean cover "
    "the story differently. Keep each perspective summary to one sentence. "
    "If all sources agree on the facts, the perspectives list can be empty "
    "or contain only the wire/center summary.\n"
    "4. Apply the user's editorial profile as calibration, not as a command "
    "to distort facts. Distinguish reported facts from interpretive framing. "
    "When coverage materially relies on loaded language, selective context, "
    "activist premises, or emotionally charged anti-Trump, anti-West, or "
    "anti-American assumptions, flag that in the relevant perspective summary "
    "or cluster summary. Do not debate the profile and do not replace one "
    "ideological framing with another.\n"
    "5. Assign each cluster exactly one category from the configured list. "
    "South African stories must use the sa_local category.\n"
    "6. The slug for each cluster must be lowercase, ascii, words separated "
    "by underscores, and globally unique within this digest.\n"
    "7. sources_count is the number of distinct sources (RSS, X, web) that "
    "covered the story. Populate source_names with the names of the main "
    "sources from the inputs that support the cluster.\n"
    "8. Match clusters against tracked story descriptions by meaning, not "
    "keywords. If a cluster is a continuation of a tracked story, set "
    "tracked_story to that story's slug AND add an entry to "
    "tracked_story_updates with a one-line development summary.\n"
    "9. Use recent records to avoid repetition. If a topic appears in recent "
    "records with no meaningful new development today, omit it. Include "
    "continuations only when there is genuinely new information, and frame "
    "them explicitly as continuations rather than fresh stories.\n"
    "10. x_trending_global and x_trending_sa are detailed freeform rundowns "
    "of the X discourse beyond what made it into clusters. Aim for 600-1200 "
    "words each. Organize by mini-topic with short paragraphs or bullet "
    "groupings. Capture: micro-trends and memes, notable accounts driving "
    "conversation, niche debates, cultural moments, sports reactions, viral "
    "clips, fringe takes that have traction, the overall mood of the "
    "platform. Use specific examples (handles, post counts, numbers) when "
    "the search results provide them. Do not restate what is already in a "
    "story_cluster — the clusters are the news, this section is the "
    "texture. If a topic is substantive enough to be a cluster, keep it in "
    "clusters and only mention X-specific reactions here. The SA section "
    "should focus on uniquely South African discourse — local memes, local "
    "accounts, local cultural moments — and skip global news coverage.\n"
    "11. Output only what is supported by the inputs. Do not invent stories, "
    "sources, or quotes.\n"
    "12. Keep the digest tight but not sparse. With a normal 10-15 source "
    "configuration, aim for 12-25 high-signal clusters across the configured "
    "categories when the inputs support that many. Do not include 100 "
    "low-importance clusters when 20 well-chosen ones would tell the day's "
    "story better."
)


def _format_rss_headlines_for_prompt(headlines: list[dict]) -> str:
    if not headlines:
        return "(no RSS headlines fetched)"
    lines = []
    for h in headlines:
        lines.append(
            f"- [{h.get('category', '?')}|{h.get('source_lean', '?')}|"
            f"{h.get('source_name', '?')}] {h.get('title', '').strip()}"
            + (f"  ({h.get('published', '')})" if h.get("published") else "")
        )
        summary = (h.get("summary") or "").strip()
        if summary:
            snippet = re.sub(r"\s+", " ", summary)[:240]
            lines.append(f"    {snippet}")
    return "\n".join(lines)


def _format_tracked_stories_for_prompt(stories: list[TrackedStory]) -> str:
    active = [s for s in stories if s.active]
    if not active:
        return "(no tracked stories)"
    lines = []
    for s in active:
        last = s.last_updated.isoformat() if s.last_updated else "never"
        lines.append(f"- slug={s.slug} | last_updated={last}")
        lines.append(f"    description: {s.description}")
        if s.developments:
            recent = s.developments[-3:]
            for d in recent:
                lines.append(f"    recent: {d}")
    return "\n".join(lines)


def _format_recent_records_for_prompt(records: list[DailyDigest]) -> str:
    if not records:
        return "(no recent records)"
    lines = []
    for rec in records:
        lines.append(f"## {rec.date.isoformat()}")
        for cluster in rec.story_clusters:
            tracked = (
                f" | tracked={cluster.tracked_story}"
                if cluster.tracked_story
                else ""
            )
            lines.append(f"- [{cluster.category}] {cluster.headline}{tracked}")
            if cluster.summary:
                lines.append(f"    {cluster.summary}")
        lines.append("")
    return "\n".join(lines).strip()


def synthesize_newspaper(
    rss_headlines: list[dict],
    x_global: str,
    x_local: str,
    web_results: str,
    tracked_stories: list[TrackedStory],
    recent_records: list[DailyDigest],
    config: NewsConfig,
    today: date | None = None,
) -> DailyDigest:
    today = today or date.today()
    user_prompt = (
        f"TODAY: {today.isoformat()}\n\n"
        "=== EDITORIAL PROFILE ===\n"
        f"{config.editorial_profile.strip() or '(none)'}\n\n"
        f"ALLOWED CATEGORIES: {', '.join(config.categories)}\n\n"
        "=== RSS HEADLINES ===\n"
        f"{_format_rss_headlines_for_prompt(rss_headlines)}\n\n"
        "=== X DISCOURSE — GLOBAL ===\n"
        f"{x_global.strip() or '(none)'}\n\n"
        "=== X DISCOURSE — SOUTH AFRICA ===\n"
        f"{x_local.strip() or '(none)'}\n\n"
        "=== WEB SEARCH (gap-fill) ===\n"
        f"{web_results.strip() or '(none)'}\n\n"
        "=== TRACKED STORIES (match clusters against these) ===\n"
        f"{_format_tracked_stories_for_prompt(tracked_stories)}\n\n"
        "=== RECENT RECORDS (for continuity — do not duplicate) ===\n"
        f"{_format_recent_records_for_prompt(recent_records)}\n\n"
        "Now produce the structured digest."
    )

    client = _get_xai_client()
    chat = client.chat.create(
        model=config.synthesis_model,
        response_format=_SynthesisOutput,
    )
    chat.append(system(_SYNTHESIS_SYSTEM))
    chat.append(user(user_prompt))
    _, parsed = chat.parse(_SynthesisOutput)

    return DailyDigest(
        date=today,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        story_clusters=parsed.story_clusters,
        x_trending_global=parsed.x_trending_global,
        x_trending_sa=parsed.x_trending_sa,
        tracked_story_updates=parsed.tracked_story_updates,
    )


# -- Refresh-time breaking-news pass --


class _BreakingOutput(BaseModel):
    new_clusters: list[StoryCluster] = []
    tracked_story_updates: list[TrackedStoryUpdate] = []
    summary: str = ""


_REFRESH_SYSTEM = (
    "You are filtering breaking news for an existing daily digest. The user "
    "already received a full digest earlier today. Your job is to identify "
    "ONLY genuinely new or materially developing stories from fresh X "
    "discourse — not to restate what is already in today's digest.\n\n"
    "Rules:\n"
    "1. If a story is already covered in today's clusters, skip it unless "
    "there is a meaningful new development worth flagging.\n"
    "2. new_clusters should follow the same StoryCluster shape (slug, "
    "headline, category, summary, perspectives, sources_count). Use "
    "category from the configured list. South African items use sa_local.\n"
    "3. Match new clusters against tracked story descriptions; if matched, "
    "set tracked_story to the slug AND add a tracked_story_updates entry.\n"
    "4. Apply the user's editorial profile as calibration. Distinguish facts "
    "from framing and flag materially loaded anti-Trump, anti-West, or "
    "anti-American assumptions when they shape the coverage.\n"
    "5. Keep clusters tight. Two or three high-signal items beats ten "
    "low-signal ones.\n"
    "6. summary is a one-sentence headline of what changed since the "
    "morning digest. Empty string if nothing new.\n"
    "7. Do not invent stories. If nothing has materially changed, return "
    "empty lists and a brief summary saying so."
)


def synthesize_breaking(
    today_record: DailyDigest | None,
    tracked_stories: list[TrackedStory],
    x_global: str,
    x_local: str,
    config: NewsConfig,
) -> _BreakingOutput:
    today_section = (
        _format_recent_records_for_prompt([today_record])
        if today_record is not None
        else "(no morning digest exists yet — every story is new)"
    )

    user_prompt = (
        "=== EDITORIAL PROFILE ===\n"
        f"{config.editorial_profile.strip() or '(none)'}\n\n"
        f"ALLOWED CATEGORIES: {', '.join(config.categories)}\n\n"
        "=== TODAY'S MORNING DIGEST (already delivered) ===\n"
        f"{today_section}\n\n"
        "=== FRESH X DISCOURSE — GLOBAL ===\n"
        f"{x_global.strip() or '(none)'}\n\n"
        "=== FRESH X DISCOURSE — SOUTH AFRICA ===\n"
        f"{x_local.strip() or '(none)'}\n\n"
        "=== TRACKED STORIES (match new clusters against these) ===\n"
        f"{_format_tracked_stories_for_prompt(tracked_stories)}\n\n"
        "Return only the new or developing material."
    )

    client = _get_xai_client()
    chat = client.chat.create(
        model=config.synthesis_model,
        response_format=_BreakingOutput,
    )
    chat.append(system(_REFRESH_SYSTEM))
    chat.append(user(user_prompt))
    _, parsed = chat.parse(_BreakingOutput)
    return parsed


# -- Tracked-story update helper --


def apply_tracked_story_updates(
    updates: list[TrackedStoryUpdate], today: date | None = None
) -> int:
    """Append developments to matched tracked stories. Skips unknown slugs and inactive stories.

    Returns the number of stories actually updated.
    """
    today = today or date.today()
    n = 0
    for update in updates:
        try:
            story = load_tracked_story(update.slug)
        except FileNotFoundError:
            continue
        if not story.active:
            continue
        story.developments.append(f"{today.isoformat()}: {update.development}")
        story.last_updated = today
        save_tracked_story(story)
        n += 1
    return n
