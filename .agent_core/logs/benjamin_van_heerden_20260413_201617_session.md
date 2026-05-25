---
created_at: '2026-04-13T20:16:17.185580'
username: benjamin_van_heerden
---
# Work Log - Fix topic rotation timing and refactor learn config

## Overarching Goals

Investigate and fix issues with the nexus learn system that surfaced when the OpenClaw agent ran commands incorrectly: topic changeover happened on Sunday instead of Monday, and `goal complete` operated on the wrong topic (math-physics instead of elixir) due to a silent topic rotation.

## What Was Accomplished

### Fixed topic changeover day (Sunday → Monday)
- Changed `get_week_start()` in `src/commands/learn/topic.py` from Sunday-based (`isoweekday() % 7`) to Monday-based (`weekday()`)

### Reverted accidental goal completion
- `learn/math-physics/foundations/calculus/phase.toml`: restored "language" goal to `in_progress`, "change" to `todo`, `current_goal` back to "language"
- The elixir phase (`abstractions-and-supervision`) was untouched by the bug — still correctly has open tasks from Saturday

### Refactored learn.toml topic config
Replaced the flat `[weights]` dict + `window_size` with a structured `[[topics]]` array:
- Each topic now has `name`, `weight`, and `active` fields
- `active = false` removes a topic from rotation without deleting it
- `window_size` removed — now derived automatically as `sum(active weights)` for perfect proportional resolution

### Separated history into its own file
- Moved topic rotation history from `learn.toml` to `learn/history.toml` as a flat inline array for readability
- `learn.toml` now only contains `current_topic` and `[[topics]]` config

### Model changes
- `src/models/learn/learn.py`: added `TopicWeight` model, `TopicHistory` model, removed `weights` dict and `window_size` from `LearnConfig`, added `active_weights()` and `all_weights()` helpers
- `src/utils/learn.py`: added `load_topic_history()` and `save_topic_history()`

### Updated all topic commands
- `pick_topic()`: no longer takes `window_size` param, derives it internally
- `ensure_topic_for_week()`: filters history and weights to active-only before picking
- `weights` command: shows active/inactive status per topic
- `list` command: shows `(inactive)` marker
- `new`/`delete` commands: work with `TopicWeight` list instead of dict

## Key Files Affected

- `src/commands/learn/topic.py` — week start fix, all commands updated for new config structure
- `src/models/learn/learn.py` — TopicWeight, TopicHistory models, removed window_size
- `src/utils/learn.py` — load/save for topic history
- `learn/learn.toml` — migrated to [[topics]] format, history removed
- `learn/history.toml` (new) — topic rotation history
- `learn/math-physics/foundations/calculus/phase.toml` — reverted accidental goal completion

## What Comes Next

- The `--topic`/`--subtopic` override flags on mutating commands (goal complete, task new, etc.) still allow cross-topic mutations — this was discussed but intentionally kept for now since the overrides are useful
- Test the updated system with a real agent session to confirm Monday changeover works correctly
- The `nexus_news_command` spec is still available (0/6 tasks, worktree exists)
