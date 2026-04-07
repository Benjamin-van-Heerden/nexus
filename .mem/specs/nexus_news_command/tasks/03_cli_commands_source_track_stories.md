---
title: CLI commands — source, track, stories
status: todo
created_at: '2026-04-07T15:20:38.303729'
updated_at: '2026-04-07T15:20:38.303729'
completed_at: null
---
Create the CRUD commands for managing sources and tracked stories.

FILE: src/commands/news/source.py
- app = typer.Typer()
- nexus news source add <url> --name 'Name' --category 'category' --lean 'center' — adds SourceEntry to config, saves
- nexus news source remove <name-or-url> — removes by name or URL match, saves
- nexus news source list — prints all sources grouped by category, showing name, URL, lean

FILE: src/commands/news/track.py
- app = typer.Typer()  (or just commands on the main news app)
- nexus news track 'description' — creates TrackedStory with slugified description, saves to news/stories/<slug>.toml
- nexus news untrack <slug> — sets active=False on the story, saves
- nexus news stories — lists all tracked stories (active and inactive), showing description, created date, last updated, number of developments

Follow existing CLI patterns from src/commands/manage/task.py and src/commands/manage/contact.py for reference.