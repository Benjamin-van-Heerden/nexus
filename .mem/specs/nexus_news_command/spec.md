---
title: nexus news command
status: todo
assigned_to: Benjamin-van-Heerden
issue_id: 9
issue_url: https://github.com/Benjamin-van-Heerden/nexus/issues/9
branch: dev-benjamin_van_heerden-nexus_news_command
pr_url: null
created_at: '2026-04-07T15:17:39.642178'
updated_at: '2026-04-07T15:24:28.262770'
completed_at: null
last_synced_at: '2026-04-07T15:22:14.853853'
local_content_hash: 3e7d5d3a9efe841b94b1312bf5d940b971e884d46c543111da014a2c58084e7a
remote_content_hash: 3e7d5d3a9efe841b94b1312bf5d940b971e884d46c543111da014a2c58084e7a
---
## Overview

Build `nexus news` — a personalized daily news aggregation system. It pulls headlines from curated RSS feeds and xAI's Grok API (with `x_search` for X/Twitter discourse and `web_search` for broader coverage), then uses an LLM pass to deduplicate, cluster related stories, tag them by perspective (left/right/international/social), and produce a structured daily newspaper. The system maintains continuity across days by loading recent records, tracks user-specified stories over time, and covers both international and South African local news.

This is a standalone `nexus news` subapp (not part of `nexus manage`), with its own `onboard` and `refresh` commands, following the same patterns as learn/self/manage.

## Goals

- Produce a detailed, personalized daily newspaper covering: science, technology, economics, US politics, international/geopolitics, entertainment, and South African local news
- Pool from diverse sources (left, right, center, international) to minimize bias — each story cluster should show what different perspectives are saying
- Surface X/Twitter discourse alongside traditional media coverage
- Track stories over time — user can say "keep tabs on the war in Iran" and the system will match incoming headlines against tracked topics and report developments
- Maintain day-to-day continuity by loading the last 3 daily records when generating a new digest
- All synthesis (dedup, clustering, perspective tagging, story matching) happens inside the CLI commands via xAI API calls — the consuming agent just reads and relays the output

## Technical Approach

### Architecture

Three data-sourcing layers feed into an LLM synthesis step:

1. **RSS layer** (free) — curated feeds parsed with `feedparser`, organized by category
2. **xAI x_search** — Grok searches X/Twitter for trending news, breaking events, social discourse. Separate calls for global and South African news
3. **xAI web_search** — Grok searches the web to fill gaps RSS might miss

The LLM synthesis step (also via xAI) takes all raw headlines and produces the final clustered, deduplicated, perspective-tagged newspaper.

### xAI API Integration

The xAI API is OpenAI-compatible. Use the `openai` Python package (already a project dependency or add it) with `base_url="https://api.x.ai/v1"`. The API key should be stored in the project's environment settings (`env_settings.py` or a dedicated `news/config.toml` field — see below).

**Search tools usage:**
```python
from openai import OpenAI

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")
response = client.chat.completions.create(
    model="grok-3",  # or latest available
    tools=[{"type": "x_search"}, {"type": "web_search"}],
    messages=[{"role": "user", "content": "..."}]
)
```

Key points:
- `x_search` and `web_search` are passed as tool types, not function-calling tools
- Grok autonomously decides when/how to search based on the prompt
- Cost is ~$0.01-0.03 per call, so daily usage is under $5/month

### Directory Structure

```
news/                           # Data directory (project root)
├── config.toml                 # Sources list, xAI config, categories
├── records/                    # Daily digests
│   ├── 2026-04-07.toml         # Structured digest (TOML, not markdown)
│   ├── 2026-04-06.toml
│   └── ...
└── stories/                    # Tracked stories (user-created)
    ├── war_in_iran.toml
    └── openai_ipo.toml
```

### Source Code Structure

Following existing conventions exactly:

```
src/
├── commands/news/
│   ├── main.py                 # Typer app, wires up subcommands
│   ├── onboard.py              # onboard() and refresh() functions
│   ├── source.py               # nexus news source [add|remove|list]
│   ├── track.py                # nexus news track / untrack / stories
│   └── agent_instructions.md   # Instructions for consuming agent
├── models/news/
│   ├── config.py               # NewsConfig, SourceEntry, CategoryConfig
│   ├── digest.py               # DailyDigest, StoryCluster, PerspectiveEntry
│   └── story.py                # TrackedStory
└── utils/
    └── news.py                 # RSS fetching, xAI calls, synthesis, TOML I/O
```

