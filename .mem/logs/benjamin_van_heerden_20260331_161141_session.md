---
created_at: '2026-03-31T14:11:41.771825'
username: benjamin_van_heerden
---
# Work Log - Improve nexus learn onboard for cold-start agents

## Overarching Goals

Make the `nexus learn onboard` command output clear and actionable for an agent waking up with zero prior context. The onboard output is the sole source of truth for the learning agent — if it's ambiguous, the agent will make bad decisions.

## What Was Accomplished

### Reviewed onboard output from an agent's perspective
Ran `nexus learn onboard` and identified 7 gaps in the output and agent instructions: no system intro, no message format guidance, ambiguous exercise creation workflow, no daily session example, no short/long day mechanism, missing task file paths, and no "last session" highlight.

### Added system intro to onboard header
The output now opens with a 5-line explanation of what nexus is, the agent's role, and that this output is the full context. Also added today's date to the header.

### Task file paths in onboard output
Task listings under "CURRENT GOAL" now show `file:` lines for each `relevant_files` entry, resolved to absolute paths. Previously the agent had no way to see which files were attached to tasks.

### Weekly session summary section
New "THIS WEEK'S SESSIONS" section in `onboard.py` that parses record frontmatter (date, duration, type) and computes:
- Session count and active days
- Total time in minutes
- Long sessions (1h+) vs 2/week target
- Type breakdown (practical/theoretical/quiz)

Helper functions added: `_parse_duration_minutes()`, `_parse_record_frontmatter()`, `_weekly_session_summary()`.

### Last session highlight
New "LAST SESSION" section placed before the full records dump, showing the most recent record's frontmatter (date, duration, type, status) and body text. This gives the agent immediate continuity without scanning 8 records.

### Rewrote agent instructions with "Composing a daily session" workflow
The decision tree was missing the most common case — what to do when a topic exists and the agent needs to compose exercises. Added a full 7-step workflow:
1. Determine session size (using weekly summary to suggest short vs long)
2. Choose exercise type (checking balance, ensuring weekly quiz)
3. Read reference material
4. Check recent records for calibration
5. Create exercise files
6. Register tasks via CLI with `--file` flag
7. Send message to user (with format guidance: greeting, progress note, exercise, instructions)

Also split the decision tree's "incomplete tasks" step into dangling (previous day) vs today's tasks.

## Key Files Affected

- `src/commands/learn/onboard.py` — intro block, date header, task file paths, weekly session summary, last session highlight, helper functions
- `src/commands/learn/agent_instructions.md` — complete rewrite of decision tree and new "Composing a daily session" section

## What Comes Next

- **Test with actual records** — the weekly summary and last session sections are empty right now. Create some test records and verify the parsing and display work correctly.
- **OpenClaw integration** — wire up the onboard command as a skill so the Telegram agent can call it via cron.
- **Similar treatment for other onboard commands** — `nexus self onboard` and `nexus manage onboard` will need the same cold-start agent patterns (intro, session summary, last session highlight, step-by-step workflow).
