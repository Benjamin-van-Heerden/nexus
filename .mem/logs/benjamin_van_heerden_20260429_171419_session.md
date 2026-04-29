---
created_at: '2026-04-29T17:14:19.041113'
username: benjamin_van_heerden
spec_slug: nexus_news_command
---
# Work Log - xAI integration, CLI commands, onboard/refresh; identified tracked-story + continuity gaps

## Overarching Goals

Continue the `nexus_news_command` spec from where the previous session left off. Last session built the model layer, RSS layer, and TOML I/O. This session was about wiring up the actual AI pipeline (xAI sourcing + LLM synthesis), then layering the user-facing commands (track/untrack/stories, onboard, refresh) on top of it. The user's priorities throughout were: tight feedback loops with verification against real data at each layer, decisions made consciously about which tools/models/abstractions to use, and a system that an agent can drive end-to-end without surprises.

A second meta-thread: scoping discipline. When the user pushed back on parts of the spec that didn't justify their cost (the `source` CLI commands; the agno dependency for synthesis), we cut them rather than building dead weight.

## What Was Accomplished

### Task 2 — xAI integration (completed)

**Decisions made with the user up-front:**
- Dropped agno entirely. xai-sdk supports Pydantic structured outputs natively via `chat.parse(MyModel)`, so we get X Search + Web Search + typed JSON output from a single SDK. The prior plan to use agno for synthesis was driven by concerns that don't apply when using xai-sdk directly.
- Single model, `grok-4.20-reasoning`, for both sourcing and synthesis. Updated `NewsConfig` defaults: `xai_model="grok-4.20-reasoning"`, `synthesis_model="grok-4.20-reasoning"`.
- No streaming. `chat.sample()` for plain-text outputs, `chat.parse(Model)` for structured.

**Side fix to `env_settings.py`:** It was not loading `.env`. Added `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`. This fix is shared infrastructure; future env vars will pick up automatically.

**Helpers added to `src/utils/news.py`:**
- `_get_xai_client()` — returns `xai_sdk.Client(api_key=ENV_SETTINGS.xai_api_key)`.
- `_xai_search_call(model, system_prompt, user_prompt, tool)` — single private helper that all three sourcing functions route through. Only place that touches the SDK directly for sourcing.
- `x_search_global(model)` — last-24h X discourse organized by topic (politics, geopolitics, tech, econ, science, entertainment, fringe/conspiracy), with one-line headline + 2-3 bullets per story and camp-disagreement flags.
- `x_search_local(model, region="South Africa")` — same shape, regional scope.
- `web_search_gaps(model)` — uses `web_search` tool for stories wires may underreport.
- `synthesize_newspaper(rss_headlines, x_global, x_local, web_results, tracked_stories, recent_records, config, today=None) -> DailyDigest` — main synthesis call. Internal `_SynthesisOutput(BaseModel)` for the LLM-fillable subset of `DailyDigest`. `date` and `generated_at` filled by Python after parsing — the LLM is not asked to populate fields it doesn't need to know about.
- 10-rule synthesis system prompt: cluster aggressively, neutral synthesized headlines, perspectives only when sources of different lean diverge, slug format (lowercase/ascii/underscores/unique), category from configured list (sa_local for SA), free-text matching against tracked stories, no invented content.
- Three private formatters for the user-prompt blocks: `_format_rss_headlines_for_prompt`, `_format_tracked_stories_for_prompt`, `_format_recent_records_for_prompt`.

Verified live (in order):
1. Hello-world chat call → grok-4.20-reasoning responds.
2. `web_search_gaps` → 2.7k chars, cited sources cleanly.
3. `x_search_global` → 3.7k chars; properly skeptical fringe section.
4. `x_search_local` → 4.3k chars; SA-specific (Operation Dudula, Masemola suspension, SARB deepfakes).
5. `synthesize_newspaper` with canned inputs → 5 clusters, correct categories, free-text tracked-story match worked, slug format correct, TOML round-trip preserved everything.

### Task 3 — Track/untrack/stories CLI commands (completed)

**Scoping decision with the user:** dropped the `source` add/remove/list commands entirely. Rationale: low value vs editing `news/config.toml` directly. Adding requires the URL on the clipboard already, the operation is rare (seed once, touch occasionally), and agent-driven adds are awkward. The `source` commands were a placeholder, not a real workflow.

**Created `src/commands/news/track.py`** with three module-level functions to be wired into the news app in Task 5:

- `track(description, --slug)` — slug derivation: explicit `--slug` wins; else first 6 words of description slugified (e.g. "The war in Iran and ongoing nuclear negotiations" → `the_war_in_iran_and_ongoing`). Refuses empty descriptions and duplicate slugs.
- `untrack(slug)` — slugifies input for safety; errors on missing; idempotent if already inactive.
- `stories()` — splits into Active and Inactive sections, each showing slug, description, created, last_updated, dev count.

