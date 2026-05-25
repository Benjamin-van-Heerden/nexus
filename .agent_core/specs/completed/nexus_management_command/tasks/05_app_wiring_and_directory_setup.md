---
title: App wiring and directory setup
status: completed
created_at: '2026-03-31T09:14:45.409019'
updated_at: '2026-03-31T10:58:34.160286'
completed_at: '2026-03-31T10:58:34.160280'
---
Wire up the management app:

1. Create src/commands/management/main.py — typer app that adds task.py and contact.py as sub-typers, plus onboard, upcoming, sync, and auth as commands (onboard/upcoming/sync/auth will be wired in later tasks, just import placeholders or skip for now)

2. Update root main.py — add: from src.commands.management.main import app as management_app, then app.add_typer(management_app, name='manage', help='Personal management commands')

3. Create management/ directory structure if not exists: management/tasks/, management/completed/, management/contacts/, management/sync/. Create empty management/index.toml with: [no content, or just a comment]

4. Add get_management_dir(), get_tasks_dir(), get_completed_dir(), get_contacts_dir(), get_sync_dir() to src/utils/paths.py (following existing pattern with get_project_root())

## Completion Notes

Created src/commands/management/main.py wiring task and contact sub-typers. Updated root main.py to add management_app as 'manage' sub-typer. Created management/ directory structure (tasks/, completed/, contacts/, sync/) with .gitkeep files and empty index.toml. get_management_dir() was already in paths.py from utility task.