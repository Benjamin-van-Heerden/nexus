---
created_at: '2026-03-31T15:54:54.271499'
username: benjamin_van_heerden
spec_slug: nexus_self_improvement_command
---
# Work Log - Implement nexus self command

## Overarching Goals

Build the complete `nexus self` command — a personal habit tracking and self-improvement system with 4 habits (reading, exercise, mental math, learning). The system is designed to be consumed by an AI agent (OpenClaw) that wakes up daily via cron, runs `nexus self onboard`, and coaches Benjamin via Telegram.

## What Was Accomplished

### Pydantic Models
Created 5 model files in `src/models/self_improvement/`:
- `habits.py` — HabitConfig, HabitsConfig
- `reading.py` — ReadingSession, BookConfig (with session history)
- `exercise.py` — ExerciseSession, ExerciseLog
- `math.py` — ProblemTypeConfig, DivisionConfig, MathConfig, MathSession, MathLog
- `learning.py` — LearningSession, LearningLog

### Directory Structure
Created `self/` directory replacing the stale `self-improvement/` directory:
- `self/habits.toml` with default goals
- `self/reading/active/` and `self/reading/completed/`
- `self/exercise/log.toml`, `self/math/config.toml`, `self/math/log.toml`, `self/learning/log.toml`
- `self/weekly/`

### Utility Module
Created `src/utils/self_improvement.py` with:
- Path helpers for all self/ subdirectories
- TOML I/O for all models (load/save with tomllib/tomli_w)
- ISO week calculations (Monday-Sunday)
- Duration formatting/parsing (M:SS format)
- Slugify helper

### Command Modules
- `read.py` — new, list, show, log (with questions/takeaways), complete, history
- `exercise.py` — log, status (weekly view), history (grouped by week)
- `math.py` — generate, log, status (with trends), config display
- `learn.py` — log (with overwrite protection and skip flag), status (with streak calculation)
- `math_generator.py` — weighted problem selection, trailing zeros, whole-number division, unicode symbols

### App Wiring
- Created `src/commands/self_improvement/main.py` wiring all sub-apps
- Updated root `main.py` to add `self_app`

### Onboard Command
Created `onboard.py` with 8 sections: system intro, date context, reading status (with stale book detection), exercise status, mental math (inline problem generation + trends), learning status (with streak), weekly overview (status emojis), and full agent instructions.

### Agent Instructions
Created `agent_instructions.md` covering identity/role, daily message structure, reading comprehension flow, exercise/math/learning logging commands, accountability patterns by day of week, and full command reference.

### Cleanup
- Removed stale `self-improvement/` directory
- Removed `[self-improvement.goals]` from `config.toml`
- Updated `paths.py` to replace `get_self_improvement_dir` with `get_self_dir`

## Key Files Affected

- `src/models/self_improvement/habits.py` (new)
- `src/models/self_improvement/reading.py` (new)
- `src/models/self_improvement/exercise.py` (new)
- `src/models/self_improvement/math.py` (new)
- `src/models/self_improvement/learning.py` (new)
- `src/utils/self_improvement.py` (new)
- `src/utils/paths.py` (updated get_self_dir)
- `src/commands/self_improvement/main.py` (new)
- `src/commands/self_improvement/read.py` (new)
- `src/commands/self_improvement/exercise.py` (new)
- `src/commands/self_improvement/math.py` (new)
- `src/commands/self_improvement/math_generator.py` (new)
- `src/commands/self_improvement/learn.py` (new)
- `src/commands/self_improvement/onboard.py` (new)
- `src/commands/self_improvement/agent_instructions.md` (new)
- `main.py` (updated — added self_app)
- `config.toml` (removed self-improvement.goals section)
- `self/habits.toml` (new)
- `self/math/config.toml` (new)
- Various empty TOML log files and .gitkeep files

## What Comes Next

All 10 tasks in the spec are complete. The spec is ready to be completed and a PR created.
