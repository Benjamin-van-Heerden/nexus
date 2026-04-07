from datetime import date, timedelta
from typing import Annotated

import typer
from src.utils.self import (
    get_current_week_start,
    get_missing_days_this_week,
    get_sessions_this_week,
    load_exercise_log,
    load_habits_config,
    save_exercise_log,
)

from src.models.self.exercise import ExerciseSession

app = typer.Typer(help="Exercise habit tracking")


@app.command()
def log(
    type: Annotated[str, typer.Option("--type")],
    description: Annotated[str, typer.Option("--description")],
    intensity: Annotated[str, typer.Option("--intensity")],
    duration: Annotated[int, typer.Option("--duration")],
    log_date: Annotated[str, typer.Option("--date", help="Backdate entry (YYYY-MM-DD)")] = "",
) -> None:
    if intensity not in ("easy", "moderate", "hard"):
        typer.echo(f"Invalid intensity '{intensity}'. Must be: easy, moderate, hard")
        raise typer.Exit(1)

    session_date = date.fromisoformat(log_date) if log_date else date.today()
    exercise_log = load_exercise_log()
    session = ExerciseSession(
        date=session_date,
        type=type,
        description=description,
        intensity=intensity,
        duration_minutes=duration,
    )
    exercise_log.sessions.append(session)
    save_exercise_log(exercise_log)

    habits = load_habits_config()
    week_sessions = get_sessions_this_week(exercise_log.sessions)
    typer.echo(f"Logged: {type} ({intensity}, {duration} min)")
    typer.echo(
        f"Sessions this week: {len(week_sessions)} — Goal: {habits.exercise.goal}"
    )


@app.command()
def status() -> None:
    exercise_log = load_exercise_log()
    habits = load_habits_config()
    week_sessions = get_sessions_this_week(exercise_log.sessions)

    typer.echo(f"Goal: {habits.exercise.goal}")
    typer.echo(f"Sessions this week: {len(week_sessions)}")

    if week_sessions:
        for s in week_sessions:
            typer.echo(
                f"  [{s.date}] {s.type} — {s.intensity}, {s.duration_minutes} min"
            )
    else:
        typer.echo("  No sessions logged this week.")

    missing = get_missing_days_this_week(exercise_log.sessions)
    if missing:
        typer.echo(f"No activity: {', '.join(missing)}")


@app.command()
def history(
    weeks: Annotated[int, typer.Option("--weeks")] = 4,
) -> None:
    exercise_log = load_exercise_log()
    if not exercise_log.sessions:
        typer.echo("No exercise sessions logged.")
        return

    today = date.today()
    cutoff = get_current_week_start(today) - timedelta(weeks=weeks - 1)
    recent = [s for s in exercise_log.sessions if s.date >= cutoff]

    if not recent:
        typer.echo(f"No sessions in the last {weeks} weeks.")
        return

    current_week_start = None
    for s in sorted(recent, key=lambda x: x.date):
        week_start = get_current_week_start(s.date)
        if week_start != current_week_start:
            current_week_start = week_start
            week_sessions = [
                x for x in recent if get_current_week_start(x.date) == week_start
            ]
            typer.echo(f"\nWeek of {week_start} ({len(week_sessions)} sessions)")
        desc = s.description[:60] + "..." if len(s.description) > 60 else s.description
        typer.echo(
            f"  [{s.date}] {s.type} — {desc} ({s.intensity}, {s.duration_minutes} min)"
        )
