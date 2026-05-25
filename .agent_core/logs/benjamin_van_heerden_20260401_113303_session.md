---
created_at: '2026-04-01T11:33:03.019139'
username: benjamin_van_heerden
---
# Work Log - Add refresh commands to self and learn systems

## Overarching Goals

Apply the "refresh" primitive from `nexus manage` to the `nexus self` and `nexus learn` systems. The refresh command provides a lightweight state dump for agents that already have session context from a prior onboard — no system intro, no full agent instructions, just current state and a condensed "what to do next" instruction set.

## What Was Accomplished

### Added `nexus self refresh` command
Created `refresh()` in `src/commands/self/onboard.py` that outputs:
- Date context (day of week, week number, days remaining)
- Per-habit status: reading (active books + stale detection), exercise (weekly sessions), mental math (weekly avg), learning (check-ins + streak)
- Weekly overview with status emojis against targets
- Condensed 5-point priority instruction set

### Added `nexus learn refresh` command
Created `refresh()` in `src/commands/learn/onboard.py` that outputs:
- Date + active topic/subtopic/phase
- Phase progress listing
- Current goal with task statuses and file paths
- Exercise balance (compact single-line format)
- Weekly session summary
- Last session highlight (capped at 10 lines of body)
- Condensed 5-point instruction set for exercise workflow

### Wired up both commands
Updated `src/commands/self/main.py` and `src/commands/learn/main.py` to import and register the refresh commands.

## Key Files Affected

- `src/commands/self/onboard.py` — added `refresh()` function
- `src/commands/self/main.py` — imported and registered refresh command
- `src/commands/learn/onboard.py` — added `refresh()` function
- `src/commands/learn/main.py` — imported and registered refresh command

## What Comes Next

- Test all three systems (self, learn, manage) with real data to verify refresh output quality
- OpenClaw skill definitions so the Telegram agent can invoke onboard/refresh via cron
- Consider the `nexus pause` todo — pausing subsystems affects what refresh should display
