---
title: nexus self-improvement command
status: todo
assigned_to: null
issue_id: null
issue_url: null
branch: null
pr_url: null
created_at: '2026-03-31T10:04:55.701451'
updated_at: '2026-03-31T10:04:55.701451'
completed_at: null
last_synced_at: null
local_content_hash: null
remote_content_hash: null
---
## Overview

Build the `nexus self` command — a personal habit tracking and self-improvement system. An OpenClaw agent wakes up once daily via cron, runs `nexus self onboard`, and sends a Telegram message with progress, motivation, accountability, and the day's mental math problems. The user responds throughout the day with updates (reading sessions, exercise logs, math completion times, learning check-ins). The agent asks follow-up questions (especially for reading comprehension) and logs structured data.

The system is designed around four habits, each tracked differently but unified under a single `habits.toml` config with textual goals the agent interprets naturally. The onboard output is the entire interface — it must give the agent enough context to assess the full weekly picture, notice missing days, and hold the user accountable.

The existing `self-improvement/` directory and `config.toml` `[self-improvement.goals]` section are stale and will be replaced by a new `self/` directory.

## Goals

- Daily agent wake-up with full context: current date/day, weekly progress, gaps, trends
- Reading tracking with agent-driven comprehension discussion and takeaways
- Exercise tracking with motivation and accountability
- Mental math with configurable problem generation and performance tracking
- Learning check-in (standalone, not derived from `nexus learn`)
- Agent provides motivation when on track, accountability when falling behind
- Agent notices missing days ("You didn't check in yesterday — what happened?")

## Technical Approach

### Directory Structure

```
self/
├── habits.toml                         # Top-level config: habit definitions with textual goals
├── reading/
│   ├── active/
│   │   ├── the_iliad.toml              # Active book with session history
│   │   └── rust_in_action.toml
│   └── completed/
│       └── the_cat_in_the_hat.toml     # Completed books (moved here on finish)
├── exercise/
│   └── log.toml                        # Exercise session log (append-only [[sessions]])
├── math/
│   ├── config.toml                     # Problem generation config (types, weights, difficulty knobs)
│   └── log.toml                        # Math session log (time, accuracy, problem types)
├── learning/
│   └── log.toml                        # Daily learning check-in log
└── weekly/                             # Optional: weekly summary snapshots (agent can write these)
```

### habits.toml

Top-level config. Each habit has a textual goal the agent interprets, plus an `active` flag.

```toml
[reading]
goal = "Read 5 days per week, at least 20 pages or 1 section per session"
active = true

[exercise]
goal = "Exercise 4 times per week, mix of running and gym"
active = true

[mental_math]
goal = "Complete 5 problems daily, aim for under 3 minutes total"
active = true

[learning]
goal = "Complete at least one learning session per day"
active = true
```

The agent reads these goals as natural language and reasons about them. No numeric parsing needed in the CLI — the CLI just prints the goal text alongside the tracking data.

### Reading System

**Book TOML** (`self/reading/active/<slug>.toml`):

```toml
name = "The Iliad"
author = "Homer"
slug = "the_iliad"
started = 2026-03-15
status = "active"                       # active | completed
current_section = "Book 9"             # Freeform: chapter, section, page range, whatever fits the book
total_sections = "24 Books"             # Optional: gives agent a sense of progress

[[sessions]]
date = 2026-03-28
section = "Book 7-8"
summary = "Hector and Ajax duel, Greeks build a wall around their ships"
takeaway = "The wall becomes a symbol of Greek desperation — they're protecting ships they might need to flee on"
agent_questions = ["Why did the gods intervene in the duel?", "What does the wall symbolize for the Greek morale?"]

[[sessions]]
date = 2026-03-30
section = "Book 9"
summary = "Embassy to Achilles — Odysseus, Ajax, and Phoenix try to persuade him to return"
takeaway = "Achilles' refusal reveals his internal conflict between glory and survival — he's not just angry, he's questioning the entire value system"
agent_questions = ["How does Phoenix's story relate to Achilles' situation?", "Is Achilles being rational or emotional in his refusal?"]
```

