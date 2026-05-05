---
title: CLI commands — source, track, stories
status: completed
created_at: '2026-04-07T15:20:38.303729'
updated_at: '2026-04-29T15:47:45.233685'
completed_at: '2026-04-29T15:47:45.233672'
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

## Completion Notes

Scope adjusted with the user: dropped the `source` commands entirely. RSS source CRUD via CLI is low-value compared to editing news/config.toml directly (rare operation, requires URL on hand anyway, agent-driven adds are awkward). Task reduced to track/untrack/stories.

## Created src/commands/news/track.py

Three module-level functions (not a Typer subapp — they will be wired as top-level commands on the news app in Task 5, matching the manage/onboard/refresh/upcoming/sync pattern in src/commands/manage/main.py):

### track(description, --slug)
- Slug derivation: explicit --slug wins (slugified for safety); else auto-derived from first 6 words of description (e.g. "The war in Iran and ongoing nuclear negotiations" -> the_war_in_iran_and_ongoing). The 6-word cap prevents giant slugs from long descriptions.
- Refuses empty/whitespace descriptions.
- Refuses duplicates with a helpful message pointing to `nexus news stories`.
- On success creates TrackedStory(slug, description, created=today) and saves via save_tracked_story (which goes through _save_toml -> news/stories/<slug>.toml).

### untrack(slug)
- Slugifies the input for safety (so users can pass either the canonical slug or a near-form).
- Errors with exit 1 if no story with that slug exists.
- Idempotent: prints "Already inactive: <slug>" if already deactivated, no error.
- Otherwise sets story.active = False, saves, prints "Untracked: <slug>".

### stories()
- Lists all (active and inactive) via list_tracked_stories(active_only=False).
- Splits into "Active (N):" and "Inactive (N):" sections, each with slug, description, created, last_updated (or "never"), and development count per story.
- Prints "No tracked stories." if none exist.

## Verified via typer.testing.CliRunner

Built a temporary Typer app registering the three functions and exercised:
- empty list
- empty-description rejection (exit 1)
- auto-slug derivation
- explicit --slug
- duplicate-slug rejection (exit 1, helpful message)
- untrack toggles active flag
- untrack idempotency on already-inactive
- untrack-nonexistent error (exit 1)
- mixed active/inactive listing renders correctly

All test TOML files cleaned up from news/stories/.

## Notes for downstream tasks

- These functions are not yet wired into a Typer app — that happens in Task 5 (main app wiring). The wiring will be: `news_app.command(name="track")(track)` etc.
- Task 6 (agent_instructions.md) needs to drop any mention of source add/remove and instead document only track/untrack/stories for the agent-driven flow ("keep tabs on X" -> nexus news track "X").