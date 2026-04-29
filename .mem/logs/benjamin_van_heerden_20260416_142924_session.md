---
created_at: '2026-04-16T14:29:24.228274'
username: benjamin_van_heerden
spec_slug: nexus_news_command
---
# Work Log - Scaffolding + RSS layer for `nexus news`

## Overarching Goals

Kick off the `nexus_news_command` spec: establish the model layer and file-system scaffolding, then make verifiable progress on the data-sourcing side of the system. The user's priority is tight feedback loops — every layer should be tested against real data before moving up the stack. The overall architecture the user settled on during this session:

- Sourcing (X trends, hot topics, breaking news, international, conspiracies) via **xai-sdk** directly — keeps Grok-specific features like X Search properly typed.
- Synthesis (clustering, dedup, perspective tagging, story matching against records) via a **separate AI** wrapped by **agno**.
- RSS fetching built and verified first, before any AI integration.

## What Was Accomplished

### Task 1 — Models and directory scaffolding (COMPLETED)

Created the Pydantic model layer for the news system and wired pause/paths integrations:

- `src/models/news/config.py` — `SourceEntry` (name, url, category, lean) and `NewsConfig` (sources, xai_model, synthesis_model, history_days, categories). The `synthesis_model` field was added to the spec shape to reflect the user's decision to use two different AIs.
- `src/models/news/digest.py` — `PerspectiveEntry`, `StoryCluster`, `DailyDigest`, plus a new typed `TrackedStoryUpdate` model (slug, headline, development) instead of the spec's `list[dict]`, for consistency with the rest of the codebase and easier downstream testing.
- `src/models/news/story.py` — `TrackedStory` (slug, description, created, last_updated, developments, active).
- `src/models/pause.py` — added `news: PauseEntry = PauseEntry()` to `PauseConfig`.
- `src/utils/paths.py` — added `get_news_dir() -> Path`.
- Created `news/records/` and `news/stories/` with `.gitkeep` files (following the `self/reading/completed` and `self/weekly` convention).

Verified via `uv run python` by importing every new model, instantiating each with realistic data (BBC source, a story cluster with perspectives, tracked story + update, `PauseConfig().news`), confirming clean round-trip.

### Task 2 — RSS portion of news utilities (PARTIAL)

Created `src/utils/news.py` with the TOML I/O layer and async RSS fetching. The xAI API integration portion of this task was deliberately deferred until the user can provision an API key.

**TOML I/O** (mirrors the pattern in `src/utils/self.py`):
- Path helpers: `get_news_config_path()`, `get_records_dir()`, `get_stories_dir()`, `get_record_path(day)`, `get_story_path(slug)`.
- `_load_toml` / `_save_toml` private helpers with `multiline_strings=True` for readable records and `parent.mkdir(parents=True, exist_ok=True)` on save so the caller never has to worry about directory creation.
- `load_news_config()` / `save_news_config()`.
- `load_daily_digest(day) -> DailyDigest | None` (returns None if missing) / `save_daily_digest(digest)`.
- `load_recent_records(n=3)` — sorts `*.toml` in records dir reversed (ISO dates sort correctly by string), skips unparseable files.
- `load_tracked_story(slug)` / `save_tracked_story(story)` / `list_tracked_stories(active_only=False)`.
- `slugify(text)` matching the regex `[^a-z0-9]+` pattern used in `self.py` and `manage.py`.

**RSS fetching** (`feedparser` + `httpx.AsyncClient`):
- `_fetch_one_feed(client, source)` — per-feed 15 s timeout, `follow_redirects=True`, custom `User-Agent: nexus-news/0.1`. Returns `[]` on any fetch/parse failure and prints `[warn] <source>: <reason>`. Ignores `bozo` flag if `entries` still came back (many feeds are technically invalid but still parseable).
- `_parse_entry_date(entry)` — tries `published`/`updated`/`created` strings first, falls back to `*_parsed` struct_time, else empty string. We deliberately keep the raw string format since sources disagree on format and the synthesis LLM can normalise later.
- `fetch_all_feeds(sources)` — `asyncio.gather` over all sources concurrently, flattens results.
- `fetch_all_feeds_sync(sources)` — wraps via `asyncio.run` for CLI callers (mirrors `fetch_weather_sync` in `src/utils/weather.py`).