**Session flow:**
1. Agent (via onboard) sees active books, last session dates, current position
2. User says "I read some more of the Iliad today, got through Books 9 and 10"
3. Agent asks comprehension questions based on what those sections cover (agent uses its own knowledge of the text + the context of prior sessions)
4. User discusses, agent formulates a takeaway
5. Agent logs the session via `nexus self read log <book_slug> --section "Book 9-10" --summary "..." --takeaway "..." --questions "q1" --questions "q2"`
6. Agent updates `current_section` on the book

**Commands:**
```
nexus self read new "The Iliad" --author "Homer"
  --section "Book 1"                    # Starting section
  --total "24 Books"                    # Optional total
nexus self read list                    # List active books
nexus self read show <slug>             # Show book details + recent sessions
nexus self read log <slug>              # Log a reading session
  --section "Book 9-10"
  --summary "Embassy to Achilles..."
  --takeaway "Achilles questions the value system..."
  --question "Why did Phoenix..."       # Repeatable
nexus self read complete <slug>         # Move to completed/
nexus self read history                 # List completed books
```

### Exercise System

Simple append-only log. The agent's job is motivation and accountability, not workout programming.

**Log TOML** (`self/exercise/log.toml`):

```toml
[[sessions]]
date = 2026-03-28
type = "gym"
description = "Upper body — bench press 4x8, overhead press 3x10, rows 4x8, curls 3x12"
intensity = "hard"                      # easy | moderate | hard
duration_minutes = 60

[[sessions]]
date = 2026-03-30
type = "run"
description = "5km easy pace, 28 minutes"
intensity = "moderate"
duration_minutes = 28
```

**Commands:**
```
nexus self exercise log                 # Log exercise session
  --type "gym"
  --description "Upper body..."
  --intensity "hard"
  --duration 60
nexus self exercise status              # This week's sessions vs goal
nexus self exercise history             # Recent sessions
  --weeks 4                             # Optional: how far back (default 4)
```

### Mental Math System

**Config TOML** (`self/math/config.toml`):

```toml
[general]
problems_per_day = 5

[addition]
enabled = true
weight = 1
min_digits = 2
max_digits = 3
trailing_zeros_chance = 0.3             # 30% chance to add up to 2 trailing zeros

[subtraction]
enabled = true
weight = 1
min_digits = 2
max_digits = 3
trailing_zeros_chance = 0.3

[multiplication]
enabled = true
weight = 3                              # Multiplication preferred
min_digits = 2
max_digits = 2                          # Up to 99x99
trailing_zeros_chance = 0.3             # Randomly adds up to 2 zeros (e.g. 47x300)

[division]
enabled = true
weight = 1
min_digits = 2
max_digits = 2
whole_numbers_only = true               # Results are always whole numbers
```

**Generator** (`src/commands/self_improvement/math_generator.py`):
- Reads `self/math/config.toml`
- Selects problem types based on weights
- Generates numbers within digit ranges
- Randomly appends 1-2 trailing zeros (based on `trailing_zeros_chance`)
- For division: generates a * b first, then presents (a*b) / b to ensure whole number result
- Prints problems in a clean numbered format:
  ```
  1. 47 × 300 =
  2. 856 + 234 =
  3. 72 × 58 =
  4. 945 - 367 =
  5. 1260 ÷ 42 =
  ```

**Log TOML** (`self/math/log.toml`):

```toml
[[sessions]]
date = 2026-03-30
time_seconds = 200                      # 3 min 20 sec
correct = 5
total = 5
problem_types = ["multiplication", "addition", "multiplication", "subtraction", "division"]
```

**Commands:**
```
nexus self math generate                # Generate and print today's problems
nexus self math log                     # Log completion
  --time "3:20"                         # Minutes:seconds format
  --correct 5                           # How many correct
nexus self math status                  # Recent performance, trend, config summary
nexus self math config                  # Show current config
```

The agent adjusts `config.toml` knobs over time based on performance trends. The user does not interact with the config directly.

### Learning System

Simple daily check-in. Standalone — does NOT derive from `nexus learn` records.

**Log TOML** (`self/learning/log.toml`):

```toml
[[sessions]]
date = 2026-03-28
did_learn = true
notes = "Worked through Rust ownership exercises"

[[sessions]]
date = 2026-03-30
did_learn = true
notes = "JAX foundations — array operations"
```

