---
created_at: '2026-04-10T16:49:29.903293'
username: benjamin_van_heerden
---
# Work Log - Fix nexus learn agent instructions and data cleanup

## Overarching Goals

The OpenClaw learn agent (running Kimi K2.5) was not following the nexus learn system correctly. It failed to complete goals/phases, filed tasks under wrong goals, created files in its own workspace instead of the nexus repo, and didn't always respond to the user after running onboard/refresh. This session focused on making the instructions bulletproof for a less capable agent.

## What Was Accomplished

### Rewrote agent_instructions.md
- Added "System hierarchy" section at the top: topic → subtopic → phase → goal → task, with clear explanation of what the agent manages vs what the user creates
- Added "State management rules" section with NON-NEGOTIABLE rules about running completion commands immediately
- Replaced the vague decision tree with a strict "Wake-up checklist" — numbered steps the agent follows in order, stopping at the first match
- Step 5 (no incomplete tasks) now explicitly requires asking the user two questions: (a) more exercises or move on? (b) how much time today? — before doing anything else
- Rewrote file creation instructions to reference absolute paths from the PATHS section, with explicit warnings against creating files in the agent's own workspace
- Clarified that `./` prefix is ONLY for CLI `--file` flags, never for file creation or user communication

### Updated onboard.py (learn)
- Moved PATHS section before exercise type instructions so the agent sees absolute paths first
- Added "ALL file creation MUST happen inside these directories" warning
- Each exercise type instruction now prefixed with `→ create files in: <absolute path>`
- Added ACTION REQUIRED footer to both onboard() and refresh()
- Added absolute PATHS section to refresh output

### Updated refresh instructions (learn)
- Replaced vague 5-line checklist with explicit wake-up checklist matching the full instructions
- Added STATE MANAGEMENT block with non-negotiable rules

### Added ACTION REQUIRED footers to all systems
- learn onboard + refresh
- self onboard + refresh
- manage onboard + refresh
- Each ends with "send a message to the user NOW — do not silently process this output"

### Cleaned up phase.toml data
- `otp-foundations/phase.toml`: Moved Hangman tasks from "OTP Basics" goal to "Functional Cores and the CRC Pattern" goal where they belong. Fixed broken `./Documents/nexus/...` paths to correct `./learn/...` paths. Removed supervisor tasks that belonged in the next phase.
- `abstractions-and-supervision/phase.toml`: Added the two supervisor tasks (KVStore practical + theoretical) under "Supervisors, Child Specs, and Restart Strategies" goal. Set current goal to `in_progress`.

### Updated mem memory
- Updated `relative-paths-and-resolve` memory to emphasize that agent-facing output MUST use absolute paths

## Key Files Affected

- `src/commands/learn/agent_instructions.md` — major rewrite (hierarchy, state management, wake-up checklist, absolute path instructions)
- `src/commands/learn/onboard.py` — PATHS before instructions, absolute paths on exercise types, ACTION REQUIRED footers
- `src/commands/manage/onboard.py` — ACTION REQUIRED footers on onboard and refresh
- `src/commands/self/onboard.py` — ACTION REQUIRED footers on onboard and refresh
- `learn/elixir/otp/otp-foundations/phase.toml` — task redistribution across goals, path fixes
- `learn/elixir/otp/abstractions-and-supervision/phase.toml` — added supervisor tasks, set goal status

## What Comes Next

- Test the updated instructions with a real agent session to see if behavior improves
- The `nexus_news_command` spec is available to work on (0/6 tasks completed, worktree exists)
- Consider whether subtopic.toml exercise type descriptions need updating to use absolute path placeholders instead of relative references like "practical/lib/"