Verified all behaviors via `typer.testing.CliRunner` (empty list, empty-desc rejection, auto-slug, explicit slug, dup rejection, untrack flow, idempotency, mixed listing). Test artifacts cleaned up.

### Task 4 — Onboard/refresh commands (effectively done; left open pending two prompt-level improvements identified at end-of-session)

**Side fix:** `src/utils/pause.py` — added `"news"` to the `Literal` types on `check_pause`, `pause_feature`, `resume_feature`. The `PauseConfig` model already had the field; the utilities were still type-restricted.

**Added to `src/utils/news.py`:**
- `synthesize_breaking(today_record, tracked_stories, x_global, x_local, config) -> _BreakingOutput` — refresh-time LLM pass that filters fresh X discourse against the morning digest. Returns only new/developing clusters + tracked updates + a one-line "what changed" summary. Separate system prompt that explicitly tells the model not to restate the morning digest.
- `apply_tracked_story_updates(updates, today)` — extracted helper that loops `TrackedStoryUpdate`s, appends `"YYYY-MM-DD: <development>"` to story developments, sets `last_updated`. Skips unknown slugs (LLM hallucination guard) and inactive stories. Returns count.

**Created `src/commands/news/onboard.py`:**

`onboard()`:
1. Pause check → exit 0 if paused.
2. Load config, last N records, active tracked stories.
3. Header banner with date + counts.
4. RSS fetch.
5. `x_search_global`, `x_search_local`, `web_search_gaps` (each with progress).
6. `synthesize_newspaper`.
7. Save digest, apply tracked-story updates.
8. Print newspaper: TRACKED STORIES section first (so agent leads with continuations), clusters grouped by `config.categories` order, then TRENDING ON X (GLOBAL/SA).
9. Print `agent_instructions.md` if present (Task 6).
10. ACTION REQUIRED footer.

`refresh()`:
1. Pause check.
2. Load today's record (None if missing), tracked stories.
3. Two fresh `x_search` calls (global + SA only — no RSS, no web).
4. `synthesize_breaking` filters against today's record.
5. Print: WHAT CHANGED summary, new clusters by category, tracked-story developments.
6. **Does not save** — morning record preserved.

Verified end-to-end live with a 2-feed config (BBC + Hacker News) + 1 tracked story (`war_in_iran`). Onboard produced 11 well-categorized clusters; tracked story correctly linked to "Oil Prices Jump Near $117..." cluster; perspectives populated where ideologically split. Refresh against the saved digest surfaced 3 genuinely new clusters not in the morning digest (tax cuts, Ukraine grain in Israel, Kimmel "widow joke" backlash). Confirmed morning record was not overwritten.

### Synthesis prompt revision — fuller X trending sections

User noted the X trending sections (~5 sentences each, ~800 chars) were too compressed given the raw search outputs were ~5k chars. Updated rule 8 in `_SYNTHESIS_SYSTEM`: removed the 2-4 sentence cap; instructed 600-1200 words organized by mini-topic with paragraphs/bullet groupings; capture micro-trends, memes, notable handles, niche debates, sports/cultural moments, mood; use specific examples (handles, post counts, numbers); SA section steered to uniquely SA discourse, skip global news echoes.