### Models

**`src/models/news/config.py`:**
```python
class SourceEntry(BaseModel):
    name: str                           # e.g. "BBC News"
    url: str                            # RSS feed URL
    category: str                       # e.g. "international", "tech", "sa_local"
    lean: str = "center"                # "left", "center-left", "center", "center-right", "right", "international"

class NewsConfig(BaseModel):
    sources: list[SourceEntry] = []
    xai_model: str = "grok-3"
    history_days: int = 3               # How many past records to load for continuity
    categories: list[str] = [
        "science", "technology", "economics",
        "us_politics", "international", "entertainment",
        "sa_local"
    ]
```

**`src/models/news/digest.py`:**
```python
class PerspectiveEntry(BaseModel):
    lean: str                           # "left", "right", "center", "international", "x_social"
    source: str                         # Source name
    summary: str                        # What this perspective is saying

class StoryCluster(BaseModel):
    slug: str                           # Unique slug for this story cluster
    headline: str                       # Synthesized headline
    category: str                       # Category tag
    summary: str                        # Overall summary
    perspectives: list[PerspectiveEntry] = []
    tracked_story: str | None = None    # Slug of tracked story if matched
    sources_count: int = 1              # How many sources covered this

class DailyDigest(BaseModel):
    date: date
    generated_at: str                   # ISO timestamp
    story_clusters: list[StoryCluster] = []
    x_trending_global: str = ""         # Freeform X trending summary (global)
    x_trending_sa: str = ""             # Freeform X trending summary (South Africa)
    tracked_story_updates: list[dict] = []  # [{slug, headline, development}]
```

**`src/models/news/story.py`:**
```python
class TrackedStory(BaseModel):
    slug: str
    description: str                    # Free text — e.g. "The war in Iran"
    created: date
    last_updated: date | None = None
    developments: list[str] = []        # Chronological list of developments
    active: bool = True
```

### Commands

| Command | Description |
|---|---|
| `nexus news onboard` | Full newspaper generation: fetch RSS, call xAI (x_search global + SA, web_search), synthesize via LLM, update tracked stories, save record, print output |
| `nexus news refresh` | Lighter version: only xAI calls (no RSS re-fetch), check for breaking news since onboard, update tracked stories |
| `nexus news source add <url> --name "Name" --category "category" --lean "center"` | Add RSS source to config |
| `nexus news source remove <name-or-url>` | Remove RSS source |
| `nexus news source list` | List all configured sources with category and lean |
| `nexus news track "description"` | Create a tracked story — description is free text interpreted by LLM during onboard |
| `nexus news untrack <slug>` | Deactivate a tracked story |
| `nexus news stories` | List all tracked stories with last update |

### Onboard Flow (the core logic)

