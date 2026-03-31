from datetime import date, timedelta
from typing import Annotated

import typer
from src.utils.self import (
    get_missing_days_this_week,
    get_sessions_this_week,
    load_habits_config,
    load_learning_log,
    save_learning_log,
)

from src.models.self.learning import LearningSession

app = typer.Typer(help="Daily learning check-in")


def _calculate_streak(sessions: list[LearningSession]) -> int:
    if not sessions:
        return 0
    today = date.today()
    learned_dates = sorted({s.date for s in sessions if s.did_learn}, reverse=True)
    if not learned_dates:
        return 0

    check_date = today if today in learned_dates else today - timedelta(days=1)
    if check_date not in learned_dates:
        return 0

    streak = 0
    for d in learned_dates:
        if d == check_date - timedelta(days=streak):
            streak += 1
        else:
            break
    return streak


@app.command()
def log(
    notes: Annotated[str, typer.Option("--notes")] = "",
    skip: Annotated[bool, typer.Option("--skip")] = False,
) -> None:
    learning_log = load_learning_log()
    today = date.today()

    existing = [s for s in learning_log.sessions if s.date == today]
    if existing:
        if not typer.confirm("A session for today already exists. Overwrite?"):
            raise typer.Exit(0)
        learning_log.sessions = [s for s in learning_log.sessions if s.date != today]

    session = LearningSession(
        date=today,
        did_learn=not skip,
        notes=notes,
    )
    learning_log.sessions.append(session)
    save_learning_log(learning_log)

    streak = _calculate_streak(learning_log.sessions)
    if skip:
        typer.echo("Logged: skip day")
    else:
        typer.echo(f"Logged: learned today{f' — {notes}' if notes else ''}")
    typer.echo(f"Current streak: {streak} day(s)")


@app.command()
def status() -> None:
    learning_log = load_learning_log()
    habits = load_habits_config()

    typer.echo(f"Goal: {habits.learning.goal}")

    week_sessions = get_sessions_this_week(learning_log.sessions)
    if week_sessions:
        typer.echo(f"\nThis week ({len(week_sessions)} check-ins):")
        for s in sorted(week_sessions, key=lambda x: x.date):
            status_str = "learned" if s.did_learn else "skipped"
            notes_str = f" — {s.notes[:60]}" if s.notes else ""
            typer.echo(f"  [{s.date}] {status_str}{notes_str}")
    else:
        typer.echo("\nNo check-ins this week.")

    streak = _calculate_streak(learning_log.sessions)
    typer.echo(f"\nStreak: {streak} day(s)")

    missing = get_missing_days_this_week(learning_log.sessions)
    if missing:
        typer.echo(f"Missing days: {', '.join(missing)}")
