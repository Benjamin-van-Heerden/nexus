---
title: nexus management command
status: completed
assigned_to: Benjamin-van-Heerden
issue_id: 5
issue_url: https://github.com/Benjamin-van-Heerden/nexus/issues/5
branch: dev-benjamin_van_heerden-nexus_management_command
pr_url: https://github.com/Benjamin-van-Heerden/nexus/pull/7
created_at: '2026-03-31T09:00:01.166659'
updated_at: '2026-03-31T16:02:10.999500'
completed_at: '2026-03-31T16:02:10.998421'
last_synced_at: '2026-03-31T09:32:10.139861'
local_content_hash: 318d8018ded1c4f836f73f8449d3092d31d0ed075421b84654e4fba0e6de4d32
remote_content_hash: 318d8018ded1c4f836f73f8449d3092d31d0ed075421b84654e4fba0e6de4d32
---
## Overview

Build the `nexus manage` command — a personal management system for tasks, contacts, and calendar integration. The system handles everything from simple open-ended todos to scheduled meetings with due dates, recurring events (birthdays, weekly engagements), and project-like hierarchical task breakdowns. Bidirectional Google Calendar sync ensures external events flow into nexus and nexus-created events push to gcal.

The architecture follows the same patterns as the existing `nexus learn` system: TOML files as state, Pydantic models for validation, typer for CLI, filesystem as the source of truth, and an `onboard` command for agent context.

## Goals

- Unified task model that handles todos, scheduled events, and project breakdowns
- Nested subtask support via filesystem (slug-folder convention) with infinite depth
- Contact management with structured fields and freeform info
- Recurring task support via cron scheduling (day-of-month, month, day-of-week)
- Bidirectional Google Calendar sync (pull meeting invites, push nexus events)
- Agent-friendly `nexus manage onboard` command for the OpenClaw agent
- Consistent with existing nexus patterns (TOML, Pydantic, typer, git sync, ./ path convention)

## Technical Approach

### Directory Structure

```
management/
├── index.toml                          # Flat index of all active task slugs + paths
├── tasks/
│   ├── go_to_dentist.toml              # Task file
│   ├── go_to_dentist/                  # Subtask folder (only exists if subtasks exist)
│   │   ├── make_appointment.toml
│   │   └── make_appointment/
│   │       └── get_dentist_number.toml
│   ├── weekly_standup.toml             # Recurring task
│   └── look_into_laptop.toml           # Open todo (no due date)
├── completed/                          # Completed/past-due tasks moved here (preserving subtree)
├── contacts/
│   ├── john_smith.toml
│   └── mom.toml
└── sync/
    └── sync_state.toml                 # Last sync timestamp, gcal sync metadata
# OAuth credentials in auth/ (gitignored, already exists):
#   auth/client_secret_*.json           # Client credentials
#   auth/token.json                     # Refresh token (created by nexus manage auth google)
```

### Task Model (TOML)

```toml
name = "Go to dentist"
slug = "go_to_dentist"
description = """
Annual checkup. Dr. Smith's office on Main St.
Bring insurance card.
"""
status = "todo"                         # todo | in_progress | completed
created = 2026-03-31
due = 2026-04-15T10:00:00              # Optional: date or datetime
completed_at = 2026-04-15              # Optional: set on completion
tags = ["health", "personal"]           # Optional

# Recurrence (optional) - only day-of-month, month, day-of-week
# Format: "dom month dow" (3 fields from cron)
# Examples: "15 3 *" = March 15 every year, "* * 1" = every Monday
recurrence = ""

# Google Calendar link (optional, set by sync)
gcal_event_id = ""
last_modified = 2026-03-31T09:00:00    # For conflict resolution (latest wins)

# Subtask tracking
has_subtasks = false                    # If true, slug/ directory contains subtask .toml files
parent = ""                             # Empty for top-level, otherwise parent slug
```

### Contact Model (TOML)

```toml
name = "John Smith"
slug = "john_smith"
phone = "+1234567890"
email = "john@example.com"
birthday = 1990-03-15                   # Optional: generates recurring birthday task
relationship = "friend"

[info]
occupation = "Software engineer at Acme"
location = "Cape Town"
notes = """
Met at RustConf 2025.
Enjoys hiking and board games.
"""
```

### Index Model (management/index.toml)

The index is a flat lookup of all active (non-completed) tasks for fast resolution without filesystem traversal.