**Commands:**
```
nexus self learn log                    # Log today's learning
  --notes "Worked through..."           # Optional notes
  --skip                                # Explicitly log a skip day (did_learn = false)
nexus self learn status                 # This week's check-ins vs goal
```

### Onboard Command

`nexus self onboard` is the core interface. The agent runs this once daily. Output sections:

**1. Date and Context**
- Current date, day of week, week number
- "It's Wednesday — 3 days left in the week"

**2. Per-Habit Status (for each active habit):**

For each habit, print:
- The goal text from `habits.toml`
- This week's data (sessions logged, days with activity)
- Days without activity this week (explicit: "No reading logged on Monday or Tuesday")
- Last session details
- Whether today's goal is met yet

**3. Reading Detail**
- Active books with current section and last session date
- If a book hasn't been touched in >3 days, flag it

**4. Mental Math Problems**
- Run the generator and print today's 5 problems directly in the onboard output
- Show yesterday's performance if logged (time, accuracy)
- Show trend: "Your average time this week is 3:45, down from 4:10 last week"

**5. Learning Check**
- Did the user log learning yesterday? If not, call it out
- Streak information

**6. Motivation / Accountability**
- If on track: encouragement
- If behind: direct but supportive accountability
- The agent instructions should guide tone: "Be a coach, not a nag. Be direct. If they're slipping, say so. If they're crushing it, celebrate."

**7. Agent Instructions**
- Read and print `src/commands/self_improvement/agent_instructions.md`
- Instructions tell the agent: how to interpret the data, how to interact with the user for each habit (especially the reading comprehension flow), how to log sessions via CLI commands, how to adjust math config

### Agent Instructions

`src/commands/self_improvement/agent_instructions.md` must cover:

- **Daily workflow**: run onboard, assess, compose message with progress + math problems + reading prompts
- **Reading interaction**: present math problems and ask about reading in the same message. When user responds about reading, ask 2-3 comprehension questions. Formulate takeaway from discussion. Log via `nexus self read log`
- **Exercise interaction**: user reports what they did, agent logs it and provides motivation. Log via `nexus self exercise log`
- **Math interaction**: problems are in the onboard output. User reports time and correctness. Agent logs via `nexus self math log`. If performance is consistently good (>90% correct, time trending down over 2+ weeks), agent can adjust config.toml knobs (increase digits, change weights)
- **Learning interaction**: user confirms they learned or didn't. Agent logs via `nexus self learn log`
- **Accountability tone**: be a coach. Notice patterns. "You've missed reading 3 days this week and it's already Thursday. What's going on?" Not: "It appears you may have fallen slightly behind schedule."
- **Date awareness**: always reason about day-of-week and days remaining. Monday with 0 sessions is fine. Friday with 0 sessions is a problem.

### File Structure (src/)

```
src/
├── commands/
│   └── self_improvement/
│       ├── main.py                     # Typer app wiring (read, exercise, math, learn subcommands + onboard)
│       ├── read.py                     # Reading CRUD + session logging
│       ├── exercise.py                 # Exercise logging + status
│       ├── math.py                     # Math generate, log, status, config
│       ├── math_generator.py           # Problem generation logic
│       ├── learn.py                    # Learning check-in
│       ├── onboard.py                  # Daily context dump
│       └── agent_instructions.md       # Agent-facing instructions
├── models/
│   └── self_improvement/
│       ├── habits.py                   # HabitsConfig model
│       ├── reading.py                  # BookConfig, ReadingSession models
│       ├── exercise.py                 # ExerciseLog, ExerciseSession models
│       ├── math.py                     # MathConfig, MathLog, MathSession models
│       └── learning.py                 # LearningLog, LearningSession models
└── utils/
    └── self_improvement.py             # TOML I/O helpers, path helpers, week calculation utils
```

### Wiring in main.py

Add to the root `main.py`:
```python
from src.commands.self_improvement.main import app as self_app
app.add_typer(self_app, name="self", help="Self-improvement and habit tracking")
```

### Stale File Cleanup

