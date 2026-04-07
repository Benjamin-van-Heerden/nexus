---
title: Models and directory scaffolding
status: todo
created_at: '2026-04-07T15:19:59.526111'
updated_at: '2026-04-07T15:19:59.526111'
completed_at: null
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