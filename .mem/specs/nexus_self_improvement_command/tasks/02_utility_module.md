---
title: Utility module
status: todo
created_at: '2026-03-31T11:20:44.308686'
updated_at: '2026-03-31T11:20:44.308686'
completed_at: null
---
Create src/utils/self_improvement.py with TOML I/O helpers, path helpers, and week calculation utilities.

IMPORTANT CONTEXT: Follow the patterns in src/utils/learn.py. Use tomllib (stdlib) for reading, tomli_w for writing (multiline_strings=True). All model_dump() calls use mode='json' and exclude_none=True. Path helpers follow the pattern in src/utils/paths.py which provides get_project_root().

**Path helpers:**
- get_self_dir() -> Path  (project_root / 'self')
- get_habits_config_path() -> Path  (self / 'habits.toml')
- get_reading_active_dir() -> Path  (self / 'reading' / 'active')
- get_reading_completed_dir() -> Path  (self / 'reading' / 'completed')
- get_exercise_log_path() -> Path  (self / 'exercise' / 'log.toml')
- get_math_config_path() -> Path  (self / 'math' / 'config.toml')
- get_math_log_path() -> Path  (self / 'math' / 'log.toml')
- get_learning_log_path() -> Path  (self / 'learning' / 'log.toml')

**TOML I/O:**
- load_habits_config() -> HabitsConfig
- load_book(slug: str) -> BookConfig  (reads from active dir by default, falls back to completed)
- save_book(book: BookConfig) -> None  (saves to active or completed based on status)
- load_exercise_log() -> ExerciseLog
- save_exercise_log(log: ExerciseLog) -> None
- load_math_config() -> MathConfig
- save_math_config(config: MathConfig) -> None
- load_math_log() -> MathLog
- save_math_log(log: MathLog) -> None
- load_learning_log() -> LearningLog
- save_learning_log(log: LearningLog) -> None
- list_active_books() -> list[BookConfig]  (read all .toml files in reading/active/)
- list_completed_books() -> list[BookConfig]  (read all .toml files in reading/completed/)

**Week calculation helpers (use ISO weeks, Monday-Sunday):**
- get_current_week_start() -> date  (Monday of current ISO week)
- get_sessions_this_week(sessions: list, date_field: str = 'date') -> list  (filter sessions where date >= current week start)
- get_days_with_activity(sessions: list, date_field: str = 'date') -> set[date]  (unique dates this week)
- get_missing_days_this_week(sessions: list, date_field: str = 'date') -> list[str]  (day names with no activity, e.g. ['Monday', 'Tuesday'])
- format_duration(seconds: int) -> str  (e.g. 200 -> '3:20')
- parse_duration(time_str: str) -> int  (e.g. '3:20' -> 200, accepts 'M:SS' format)

**Slug helper:**
- slugify(name: str) -> str  (lowercase, spaces and special chars to underscores)