1. Check pause status (`check_pause("news")`)
2. Load last N daily records (default 3) from `news/records/` for continuity
3. Load all tracked stories from `news/stories/`
4. **Fetch RSS feeds** — iterate all sources in config, parse with `feedparser`, collect raw headlines (title, source, link, published date, category)
5. **Call xAI with x_search (global)** — prompt: "Search X and find the biggest news stories, breaking events, and major topics of conversation happening right now globally. Cover: politics, economics, technology, science, entertainment, geopolitics."
6. **Call xAI with x_search (South Africa)** — prompt: "Search X and find the biggest news stories, events, and topics being discussed in South Africa right now."
7. **Call xAI with web_search** — prompt: "What are the most important news stories in the world right now that might not be covered in mainstream RSS feeds? Focus on breaking news in the last 24 hours."
8. **LLM synthesis call** — send ALL collected data (RSS headlines, X results, web results, tracked story descriptions, last 3 days' summaries for continuity) to xAI with a structured prompt:
   - Cluster related headlines into story groups
   - For each cluster: synthesize a headline, write a summary, tag perspectives (what left says, what right says, what's on X)
   - Match clusters against tracked story descriptions (free-text matching)
   - Flag stories that are continuations of yesterday's stories
   - Output as structured JSON matching the DailyDigest model
9. Parse LLM response into DailyDigest
10. Save to `news/records/YYYY-MM-DD.toml`
11. Update matched tracked stories (append developments)
12. **Print the newspaper** — formatted output organized by category, with sections for perspectives and tracked story updates

### Refresh Flow

1. Check pause
2. Load today's record (if onboard already ran)
3. Call xAI with x_search only (both global and SA) — "What breaking news has happened in the last few hours?"
4. Quick LLM pass to identify genuinely new stories not in today's record
5. Print only new/breaking stories + any tracked story developments
6. Do NOT overwrite today's record — append or create a refresh addendum

### Deduplication Strategy

All deduplication is LLM-based. No hashing. The synthesis prompt instructs the model to:
- Group headlines about the same event/story from different sources
- Preserve source attribution within each cluster
- Note the editorial lean of each source
- Produce a neutral synthesized headline
- Show "What the left is saying / What the right is saying / What's happening on X" sections per cluster when perspectives meaningfully differ

### Story Tracking

The `track` command takes free text only — e.g. `nexus news track "The war in Iran"`. No structured fields. During onboard, the LLM synthesis step receives all tracked story descriptions and is prompted to match incoming headlines against them. When a match is found:
- The cluster gets tagged with the tracked story slug
- A development summary is appended to the story's `developments` list
- The story's `last_updated` date is set to today
- The newspaper output has a dedicated "TRACKED STORIES" section showing: description → latest development

### Source Diversity (Default Sources)

The initial `news/config.toml` should ship with a curated but editable list. At minimum:

**Wire/Neutral:** Reuters, AP
**US Left/Center-Left:** NPR, NYT, The Guardian
**US Right/Center-Right:** Fox News, WSJ, The Hill
**International:** BBC, Al Jazeera, DW (Deutsche Welle), France24
**Tech:** Ars Technica, TechCrunch, Hacker News
**Science:** Nature, Science Daily
**South Africa:** News24, Daily Maverick, EWN (Eyewitness News), TimesLive, IOL

The exact source list is dynamic — the user curates it via `nexus news source add/remove`. The system must work with whatever sources are configured.

### Pause Integration

Add `news: PauseEntry = PauseEntry()` to the `PauseConfig` model in `src/models/pause.py`. Add `nexus pause news --until YYYY-MM-DD` to the pause command in `src/commands/pause/main.py`.

### Key File Touchpoints (existing files to modify)

- `main.py` — register `news_app` as `app.add_typer(news_app, name="news", ...)`
- `src/utils/paths.py` — add `get_news_dir() -> Path`
- `src/models/pause.py` — add `news: PauseEntry = PauseEntry()` to PauseConfig
- `src/commands/pause/main.py` — add `nexus pause news` command

### API Key Configuration

The xAI API key should be configured via the project's existing environment settings pattern. Add `xai_api_key: str = ""` to the env settings, or store it in `news/config.toml` as a field. The implementer should check if `env_settings.py` exists and follow the existing pattern — if not, store it in `news/config.toml` and load it from there. The key is obtained from `console.x.ai`.

**Important:** If `env_settings.py` doesn't exist in this project, do NOT create one just for this. Store the API key in `news/config.toml` under an `[xai]` section, or use an environment variable `XAI_API_KEY` loaded via `os.environ.get()`.

### Dependencies

- `feedparser` — RSS parsing (needs `uv add feedparser`)
- `openai` — xAI API client (OpenAI-compatible, needs `uv add openai`)
- These are the only new dependencies. httpx, tomllib, tomli_w, pydantic are already available.

## Success Criteria

- `nexus news onboard` produces a complete, categorized newspaper with perspective tagging and X discourse
- `nexus news refresh` produces a lighter update with only new/breaking stories
- Story tracking works with free-text descriptions and LLM-based matching
- Sources are configurable via `nexus news source add/remove/list`
- Daily records are saved and loaded for continuity
- South African local news has its own section with multiple sources and X coverage
- Pause integration works (`nexus pause news --until ...`)
- Output is clean, structured, and readable by both humans and agents

## Notes

- The consuming agent (OpenClaw via Telegram) will read the onboard/refresh output and relay it to the user. The CLI does the heavy lifting — the agent just formats for Telegram.
- Cost should be under $5/month for daily usage.
- The `openai` package is used as the xAI client since the API is OpenAI-compatible. Use `base_url="https://api.x.ai/v1"`.
- All HTTP calls use `httpx` (project convention), except for the xAI API calls which go through the `openai` SDK.
- RSS feed URLs change occasionally — the system should handle fetch failures gracefully (skip failed feeds, log a warning, continue with what succeeded).
- The LLM synthesis prompt is the most critical piece — it needs to be well-crafted to produce consistent, structured JSON output. Use JSON mode if the xAI API supports it.
- The exact model to use (grok-3, grok-4, etc.) should be configurable in `news/config.toml` so it can be updated without code changes.
