---
title: Models and directory scaffolding
status: completed
created_at: '2026-04-07T15:19:59.526111'
updated_at: '2026-04-16T11:41:23.343217'
completed_at: '2026-04-16T11:41:23.343205'
---
Create all Pydantic models and directory structure for the news system.

NEW FILES:
- src/models/news/config.py — NewsConfig (sources list, xai_model, history_days, categories), SourceEntry (name, url, category, lean)
- src/models/news/digest.py — DailyDigest (date, generated_at, story_clusters, x_trending_global, x_trending_sa, tracked_story_updates), StoryCluster (slug, headline, category, summary, perspectives, tracked_story, sources_count), PerspectiveEntry (lean, source, summary)
- src/models/news/story.py — TrackedStory (slug, description, created, last_updated, developments list, active flag)

MODIFY:
- src/models/pause.py — add 'news: PauseEntry = PauseEntry()' to PauseConfig
- src/utils/paths.py — add get_news_dir() -> Path returning get_project_root() / 'news'

CREATE DIRECTORIES:
- news/ (data dir at project root)
- news/records/
- news/stories/

Ensure all models use the same patterns as existing models (Pydantic BaseModel, date/datetime types, Optional via | None).

## Completion Notes

Created src/models/news/ with config.py (SourceEntry, NewsConfig), digest.py (PerspectiveEntry, StoryCluster, TrackedStoryUpdate, DailyDigest), and story.py (TrackedStory).

Divergences from the spec (both minor, both for type safety and to reflect the user's architectural direction):
- Added synthesis_model: str = '' field to NewsConfig alongside xai_model, since the user wants a different AI for synthesis than the one used for sourcing (xAI). Default left empty so the user configures it explicitly.
- Made TrackedStoryUpdate a typed Pydantic model (slug, headline, development) instead of list[dict] as shown in the spec — cleaner for the feedback loops the user wants to build.

Pause integration:
- Added news: PauseEntry = PauseEntry() to PauseConfig in src/models/pause.py. Note: the pause CLI command wiring (nexus pause news --until ...) is in task 5, not here.

Paths:
- Added get_news_dir() -> Path in src/utils/paths.py returning get_project_root() / 'news'.

Directories:
- Created news/records/ and news/stories/ with .gitkeep files (following the self/reading/completed and self/weekly convention). The top-level news/ dir is implicit.

Verified via feedback loop: ran uv run python that imports every new model, instantiates each with realistic data (BBC source, a story cluster with perspectives, a tracked story update, a TrackedStory), and confirms PauseConfig().news works and get_news_dir() resolves. All clean.