```toml
[[tasks]]
slug = "go_to_dentist"
name = "Go to dentist"
path = "./management/tasks/go_to_dentist.toml"
due = 2026-04-15T10:00:00
parent = ""

[[tasks]]
slug = "make_appointment"
name = "Make appointment"
path = "./management/tasks/go_to_dentist/make_appointment.toml"
due = 2026-04-10
parent = "go_to_dentist"

[[tasks]]
slug = "get_dentist_number"
name = "Get dentist number"
path = "./management/tasks/go_to_dentist/make_appointment/get_dentist_number.toml"
parent = "make_appointment"
```

### Pydantic Models (src/models/management/)

**task.py:**
- `TaskConfig`: name, slug, description, status (Literal["todo", "in_progress", "completed"]), created (date), due (datetime | date | None), completed_at (date | None), tags (list[str]), recurrence (str), gcal_event_id (str), last_modified (datetime), has_subtasks (bool), parent (str)

**contact.py:**
- `ContactConfig`: name, slug, phone (str), email (str), birthday (date | None), relationship (str), info (dict[str, Any])

**index.py:**
- `IndexEntry`: slug, name, path, due (datetime | date | None), parent (str)
- `ManageIndex`: tasks (list[IndexEntry])

### CLI Commands (src/commands/management/)

```
nexus manage onboard                    # Full context dump for agents
nexus manage task new "title"           # Create task
  --due 2026-04-15                      # Optional due date
  --due 2026-04-15T10:00                # Optional due datetime
  --recur "15 3 *"                      # Optional recurrence
  --parent go_to_dentist                # Optional parent (slug or name)
  --tag health --tag personal           # Optional tags
nexus manage task list                  # List active tasks (tree view)
  --tag health                          # Optional: filter by tag
  --due today|week|month                # Optional: filter by due window
nexus manage task show <slug>           # Show task details + subtask tree
nexus manage task complete <slug>       # Mark completed, move to completed/
nexus manage task edit <slug>           # Edit task fields
  --due 2026-04-20                      # Update due date
  --description "new desc"              # Update description
  --tag newtag                          # Add tag
nexus manage task delete <slug>         # Delete task (with confirmation)
nexus manage contact new "name"         # Create contact
  --phone "+1234567890"
  --email "john@example.com"
  --birthday 1990-03-15
  --relationship "friend"
nexus manage contact list               # List all contacts
nexus manage contact show <slug>        # Show contact details
nexus manage contact edit <slug>        # Edit contact fields
nexus manage contact delete <slug>      # Delete contact
nexus manage upcoming                   # Show upcoming due tasks + birthdays (next 14 days)
nexus manage sync                       # Bidirectional Google Calendar sync
nexus manage auth google                # One-time OAuth setup
```

### Slug Resolution

Slugs are generated from names: lowercase, spaces/special chars replaced with underscores. When a command accepts a slug argument, it can be:
- An exact slug: `go_to_dentist`
- A name (resolved to slug): `"Go to dentist"`

Resolution checks the index first. If ambiguous (multiple matches), error with options.

### Subtask Mechanics