Re-verified live: trending sections came in at ~300 words each (model naturally tighter than the 1200 cap, which is fine — better high-quality 300 than padded 800). Quality jumped: named handles, engagement numbers, meta-dynamics (e.g. fringe content getting ratio'd), real mood reads.

### Token usage measurement (instrumented onboard run)

Per-call breakdown (with 2 RSS feeds, 1 tracked story):

| Call | Input | Output | Reasoning | Cached | Output content |
|---|---|---|---|---|---|
| `x_search` global | 22,139 | 858 | 3,629 | 9,152 | 4.1k chars |
| `x_search` SA | 27,142 | 601 | 2,614 | 11,520 | 2.9k chars |
| `web_search` gaps | 19,473 | 584 | 1,908 | 1,344 | 2.7k chars |
| `synthesize` | 7,515 | 2,807 | 5,908 | 64 | 14.2k chars |
| **TOTAL** | **76,269** | **4,850** | **14,059** | **22,080** | |

Key insight: each search call pulls 20-27k input tokens because the API includes raw search results in what the model re-reads during tool use. Our prompt is tiny; we pay for Grok reading what it just searched. **Synthesis is small (7.5k input).**

Scaling implication: RSS only affects synthesis input. 2 feeds → 7.5k tokens; estimated 20 feeds → ~28k; 50 feeds → ~65k. All comfortably within Grok-4.20's context. **Adding RSS sources is essentially free** — the three search calls cost the same regardless of feed count.

User accepted the cost as reasonable, will monitor actual spend.

## Key Files Affected

- MODIFIED `env_settings.py` — added `SettingsConfigDict(env_file=".env", extra="ignore")` so `.env` is actually read.
- MODIFIED `src/models/news/config.py` — defaults: `xai_model="grok-4.20-reasoning"`, `synthesis_model="grok-4.20-reasoning"`.
- MODIFIED `src/utils/news.py` — added `_get_xai_client`, `_xai_search_call`, `x_search_global`, `x_search_local`, `web_search_gaps`, `_SynthesisOutput`, `_SYNTHESIS_SYSTEM` (10 rules), three prompt-formatter helpers, `synthesize_newspaper`, `_BreakingOutput`, `_REFRESH_SYSTEM`, `synthesize_breaking`, `apply_tracked_story_updates`.
- MODIFIED `src/utils/pause.py` — added `"news"` to all three `Literal` type annotations.
- NEW `src/commands/news/track.py` — `track`, `untrack`, `stories` (module-level functions, not yet a Typer subapp; wiring happens in Task 5).
- NEW `src/commands/news/onboard.py` — `onboard`, `refresh`, plus several private display helpers (`_print_cluster`, `_print_categorized_clusters`, `_print_x_section`, `_print_tracked_updates`, `_print_agent_instructions`, `_print_action_required`).

## Errors and Barriers

Two gaps surfaced at end-of-session that should be fixed before Task 4 is finalized. They are NOT blockers — the system works — but they are real correctness issues for the user's stated use case ("track this story over time"; "don't show me yesterday's news again"). Both fixes are pure prompt edits, no architectural change.

### 1. Tracked stories are NOT actively searched

In the current pipeline, `tracked_stories` is loaded and passed only into `synthesize_newspaper`. The three sourcing calls (`x_search_global`, `x_search_local`, `web_search_gaps`) have fixed prompts that do not know about the user's tracked stories. So tracking only works **passively** — if the searches happen to surface something about a tracked topic, synthesis matches it via free-text. On a quiet news day for that topic, the user gets no update for it, even though something might exist if we had explicitly looked.

**Recommended fix (cheap option):** inject the active tracked-story slugs + descriptions into each existing search prompt. Something like: `"ALSO specifically check for any developments on these tracked topics: war_in_iran (description...), openai_ipo (description...)."` No new calls. ~200 more tokens per sourcing call. Grok will give them attention as part of its existing tool use.

**Alternative (thorough but more expensive):** add a fourth sourcing call dedicated to tracked stories — one search per story or one batched call. Adds ~$0.05-0.10 per onboard and ~30s latency.

User signalled preference for the cheap option but did not finalize.

### 2. Continuity (anti-repetition) is only partially enforced

The synthesis prompt passes the last 3 days' records via `_format_recent_records_for_prompt` and the system prompt rule 5 says: *"Note which stories are continuations from recent records."* But there is **no explicit anti-repetition rule** — nothing that says "skip topics that appear in recent records with no new development."

Real news cycles naturally repeat with new angles; Grok is smart enough to phrase day-2 coverage as "Iran blockade enters week 2 with..." rather than verbatim restating. But on quiet days with zero new info on a story, the current prompt may still re-cluster it.

**Recommended fix:** add one rule to `_SYNTHESIS_SYSTEM`: *"If a topic appears in recent records with no new development since, omit it. Continuations are only included when there is genuinely new information; frame those explicitly as continuations rather than fresh news."*

User asked for both gaps to be flagged here for next-session pickup.

## What Comes Next

### Immediate (next session, before declaring Task 4 done)

1. **Inject tracked stories into the three sourcing prompts** — pure prompt edit in `src/utils/news.py`. Add a new optional `tracked_stories: list[TrackedStory]` parameter to `_xai_search_call` (or to each of the three sourcing functions) and append a "ALSO check for these tracked topics" block when present. Onboard already loads tracked stories before the sourcing phase; thread them through.
2. **Tighten continuity in synthesis** — add the anti-repetition rule to `_SYNTHESIS_SYSTEM` rule 5 (or as a new rule).
3. **Re-verify with one onboard run** to confirm both behaviors land cleanly. Delete artifacts.
4. **Mark Task 4 complete.**

### Remaining spec tasks

5. Task 5 — Main app wiring + pause CLI integration:
   - NEW `src/commands/news/main.py` — typer app, register `onboard`, `refresh` from `onboard.py`, register `track`, `untrack`, `stories` from `track.py`.
   - MODIFY `main.py` (project root) — `app.add_typer(news_app, name="news", help="Daily news aggregation")`.
   - MODIFY `src/commands/pause/main.py` — add `nexus pause news --until YYYY-MM-DD` command following the existing pause learn/self/manage pattern.
6. Task 6 — Agent instructions + default sources config:
   - NEW `src/commands/news/agent_instructions.md` — relay newspaper to Benjamin via Telegram, onboard/refresh flow, story tracking handoff (`nexus news track "..."`), untrack, response pattern (present, then STOP, no back-and-forth). Drop any mention of `source` add/remove (we cut those commands).
   - NEW `news/config.toml` — curated default source list. The Reuters/Daily Maverick URLs from the original spec are stale (verified last session) — re-research current URLs. Set `xai_model = "grok-4.20-reasoning"` and `synthesis_model = "grok-4.20-reasoning"` as defaults.

No blockers.