Each headline dict has: `title`, `source_name`, `source_lean`, `link`, `published`, `category`, `summary`.

### Dependency added

- `feedparser==6.0.12` (transitively pulls `sgmllib3k==1.0.0`) via `uv add feedparser`.

### Feedback loops exercised

1. **TOML round-trip test** — saved and reloaded a `NewsConfig` (2 sources), a `DailyDigest` with clusters/perspectives/tracked updates, and a `TrackedStory`; verified each field. Confirmed `load_recent_records(n=3)` finds the saved file. Cleaned up artifacts after.
2. **Live RSS fetch** — ran `fetch_all_feeds` against 10 real-world sources (7 expected-working, 3 expected-broken). Results:
   - 176 total headlines from working feeds.
   - Counts: BBC 36, Guardian 45, HN 30, Al Jazeera 25, Ars Technica 20, NPR 10, News24 10.
   - Graceful failures: Reuters feed (404 — URL in spec is stale), Daily Maverick (404 — URL in spec is stale), nonexistent-domain test (DNS error).
   - Findings worth flagging for synthesis work: published-date formats vary per source (RFC822, ISO8601, human-readable "Thursday Apr 16 2026 11:11:53"); `summary` fields for The Guardian and Hacker News contain raw HTML tags. Both are fine for LLM ingestion as-is.

## Key Files Affected

- NEW `src/models/news/config.py` — `SourceEntry`, `NewsConfig`
- NEW `src/models/news/digest.py` — `PerspectiveEntry`, `StoryCluster`, `TrackedStoryUpdate`, `DailyDigest`
- NEW `src/models/news/story.py` — `TrackedStory`
- NEW `src/utils/news.py` — TOML I/O + async RSS fetching
- NEW `news/records/.gitkeep`, `news/stories/.gitkeep`
- MODIFIED `src/models/pause.py` — added `news: PauseEntry = PauseEntry()` to `PauseConfig`
- MODIFIED `src/utils/paths.py` — added `get_news_dir() -> Path`
- MODIFIED `pyproject.toml` / `uv.lock` — added `feedparser` dependency

## What Comes Next

Task 2 (`News utilities — RSS fetching and xAI API integration`) is partially complete — the RSS + TOML I/O + slug parts are done and verified. The xAI integration half remains, and requires:

1. **User provisions `XAI_API_KEY`** — the user indicated they'd set this up when we reach this point.
2. **Add `xai-sdk` and `agno` as dependencies** once keys are sorted. Synthesis model itself is TBD — `NewsConfig.synthesis_model` is empty by default, waiting on the user.
3. **Implement the xAI client helpers in `src/utils/news.py`**:
   - `_get_xai_client()` — uses `xai-sdk` directly (not the OpenAI-compatible shim) so X Search is properly typed.
   - `x_search_global()`, `x_search_local(region='South Africa')` — use Grok's `x_search` tool. User's framing: "Get me the most recent X stories and news, hot topics in categories XYZ, any conspiracies that have gone trending, international interests etc".
   - `web_search_gaps()` — Grok with `web_search` tool.
4. **Implement synthesis via agno** — a separate function `synthesize_newspaper(rss_headlines, x_global, x_local, web_results, tracked_stories, recent_records) -> DailyDigest` that uses agno to call the synthesis model and parse into the `DailyDigest` schema.
5. **Test each xAI call independently** before wiring synthesis — print raw outputs so we can see what Grok actually returns for each tool/prompt combo, then tune prompts before stringing them together.

Remaining spec tasks after task 2 finishes:
- Task 3: CLI commands (source, track, stories)
- Task 4: `onboard` and `refresh` commands
- Task 5: Main app wiring + pause CLI integration (`nexus pause news`)
- Task 6: Agent instructions + default `news/config.toml` with curated real sources (the Reuters/Daily Maverick URLs in the spec are stale — need to re-research)

No blockers. User stepped away; resume on next session.
