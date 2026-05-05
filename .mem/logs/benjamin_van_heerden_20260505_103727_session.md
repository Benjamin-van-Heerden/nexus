---
created_at: '2026-05-05T10:37:27.022135'
username: benjamin_van_heerden
spec_slug: nexus_news_command
---
# Work Log - Finished `nexus news` spec

## Overarching Goals

Finish the remaining `nexus_news_command` spec tasks and bring the news system to a usable end-to-end state:

- Complete the onboard/refresh behavior gaps identified in the prior session.
- Wire `nexus news` into the main CLI and pause system.
- Seed real RSS sources and add practical context/freshness safeguards.
- Encode Benjamin's editorial calibration around anti-Trump, anti-West, and anti-American framing risks.
- Add agent-facing instructions so the Telegram/OpenClaw consumer can run the system correctly.
- Verify the system with live RSS and one real xAI API onboard run.

## What Was Accomplished

### Completed Task 4 — Onboard and refresh commands

Closed the two correctness gaps from the previous session:

- Active tracked stories are now injected into `x_search_global`, `x_search_local`, `web_search_gaps`, and refresh-time X searches. This makes tracked stories actively searched rather than only passively matched during synthesis.
- The synthesis prompt now explicitly omits topics from recent records unless there is a meaningful new development, and frames real continuations as continuations.

Verified the changes with:

- `uvx ty check src/utils/news.py src/commands/news/onboard.py`
- A focused `uv run python` import/signature check for the tracked-topic prompt helper and updated search functions.

### Switched xAI model default

Updated `NewsConfig` defaults and `news/config.toml` to use:

- `xai_model = "grok-4.3"`
- `synthesis_model = "grok-4.3"`

Validated config loading with `uv run python`.

### Added RSS safeguards and source-name auditability

Added config-driven RSS caps/freshness filters:

- `max_entries_per_source = 30`
- `max_total_entries = 250`
- `max_entry_age_hours = 72`

Threaded these through `fetch_all_feeds`, `fetch_all_feeds_sync`, and `onboard()`.

Added date parsing helpers for RSS freshness filtering, handling RFC822-style dates and ISO timestamps.

Added `source_names: list[str]` to `StoryCluster`, updated the synthesis prompt to populate it, and updated newspaper output to print sources per cluster when available. This gives a better audit trail for which sources drove each story.

After a live onboard run exposed over-clustering (only 8 clusters and an unrelated Supreme Court merge), tightened the synthesis prompt:

- Do not merge unrelated stories merely because they share a source, institution, country, category, person, or broad theme.
- Aim for 12-25 high-signal clusters with a normal 10-15 source configuration.
- Keep the digest tight but not sparse.

### Seeded default RSS config

Created `news/config.toml` with live-tested feeds across categories:

- US politics, left/center-left: NPR Politics, The Guardian US Politics
- US politics, right/center-right: Fox News Politics, The Hill News
- International: BBC World, Al Jazeera, Deutsche Welle
- Economics: MarketWatch
- Technology: Ars Technica, Hacker News
- Science: ScienceDaily
- Entertainment: Variety
- South Africa: Daily Maverick

Live feed probe confirmed the seeded config fetched 250 capped entries across 13 configured sources.

Broken or stale candidate feeds were deliberately not seeded:

- News24 candidate RSS URLs returned 404.
- EWN candidate RSS URL returned 404.
- TimesLIVE candidate RSS URL returned 404.

### Added editorial calibration

Added `editorial_profile: str = ""` to `NewsConfig` and seeded `news/config.toml` with Benjamin's calibration:

- Keep broad source coverage.
- Treat some modern left-leaning coverage as prone to anti-Trump, anti-West, and anti-American framing.
- Do not discard those sources.
- Distinguish reported facts from interpretive framing.
- Flag loaded language, selective context, activist premises, and emotionally charged anti-Trump / anti-West assumptions when material.

Threaded this editorial profile into both full synthesis and refresh prompts. The prompt now applies it as calibration, not permission to distort facts or replace one ideological frame with another.

### Ran a real xAI onboard

With Benjamin's permission, ran the full onboard pipeline:

- RSS fetch: 250 headlines.
- Global X search: returned a compact discourse summary.
- South Africa X search: returned local discourse summary.
- Web search gaps: returned under-covered/breaking stories.
- Synthesis: produced a saved daily digest.

