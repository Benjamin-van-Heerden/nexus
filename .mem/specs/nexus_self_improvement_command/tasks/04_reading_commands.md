---
title: Reading commands
status: todo
created_at: '2026-03-31T11:22:57.528277'
updated_at: '2026-03-31T11:22:57.528277'
completed_at: null
---
Create src/commands/self_improvement/read.py with a typer app for reading habit tracking.

IMPORTANT CONTEXT: This project uses typer for CLI. Follow patterns in src/commands/learn/ — use typer.echo() for output, typer.confirm() for destructive ops, raise typer.Exit(1) on errors. No __init__.py files. Use utility functions from src/utils/self_improvement.py for TOML I/O.

Reading is the most complex habit. Each book gets its own TOML file in self/reading/active/<slug>.toml. Sessions are appended as [[sessions]] arrays in the book TOML. The agent (not the user) writes session records after a comprehension discussion — the CLI just provides the logging commands.

**Commands:**

nexus self read new 'title' --author 'name':
- Create self/reading/active/<slug>.toml with: name, author, slug, started=today, status='active', current_section (optional --section flag, default ''), total_sections (optional --total flag, default '')
- Print confirmation with the book slug for future reference

nexus self read list:
- List all active books: name, author, current_section, last session date (or 'No sessions yet'), number of sessions
- If no active books, print hint to create one

nexus self read show <slug>:
- Show full book details: name, author, started, current_section, total_sections
- Show last 3 sessions with date, section, summary (truncated to 100 chars), takeaway (truncated)
- Show total session count

nexus self read log <slug>:
- Append a reading session to the book. Required flags: --section, --summary, --takeaway. Optional repeatable flag: --question (for agent_questions list)
- Update the books current_section to the value of --section
- Print confirmation

nexus self read complete <slug>:
- Set status='completed' on the book
- Move the TOML file from self/reading/active/ to self/reading/completed/
- Print confirmation with total sessions and date range

nexus self read history:
- List completed books: name, author, started, completed date (from last session or file mtime), total sessions