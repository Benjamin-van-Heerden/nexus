---
title: Pydantic models and directory setup
status: todo
created_at: '2026-03-31T11:09:34.425390'
updated_at: '2026-03-31T11:09:34.425390'
completed_at: null
---
Create all Pydantic models and the self/ directory structure. No __init__.py files anywhere.

IMPORTANT CONTEXT: This project uses typer for CLI, Pydantic for models, tomllib (stdlib, Python 3.14+) for TOML reading, tomli_w for TOML writing. All model_dump() calls must use mode='json' and exclude_none=True. All tomli_w.dump() calls must use multiline_strings=True. Look at existing models in src/models/learn/ for patterns.

**1. Create src/models/self_improvement/ with these files:**

habits.py:
- HabitConfig: goal (str), active (bool, default True)
- HabitsConfig: reading (HabitConfig), exercise (HabitConfig), mental_math (HabitConfig), learning (HabitConfig)

reading.py:
- ReadingSession: date (date), section (str), summary (str), takeaway (str), agent_questions (list[str], default [])
- BookConfig: name (str), author (str), slug (str), started (date), status (Literal['active', 'completed']), current_section (str, default ''), total_sections (str, default ''), sessions (list[ReadingSession], default [])

exercise.py:
- ExerciseSession: date (date), type (str), description (str), intensity (Literal['easy', 'moderate', 'hard']), duration_minutes (int)
- ExerciseLog: sessions (list[ExerciseSession], default [])

math.py:
- ProblemTypeConfig: enabled (bool, default True), weight (int, default 1), min_digits (int, default 2), max_digits (int, default 2), trailing_zeros_chance (float, default 0.3)
- DivisionConfig(ProblemTypeConfig): whole_numbers_only (bool, default True)
- MathGeneralConfig: problems_per_day (int, default 5)
- MathConfig: general (MathGeneralConfig), addition (ProblemTypeConfig), subtraction (ProblemTypeConfig), multiplication (ProblemTypeConfig with weight=3), division (DivisionConfig)
- MathSession: date (date), time_seconds (int), correct (int), total (int), problem_types (list[str])
- MathLog: sessions (list[MathSession], default [])

learning.py:
- LearningSession: date (date), did_learn (bool), notes (str, default '')
- LearningLog: sessions (list[LearningSession], default [])

**2. Create self/ directory structure:**
- self/habits.toml — populated with default goals:
  - reading: 'Read 5 days per week, at least 20 pages or 1 section per session'
  - exercise: 'Exercise 4 times per week, mix of running and gym'
  - mental_math: 'Complete 5 problems daily, aim for under 3 minutes total'
  - learning: 'Complete at least one learning session per day'
- self/reading/active/ (empty dir)
- self/reading/completed/ (empty dir)
- self/exercise/log.toml — empty sessions: just the file with no [[sessions]] yet
- self/math/config.toml — populated with default config (addition/subtraction weight 1, multiplication weight 3, division weight 1, all 2-digit, trailing_zeros_chance 0.3, problems_per_day 5)
- self/math/log.toml — empty sessions
- self/learning/log.toml — empty sessions
- self/weekly/ (empty dir)

**3. Stale cleanup:**
- Remove the self-improvement/ directory entirely (it contains only empty subdirs)
- Remove the [self-improvement.goals] section from config.toml (lines with exercise_sessions_per_week and reading_sessions_per_week)
- Remove the habits/ directory if it exists (unused)