Record saved:

- `news/records/2026-05-05.toml`

The run verified the pipeline works end to end. It also revealed the over-clustering issue described above, which was fixed by prompt changes after the run.

### Completed Task 5 — Main app wiring and pause integration

Added `src/commands/news/main.py` and wired:

- `nexus news onboard`
- `nexus news refresh`
- `nexus news track`
- `nexus news untrack`
- `nexus news stories`

Updated root `main.py` to register:

- `nexus news`

Updated pause CLI:

- Added `nexus pause news --until YYYY-MM-DD [--reason ...]`.
- Included `news` in pause status output.
- Included `news` in resume validation.
- Replaced the old type-ignore path with an explicit `FeatureName` `Literal` and `cast`.

Verified with:

- `uvx ty check main.py src/commands/news/main.py src/commands/pause/main.py`
- Typer `CliRunner` help checks for `news`, `news track`, `news refresh`, and `pause news`.

### Completed Task 6 — Agent instructions and default sources config

Added `src/commands/news/agent_instructions.md` covering:

- Purpose: relay the generated newspaper to Benjamin via Telegram.
- Daily onboard flow: run `nexus news onboard`, present the output, stop.
- Refresh flow: run `nexus news refresh`, relay only breaking/developing material, stop.
- Story tracking: run `nexus news track "description"` for "keep tabs on X" requests.
- Untracking: list stories if needed, then run `nexus news untrack <slug>`.
- Source management: sources live in `news/config.toml`; no source CLI exists.
- Editorial calibration: respect the config profile while preserving factual accuracy.
- Response pattern: concise, perspective-aware, no debate loop, present then stop.

Final verification:

- `uvx ty check main.py src/commands/news/main.py src/commands/news/onboard.py src/commands/pause/main.py src/models/news/config.py src/models/news/digest.py src/utils/news.py`
- Focused `uv run python` check that loaded config, performed a capped RSS fetch, confirmed agent instructions exist, and validated news/pause CLI help.

## Key Files Affected

- `src/utils/news.py` — tracked-story injection into search prompts; RSS caps/freshness filtering; stronger synthesis prompt; editorial profile injection; richer recent-record context; source-name synthesis instruction.
- `src/commands/news/onboard.py` — uses RSS caps from config; passes tracked stories into all sourcing calls; prints source names.
- `src/commands/news/main.py` — new Typer app wiring for news commands.
- `src/commands/news/agent_instructions.md` — new agent-facing instructions.
- `src/commands/news/track.py` — existing tracked-story commands used by new news app.
- `src/models/news/config.py` — `grok-4.3` defaults; RSS cap fields; `editorial_profile`.
- `src/models/news/digest.py` — added `source_names`.
- `src/commands/pause/main.py` — added news pause/resume/status integration.
- `main.py` — registered `news_app`.
- `news/config.toml` — new seeded configuration with live RSS feeds, model settings, RSS caps, and editorial profile.
- `news/records/2026-05-05.toml` — generated by the live onboard verification run.

## Errors and Barriers

- `uv run ruff` failed because ruff is not installed in the project environment.
- `uvx ruff` initially hit sandbox/cache permissions, then stalled while downloading `ruff`; the hung process was stopped. Type checking and focused runtime checks passed, but ruff linting was not completed.
- Some candidate RSS feeds from the original spec were stale or unavailable:
  - News24 candidate URLs returned 404.
  - EWN candidate URL returned 404.
  - TimesLIVE candidate URL returned 404.
- The first live onboard synthesis over-clustered: it produced only 8 clusters from 250 RSS items and merged unrelated Supreme Court stories. The prompt was tightened afterward, but another live onboard should be run later to confirm the new prompt produces the intended 12-25 cluster shape.

## What Comes Next

All tasks in `nexus_news_command` are complete.

Recommended follow-ups after the spec lands:

- Run another `nexus news onboard` after the prompt tightening to confirm the digest now has richer cluster coverage and better separation of unrelated stories.
- Monitor actual xAI spend with `grok-4.3` and tool calls after a few daily runs.
- Add more South African RSS sources if reliable feeds are found, or rely on X/local search plus Daily Maverick for now.
- Consider a dedicated tracked-story search call later if tracked topics need higher recall than the current cheap batched prompt injection.
