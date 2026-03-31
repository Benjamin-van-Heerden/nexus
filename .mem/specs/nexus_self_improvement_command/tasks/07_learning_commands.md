---
title: Learning commands
status: completed
created_at: '2026-03-31T11:25:06.427091'
updated_at: '2026-03-31T15:52:30.249682'
completed_at: '2026-03-31T15:52:30.249676'
---
Create src/commands/self_improvement/learn.py with a typer app for daily learning check-in tracking.

IMPORTANT CONTEXT: Learning tracking is standalone — it does NOT derive from nexus learn records. The nexus self system and nexus learn system are completely independent. This is a simple daily yes/no check-in with optional notes. All sessions go in self/learning/log.toml. Use typer patterns from src/commands/learn/.

**Commands:**

nexus self learn log:
- Append a learning session to self/learning/log.toml
- By default: did_learn=True, date=today
- Optional flag: --notes (str, freeform description of what was learned)
- Optional flag: --skip — sets did_learn=False (explicitly logging that no learning happened today, useful for agent accountability tracking)
- If a session for today already exists, warn and ask to overwrite (typer.confirm)
- Print confirmation with current streak info

nexus self learn status:
- Show this weeks check-ins: which days have entries, did_learn value for each
- Show streak: consecutive days with did_learn=True ending today (or yesterday if today not yet logged)
- Show the goal text from habits.toml
- Show missing days this week (days with no entry at all)

## Completion Notes

Created learn.py with log (overwrite protection, skip flag) and status (streak calc, missing days) commands.