---
created_at: '2026-03-31T15:52:50'
username: benjamin_van_heerden
spec_slug: nexus_management_command
---
# Work Log - Build nexus manage command

## Overarching Goals

Build the `nexus manage` command — a personal management system for tasks, contacts, and Google Calendar integration. The system handles todos, scheduled events, recurring tasks, subtask hierarchies, contact management with birthday reminders, and bidirectional gcal sync.

## What Was Accomplished

### Pydantic Models
Created `src/models/management/` with TaskConfig, ContactConfig, IndexEntry, and ManageIndex models following existing learn system patterns.

### Utility Module
Created `src/utils/management.py` with TOML I/O helpers, index management (add/remove/update), slug resolution, custom 3-field cron parser (`parse_recurrence`, `next_occurrence`, `is_due_in_window`), task tree helpers (`get_subtasks`, `get_task_tree`, `move_to_completed`), and contact slug resolution. Added `get_management_dir()` to `src/utils/paths.py`.

### Task CRUD Commands
Created `src/commands/manage/task.py` with 6 commands: `new` (with --due, --recur, --parent, --tag, --description), `list` (tree view with --flat, --tag, --due filters), `show` (full details + subtask tree), `complete` (subtask guard, recurring task handling), `edit`, `delete`.

### Contact CRUD Commands
Created `src/commands/manage/contact.py` with 5 commands: `new`, `list`, `show`, `edit` (including --info-key/--info-value for freeform data), `delete`.

### App Wiring
Created `src/commands/manage/main.py` wiring all sub-typers. Updated root `main.py` to add management app. Created `management/` directory structure (tasks/, completed/, contacts/, sync/).

### Onboard, Refresh, and Upcoming Commands
Created `src/commands/manage/onboard.py` with three commands:
- `onboard` — full agent context dump with user info, sync status, all actionable sections, task tree, and full agent instructions
- `refresh` — lightweight version for follow-up sessions with same data sections plus condensed instructions (no full agent_instructions.md)
- `upcoming` — quick lookahead with --days option

Reminder windows: birthdays at 7/2/1/0 days, tasks from 1 day out (tomorrow/today), recurring on day-of only, open todos always shown. "This week" section for 2-7 days out.

### Google Calendar Sync
Created `src/commands/manage/sync.py` with `auth google` (OAuth flow) and `sync` (bidirectional):
- Pull window: 14 days back, 30 days forward
- Birthday events filtered out (handled by nexus contacts)
- Past events without existing nexus tasks auto-completed
- Event metadata extracted (description, location, meeting links)
- Calendar hardcoded to `benjaminvh1997@gmail.com`

### Agent Instructions
Created `src/commands/manage/agent_instructions.md` — concise instructions for the OpenClaw agent with priority order, key rules, gcal sync guidance, and command reference.

## Key Files Affected

- `src/models/management/task.py` — TaskConfig model
- `src/models/management/contact.py` — ContactConfig model
- `src/models/management/index.py` — IndexEntry, ManageIndex models
- `src/utils/management.py` — All utility functions
- `src/utils/paths.py` — Added get_management_dir()
- `src/commands/manage/task.py` — Task CRUD commands
- `src/commands/manage/contact.py` — Contact CRUD commands
- `src/commands/manage/onboard.py` — Onboard, refresh, upcoming commands
- `src/commands/manage/sync.py` — Google Calendar auth and sync
- `src/commands/manage/main.py` — App wiring
- `src/commands/manage/agent_instructions.md` — Agent instructions
- `main.py` — Root app wiring
- `management/index.toml` — Task index file

## What Comes Next

- All 8 spec tasks completed. Spec ready for completion.
- Future work: OpenClaw skill definition (SKILL.md) for the management system
- Consider adding the management system to the main nexus onboard flow
