---
created_at: '2026-04-07T11:55:31.050161'
username: benjamin_van_heerden
---
# Work Log - Improve agent instructions and reading model across all nexus systems

## Overarching Goals

Improve the agent instructions for all three nexus systems (learn, self, manage) based on real-world usage feedback. The main issues were: agents didn't know what to do after composing tasks/exercises (missing "what to expect next" instructions), the reading flow was too rigid and chapter-centric, and the self system couldn't handle backdated entries.

## What Was Accomplished

### Nexus Learn — Theoretical pairing and feedback loop
- Updated Step 2 (Choose exercise type) in agent instructions to make theoretical+practical pairing the default instead of practical-first
- Changed exercise balance display from `Priority: practical > theoretical > quiz` to `Default: pair practical with theoretical reading`
- Added "Step 9: Stop and wait" after composing exercises
- Added full "When the user reports back" section covering: gathering detail, edge cases (broken exercises, redos, partial completion), updating system state, creating records, and stopping
- Removed old "Tracking progress" and "Records — IMPORTANT" sections (folded into new section)
- Updated refresh instructions to mention theoretical pairing

### Nexus Self — Reading model rework and response flow
- Reworked `ReadingSession` model: renamed `section` → `description` (free-form), removed `agent_questions`
- Reworked `BookConfig` model: removed `current_section` and `total_sections`, added `completion_summary` and `completion_takeaway`
- Simplified `read new` command to just title + author
- Updated `read log` to use `--description` instead of `--section`, dropped `--question`
- Updated `read complete` to require `--summary` and `--takeaway` for a whole-book reflection
- Updated `read list` to show slugs for agent discoverability
- Rewrote reading interaction flow in agent instructions: research the material → provide recap with quotes/context → engage discussion (mainstream vs user interpretation) → only then log
- Added book completion feedback loop instructions
- Added `--date YYYY-MM-DD` backdating flag to all 4 self log commands (exercise, read, math, learn)
- Updated onboard and refresh outputs to remove section/total references
- Migrated Blood Meridian TOML data to new schema

### Nexus Manage — Response flow
- Added "When Benjamin responds" section to agent instructions covering: expected inputs, parse → execute → confirm → stop pattern, edge cases (ambiguity, bulk requests, corrections)
- Updated refresh instructions with condensed response pattern

### Memories
- Created 3 project memories: nexus-manage-interaction-model, nexus-self-interaction-model, nexus-learn-interaction-model

## Key Files Affected

- `src/commands/learn/agent_instructions.md` — theoretical pairing, feedback loop, stop-and-wait
- `src/commands/learn/onboard.py` — exercise balance display, refresh instructions
- `src/commands/self/agent_instructions.md` — reading flow rework, completion flow, backdating, response patterns
- `src/commands/self/onboard.py` — removed section/total references from onboard and refresh
- `src/commands/self/read.py` — description instead of section, simplified new/complete, removed question flag
- `src/commands/self/exercise.py` — added --date flag
- `src/commands/self/math.py` — added --date flag
- `src/commands/self/learn.py` — added --date flag
- `src/models/self/reading.py` — model rework (description, completion fields)
- `src/commands/manage/agent_instructions.md` — response flow section
- `src/commands/manage/onboard.py` — refresh instructions
- `self/reading/active/blood_meridian.toml` — migrated to new schema

## What Comes Next

- Test all three systems end-to-end with real agent sessions to verify the new instruction flows
- OpenClaw skill definitions so the Telegram agent can invoke onboard/refresh via cron
- Consider whether the `nexus pause` GitHub issue is still open and should be claimed