- Remove `self-improvement/` directory (empty subdirs, no files)
- Remove `[self-improvement.goals]` section from `config.toml`
- Create `self/` directory with the new structure

## Success Criteria

- `habits.toml` with textual goals drives all habit tracking
- `nexus self onboard` produces a complete daily context dump with: date awareness, per-habit weekly status, missing day detection, reading book state, mental math problems, trends
- Reading flow works: new book → log sessions with summary/takeaway/questions → complete book → history
- Exercise flow works: log sessions with type/description/intensity/duration → status shows weekly progress
- Mental math generator produces correct problems respecting config (weights, digit ranges, trailing zeros, whole-number division)
- Math logging tracks time and accuracy, status shows trends
- Learning check-in is standalone (not derived from `nexus learn`)
- Agent instructions are comprehensive enough for OpenClaw to run the full daily workflow autonomously
- Onboard output enables the agent to notice missing days and provide accountability
- All TOML files follow project conventions (no __init__.py, Pydantic models, tomli_w with multiline_strings, ./ path convention where applicable)

## Critical Context: Daily Flow and Agent Architecture

The `nexus self` system is consumed by an AI agent (OpenClaw) that runs once per day via cron on a remote machine. **The agent wakes up with zero context** — no memory of yesterday, no knowledge of the user, no understanding of what nexus is. The onboard output is the agent's ENTIRE brain. If something isn't in the onboard output, the agent doesn't know it.

### The Daily Flow

**Step 1 — Agent wakes up, runs `nexus self onboard`.**

The onboard output must be completely self-contained. It prints:
1. What this system is and who the user is ("You are Benjamin's self-improvement coach...")
2. Today's date, day of week, week number, days remaining in the week
3. Each habit's full weekly picture: goal text, sessions logged this week, which days are missing, last session details
4. Active reading books with current position and last session date
5. Today's mental math problems (generated inline)
6. Math performance trends
7. The full agent instructions playbook (from agent_instructions.md)

**Step 2 — Agent composes a Telegram message.**

Based on the onboard data, the agent sends something like:
> Morning! It's Wednesday — here's where you stand this week:
> **Reading** (2/5): Read the Iliad on Monday (Books 7-8). Nothing since Tuesday. 3 sessions needed, 4 days left.
> **Exercise** (1/4): Gym on Monday. Need 3 more this week.
> **Learning**: Logged Monday and Tuesday. On track.
> **Math:**
> 1. 47 × 300 =
> 2. 856 + 234 =
> ...
> Let me know how the math goes and what you're reading today.

**Step 3 — User responds throughout the day.**

The user reports everything in natural language, potentially all at once:
> "Did a hard gym session. Read more of the Iliad, got through Book 9. Math took 3:20, got them all."

**Step 4 — Agent processes and interacts.**

- Logs exercise immediately via CLI
- Logs math immediately via CLI
- For reading: does NOT log yet. First asks 2-3 comprehension questions about what the user read. User discusses. Agent formulates a takeaway from the discussion, THEN logs the full reading session (summary + takeaway + questions) via CLI.

**Step 5 — Next morning.** Fresh agent, runs onboard, sees yesterday's sessions, full picture.

### Design Principle

The onboard output must contain:
- **What** — what the system is, what each habit tracks
- **State** — full weekly data for every habit, every session, every gap
- **Action** — what to do right now (compose message, present math, ask about reading)
- **How** — exact CLI commands to log each type of session
- **Tone** — coaching voice, accountability, motivation guidance

If the implementation is correct, a cold-start agent reading only the onboard output can run the entire daily workflow without any external context.

## Notes

- The `self/` system and `nexus learn` system are completely independent — do not cross-reference or derive data between them
- The agent adjusts `self/math/config.toml` over time — the user never touches it directly
- Reading session records are written by the agent after a comprehension discussion, not by the user directly
- Exercise tracking is intentionally simple — the agent provides motivation, not workout plans
- The `habits/` directory at project root appears unused and can be removed during cleanup
- Week boundaries: use ISO weeks (Monday-Sunday) for all weekly goal tracking
- The onboard command should be fast — no external API calls, just TOML reads and math generation
- Git sync (pre/post in main.py) handles all state persistence automatically