When `--parent` is provided to `task new`:
1. Resolve parent slug via index
2. Create `<parent_slug>/` directory next to `<parent_slug>.toml` (if doesn't exist)
3. Write new task .toml inside that directory
4. Set `has_subtasks = true` on parent task
5. Set `parent = <parent_slug>` on child task
6. Add to index with parent field

On `task complete`:
- If task has subtasks, all subtasks must be completed first (or force with --force)
- Move task .toml and its subtask directory (if any) to `completed/` preserving structure
- Remove from index

### Recurrence Handling

Recurring tasks use a 3-field cron format: `"dom month dow"`
- `"15 3 *"` = March 15 every year (birthday)
- `"* * 1"` = Every Monday (weekly meeting)
- `"1 * *"` = First of every month
- `"* * 1,3,5"` = Monday, Wednesday, Friday

On `onboard` or `upcoming`:
- Calculate next occurrence from cron pattern
- Show as upcoming if within window
- Recurring tasks are never "past due" — they just show the next occurrence

On `task complete` for a recurring task:
- Don't move to completed/ — instead, record the completion date and calculate next due

### Google Calendar Sync

**Setup:**
- Google OAuth credentials already exist at `auth/client_secret_221009037075-mscrrhc8b32ad40ang5ha8rd82ivtmuq.apps.googleusercontent.com.json` (Desktop app / "installed" type). The `auth/` directory is gitignored.
- `nexus manage auth google` reads this credentials file, opens browser for OAuth consent, stores the resulting `token.json` (refresh token) in `auth/` (also gitignored)
- Uses `google-auth-oauthlib` for the flow, `google-api-python-client` for Calendar API

**Sync flow (`nexus manage sync`):**
1. Load last sync timestamp from `sync_state.toml`
2. **Pull** (gcal → nexus):
   - Fetch events modified since last sync
   - For each event with a matching `gcal_event_id` in index: compare `last_modified` — latest wins
   - For new events (no matching nexus task): create task with `gcal_event_id` set, `tags = ["gcal"]`
3. **Push** (nexus → gcal):
   - Find tasks with `due` set and no `gcal_event_id` (or modified since last sync)
   - Create/update gcal events, store `gcal_event_id` back on task
4. **Conflict resolution**: compare `last_modified` (nexus) vs `updated` (gcal) — latest wins, always
5. Update `sync_state.toml` with new timestamp

**sync_state.toml:**
```toml
last_sync = 2026-03-31T09:00:00
calendar_id = "primary"
```

**Dependencies to add:**
- `google-auth-oauthlib` — OAuth flow
- `google-api-python-client` — Calendar API
- `google-auth-httplib2` — HTTP transport for google auth

### Onboard Command

`nexus manage onboard` outputs (in order):
1. **Overdue tasks** — due date passed, not completed, not recurring
2. **Due today** — tasks due today
3. **Due this week** — tasks due in the next 7 days
4. **Upcoming birthdays** — contacts with birthdays in the next 30 days
5. **Upcoming recurring** — next occurrence of recurring tasks within 14 days
6. **Open todos** — tasks with no due date
7. **Task tree** — hierarchical view of all active tasks with subtask nesting
8. **Agent instructions** — read from `src/commands/management/agent_instructions.md`

### File Structure (src/)

```
src/
├── commands/
│   └── management/
│       ├── main.py                     # Typer app wiring
│       ├── task.py                     # Task CRUD commands
│       ├── contact.py                  # Contact CRUD commands
│       ├── onboard.py                  # Agent context dump
│       ├── sync.py                     # Google Calendar sync + auth
│       └── agent_instructions.md       # Agent-facing instructions
├── models/
│   └── management/
│       ├── task.py                     # TaskConfig model
│       ├── contact.py                  # ContactConfig model
│       └── index.py                    # ManageIndex, IndexEntry models
└── utils/
    └── management.py                   # TOML I/O, index management, slug resolution, cron helpers
```

### Wiring in main.py

Add to the root `main.py`:
```python
from src.commands.management.main import app as management_app
app.add_typer(management_app, name="manage", help="Personal management commands")
```

## Success Criteria

- `nexus manage task new/list/show/complete/edit/delete` all work correctly
- Subtask nesting works to arbitrary depth via --parent flag
- `nexus manage contact new/list/show/edit/delete` all work correctly
- Contacts with birthdays generate upcoming reminders
- Recurring tasks show next occurrence, don't get marked "past due"
- `nexus manage onboard` produces a complete context dump suitable for an agent
- Index stays consistent across all task operations (create, complete, delete)
- Completed tasks move to completed/ preserving subtree structure
- `nexus manage auth google` completes OAuth flow and stores tokens
- `nexus manage sync` pulls gcal events and pushes nexus tasks bidirectionally
- Conflict resolution uses latest-wins by comparing timestamps
- All paths use the ./ convention consistent with the rest of nexus
- Git sync (pre/post) works for all management commands (no changes needed — inherited from main.py)
- Tags can be added to tasks and filtered in list commands

## Notes

- The management/ directory already exists (empty) at the project root
- Google Calendar dependencies (`google-auth-oauthlib`, `google-api-python-client`, `google-auth-httplib2`) need to be added — advise user before installing
- `auth/` is already in .gitignore — credentials and tokens are safe
- The sync/ directory in management/ should also be gitignored except for sync_state.toml
- Follow existing patterns exactly: no __init__.py files, typer for CLI, Pydantic for models, tomli_w for TOML writing, tomllib (stdlib) for reading
- All commands should use `typer.echo()` for output, `raise typer.Exit(1)` on errors, `typer.confirm()` for destructive operations
- The cron 3-field format is non-standard — we parse it ourselves, no external cron library needed. Use Python's `calendar` and `datetime` modules
- Contact info section uses `dict[str, Any]` in Pydantic — TOML tables map naturally to this
- mem is completely separate from nexus — don't conflate the two systems
