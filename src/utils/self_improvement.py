import re
import tomllib
from datetime import date, timedelta
from pathlib import Path

import tomli_w

from src.models.self_improvement.exercise import ExerciseLog
from src.models.self_improvement.habits import HabitsConfig
from src.models.self_improvement.learning import LearningLog
from src.models.self_improvement.math import MathConfig, MathLog
from src.models.self_improvement.reading import BookConfig
from src.utils.paths import get_self_dir


# -- Path helpers --


def get_habits_config_path() -> Path:
    return get_self_dir() / "habits.toml"


def get_reading_active_dir() -> Path:
    return get_self_dir() / "reading" / "active"


def get_reading_completed_dir() -> Path:
    return get_self_dir() / "reading" / "completed"


def get_exercise_log_path() -> Path:
    return get_self_dir() / "exercise" / "log.toml"


def get_math_config_path() -> Path:
    return get_self_dir() / "math" / "config.toml"


def get_math_log_path() -> Path:
    return get_self_dir() / "math" / "log.toml"


def get_learning_log_path() -> Path:
    return get_self_dir() / "learning" / "log.toml"


# -- TOML I/O helpers --


def _load_toml(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _save_toml(path: Path, data: dict) -> None:
    with open(path, "wb") as f:
        tomli_w.dump(data, f, multiline_strings=True)


# -- Habits --


def load_habits_config() -> HabitsConfig:
    raw = _load_toml(get_habits_config_path())
    return HabitsConfig(**raw)


# -- Reading --


def load_book(slug: str) -> BookConfig:
    active_path = get_reading_active_dir() / f"{slug}.toml"
    if active_path.exists():
        return BookConfig(**_load_toml(active_path))
    completed_path = get_reading_completed_dir() / f"{slug}.toml"
    if completed_path.exists():
        return BookConfig(**_load_toml(completed_path))
    raise FileNotFoundError(f"Book '{slug}' not found in active or completed")


def save_book(book: BookConfig) -> None:
    if book.status == "active":
        path = get_reading_active_dir() / f"{book.slug}.toml"
    else:
        path = get_reading_completed_dir() / f"{book.slug}.toml"
    _save_toml(path, book.model_dump(mode="json", exclude_none=True))


def list_active_books() -> list[BookConfig]:
    books = []
    for p in sorted(get_reading_active_dir().glob("*.toml")):
        books.append(BookConfig(**_load_toml(p)))
    return books


def list_completed_books() -> list[BookConfig]:
    books = []
    for p in sorted(get_reading_completed_dir().glob("*.toml")):
        books.append(BookConfig(**_load_toml(p)))
    return books


# -- Exercise --


def load_exercise_log() -> ExerciseLog:
    raw = _load_toml(get_exercise_log_path())
    return ExerciseLog(**raw)


def save_exercise_log(log: ExerciseLog) -> None:
    _save_toml(get_exercise_log_path(), log.model_dump(mode="json", exclude_none=True))


# -- Math --


def load_math_config() -> MathConfig:
    raw = _load_toml(get_math_config_path())
    return MathConfig(**raw)


def save_math_config(config: MathConfig) -> None:
    _save_toml(get_math_config_path(), config.model_dump(mode="json", exclude_none=True))


def load_math_log() -> MathLog:
    raw = _load_toml(get_math_log_path())
    return MathLog(**raw)


def save_math_log(log: MathLog) -> None:
    _save_toml(get_math_log_path(), log.model_dump(mode="json", exclude_none=True))


# -- Learning --


def load_learning_log() -> LearningLog:
    raw = _load_toml(get_learning_log_path())
    return LearningLog(**raw)


def save_learning_log(log: LearningLog) -> None:
    _save_toml(get_learning_log_path(), log.model_dump(mode="json", exclude_none=True))


# -- Week calculation helpers (ISO weeks, Monday-Sunday) --


def get_current_week_start(reference: date | None = None) -> date:
    today = reference or date.today()
    return today - timedelta(days=today.weekday())


def get_sessions_this_week(sessions: list, reference: date | None = None) -> list:
    week_start = get_current_week_start(reference)
    return [s for s in sessions if s.date >= week_start]


def get_days_with_activity(sessions: list, reference: date | None = None) -> set[date]:
    week_sessions = get_sessions_this_week(sessions, reference)
    return {s.date for s in week_sessions}


def get_missing_days_this_week(sessions: list, reference: date | None = None) -> list[str]:
    today = reference or date.today()
    week_start = get_current_week_start(today)
    active_dates = get_days_with_activity(sessions, today)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    missing = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        if day > today:
            break
        if day not in active_dates:
            missing.append(day_names[i])
    return missing


def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def parse_duration(time_str: str) -> int:
    parts = time_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid duration format '{time_str}', expected M:SS")
    minutes = int(parts[0])
    seconds = int(parts[1])
    return minutes * 60 + seconds


# -- Slug helper --


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug
