---
title: News utilities — RSS fetching and xAI API integration
status: todo
created_at: '2026-04-07T15:20:22.399271'
updated_at: '2026-04-07T15:20:22.399271'
completed_at: null
---
Create src/utils/news.py with all the core logic.

TOML I/O (follow patterns in src/utils/self.py):
- get_news_config_path() -> news/config.toml
- get_records_dir() -> news/records/
- get_stories_dir() -> news/stories/
- load_news_config() / save_news_config()
- load_daily_digest(date) / save_daily_digest(digest)
- load_tracked_story(slug) / save_tracked_story(story)
- list_tracked_stories() -> list[TrackedStory]
- load_recent_records(n=3) -> list[DailyDigest]
- slugify(text) -> str (reuse pattern from src/utils/self.py)

RSS FETCHING:
- fetch_all_feeds(sources: list[SourceEntry]) -> list[dict] — iterate all sources, parse with feedparser, return list of {title, source_name, source_lean, link, published, category}. Handle failures gracefully (skip failed feeds, print warning, continue).
- Use httpx to fetch feed content, feedparser to parse it. feedparser can parse from a string (fetched via httpx) or from a URL directly — use feedparser.parse(url) for simplicity.

xAI API INTEGRATION:
- _get_xai_client() -> OpenAI — creates OpenAI client with base_url='https://api.x.ai/v1' and api key from config or XAI_API_KEY env var
- x_search_global() -> str — calls xAI with x_search tool, prompt asking for biggest global news stories on X
- x_search_local(region='South Africa') -> str — same but for SA news on X
- web_search_gaps() -> str — calls xAI with web_search tool for stories RSS might miss
- synthesize_newspaper(rss_headlines, x_global, x_local, web_results, tracked_stories, recent_records) -> DailyDigest — the main synthesis call. Sends everything to xAI with a carefully crafted prompt that instructs it to: cluster related stories, tag perspectives per cluster, match against tracked story descriptions, produce structured JSON. Parse the JSON response into a DailyDigest model.

SYNTHESIS PROMPT (critical):
The prompt must instruct the LLM to:
1. Group headlines about the same event from different sources into clusters
2. For each cluster: write a neutral headline, summary, and list perspectives (what left-leaning sources say, what right-leaning say, what X discourse says)
3. Assign each cluster a category from the configured list
4. Match clusters against tracked story descriptions (free-text semantic matching)
5. Note which stories are continuations from recent records
6. Output valid JSON matching the DailyDigest schema
7. The SA section should be treated as its own category

Use JSON mode / structured output if supported by the xAI model. Otherwise, prompt for JSON and parse.

All async functions should have sync wrappers (asyncio.run) following the weather.py pattern.