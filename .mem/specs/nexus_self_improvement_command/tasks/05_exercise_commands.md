---
title: Exercise commands
status: todo
created_at: '2026-03-31T11:23:17.771649'
updated_at: '2026-03-31T11:23:17.771649'
completed_at: null
---
Create src/commands/self_improvement/exercise.py with a typer app for exercise habit tracking.

IMPORTANT CONTEXT: Exercise tracking is intentionally simple. All sessions go into a single file: self/exercise/log.toml as a [[sessions]] array. The agent provides motivation and accountability, not workout programming. Use typer patterns from src/commands/learn/.

**Commands:**

nexus self exercise log:
- Append an exercise session to self/exercise/log.toml
- Required flags: --type (str, e.g. 'gym', 'run', 'swim'), --description (str, freeform), --intensity (choice: easy/moderate/hard), --duration (int, minutes)
- Date is always today (auto-set)
- Print confirmation with this weeks session count vs goal text from habits.toml

nexus self exercise status:
- Show this weeks sessions (ISO week, Mon-Sun): date, type, intensity, duration for each
- Show count: 'Sessions this week: 2/goal' (print the goal text, not a number — the goal is natural language from habits.toml)
- Show which days this week had sessions vs which didnt
- If no sessions this week, print the goal and a note that no sessions have been logged

nexus self exercise history:
- Show recent sessions, default last 4 weeks (--weeks flag to override)
- Group by ISO week, show weekly session counts
- Show per-session: date, type, description (truncated), intensity, duration