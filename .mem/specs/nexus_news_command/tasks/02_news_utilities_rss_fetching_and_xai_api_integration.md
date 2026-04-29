---
title: News utilities — RSS fetching and xAI API integration
status: completed
created_at: '2026-04-07T15:20:22.399271'
updated_at: '2026-04-29T15:40:21.804284'
completed_at: '2026-04-29T15:40:21.804280'
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

## Completion Notes

Completed the xAI half of src/utils/news.py. The RSS + TOML I/O half was already done in the prior session.

## Decisions (set with the user)

- **Dropped agno** entirely. xai-sdk supports Pydantic structured outputs natively (response_format=MyModel on chat.create), so we get X Search, Web Search, AND typed JSON output from a single SDK.
- **Single model, grok-4.20-reasoning, for everything** (sourcing AND synthesis). Updated NewsConfig defaults: xai_model="grok-4.20-reasoning", synthesis_model="grok-4.20-reasoning".
- **No streaming.** chat.sample() for text outputs, chat.parse(Model) for structured output.

## Fixed env_settings.py

It was not loading .env (pydantic-settings does not auto-load without config). Added `model_config = SettingsConfigDict(env_file=".env", extra="ignore")` so `from env_settings import ENV_SETTINGS` now picks up XAI_API_KEY.

## Helpers added to src/utils/news.py

- `_get_xai_client()` — returns `xai_sdk.Client` keyed off `ENV_SETTINGS.xai_api_key`.
- `x_search_global(model)` — returns plain text. Prompt asks for last 24h on X, organized by topic (politics, geopolitics, tech, econ, science, entertainment, fringe/conspiracy), one-line headline + 2-3 bullets per story, flag camp-disagreement when meaningful.
- `x_search_local(model, region="South Africa")` — same shape, scoped to a region. Default region is South Africa.
- `web_search_gaps(model)` — uses web_search tool, asks for stories that wire feeds may underreport (developing events, under-covered international, science/tech/econ deep-dives, long-running story updates).
- All three sourcing helpers route through `_xai_search_call(model, system_prompt, user_prompt, tool)` which is the only place that touches the SDK directly for sourcing.
- `synthesize_newspaper(rss_headlines, x_global, x_local, web_results, tracked_stories, recent_records, config, today=None) -> DailyDigest` — the main synthesis call.
  - Uses an internal `_SynthesisOutput(BaseModel)` for the LLM-fillable subset of DailyDigest (story_clusters, x_trending_global, x_trending_sa, tracked_story_updates). date and generated_at are filled by Python after parsing.
  - chat.parse(_SynthesisOutput) is used for typed structured output.
  - The system prompt lays out 10 hard rules: cluster aggressively, neutral synthesized headlines, perspectives only when sources of different lean diverge, slug format (lowercase/ascii/underscores/unique), category from configured list (sa_local for SA), free-text matching against tracked stories, no invented content, keep digest tight.
  - The user prompt is built by three private formatters: `_format_rss_headlines_for_prompt`, `_format_tracked_stories_for_prompt`, `_format_recent_records_for_prompt`.

## Verification (live calls against the xAI API)

1. Hello-world chat call → grok-4.20-reasoning responds.
2. `web_search_gaps` → 2.7k chars. Cleanly organized output (Middle East tensions, NASA Curiosity, Oak Ridge SNS, oil-driven inflation). Cited Reuters/BBC/IMF/JPL.
3. `x_search_global` → 3.7k chars. Geopolitics, economics/tech, Indian politics, K-pop entertainment with handle attribution and disagreement flags. Fringe/conspiracy section noted limited traction (appropriate skepticism).
4. `x_search_local` (South Africa) → 4.3k chars. Operation Dudula protests, JHB CBD targeted killings, Police Commissioner Masemola suspension, AI policy withdrawal, SARB deepfake warning. Flagged polarized discourse explicitly.
5. `synthesize_newspaper` with canned inputs (4 RSS headlines + brief x_global/x_local/web summaries + 1 tracked story "war_in_iran"):
   - Produced 5 clusters with correct categories (international/sa_local/economics/science/us_politics).
   - The Iran blockade cluster was correctly tagged `tracked_story="war_in_iran"` via free-text semantic match.
   - tracked_story_updates list populated with one-line dev summary.
   - Slug format correct: `trump_threatens_iran_blockade`.
   - x_trending_global and x_trending_sa populated as freeform summaries (not duplicating cluster content).
   - TOML round-trip via save_daily_digest / load_daily_digest preserved all fields including the nested tracked_story link.

## Notes for downstream tasks

- The synthesis prompt is the most expensive call (reasoning tokens add up). Consider whether tasks 4+ should expose a `--no-x-search` or `--no-web-search` flag for cheap dev iteration.
- All search outputs are plain text (markdown-formatted by Grok). They go straight into the synthesis user prompt as separate sections — no parsing.
- _SynthesisOutput is intentionally private to news.py; we never serialize it. DailyDigest is the only public model consumers see.
- httpx is used for RSS fetching; xAI calls go through xai_sdk's gRPC channel — no httpx involvement there.