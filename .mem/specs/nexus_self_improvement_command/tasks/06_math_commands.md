---
title: Math commands
status: completed
created_at: '2026-03-31T11:24:21.473293'
updated_at: '2026-03-31T15:52:23.331710'
completed_at: '2026-03-31T15:52:23.331703'
---
Create src/commands/self_improvement/math.py with a typer app for mental math tracking.

IMPORTANT CONTEXT: The math system has two parts — problem generation (handled by math_generator.py, already created in a prior task) and performance logging/tracking. The user solves problems on paper/in head and self-reports time and accuracy. The agent adjusts self/math/config.toml over time based on trends. Use typer patterns from src/commands/learn/.

**Commands:**

nexus self math generate:
- Call generate_problems() from math_generator.py
- Print the formatted problems to stdout
- This is also called by onboard, but exists as a standalone command too

nexus self math log:
- Log a math session to self/math/log.toml
- Required flags: --time (str, 'M:SS' format e.g. '3:20'), --correct (int, number correct)
- Parse --time using parse_duration() from utils to get time_seconds
- Total is always config.general.problems_per_day (read from config)
- Date is always today
- problem_types: if generate was run today (check if onboard was run), store the types. Otherwise store empty list — this is a best-effort field. Actually, the simplest approach: run generate_problems() to get the types list (it is deterministic per day if we seed with the date, but we dont need to — just store what was generated). Since generate and log happen in different commands/sessions, just store an empty list for problem_types. The agent can fill it in from context if it wants by passing --types flag.
- Optional repeatable flag: --type (str, problem type names to record, e.g. --type multiplication --type addition)
- Print confirmation with time formatted, accuracy as fraction, and comparison to recent average

nexus self math status:
- Show recent performance (last 2 weeks of sessions)
- Per session: date, time (formatted), correct/total
- Averages: this week avg time, last week avg time, trend direction (improving/declining/stable)
- Current config summary: which types enabled, weights, digit ranges

nexus self math config:
- Print the current self/math/config.toml in a readable format
- Show each problem type: enabled, weight, digit range, trailing zeros chance
- This is informational only — the agent modifies the config directly by editing the TOML file, no CLI command needed for that

## Completion Notes

Created math.py with generate, log, status, config commands. Duration parsing, trend analysis, config display.