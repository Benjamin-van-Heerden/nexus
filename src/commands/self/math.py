from datetime import date, timedelta
from typing import Annotated

import typer
from src.utils.self import (
    format_duration,
    get_current_week_start,
    load_math_config,
    load_math_log,
    parse_duration,
    save_math_log,
)

from src.commands.self.math_generator import generate_problems
from src.models.self.math import MathSession

app = typer.Typer(help="Mental math practice")


@app.command()
def generate() -> None:
    problems, _ = generate_problems()
    typer.echo(problems)


@app.command()
def log(
    time: Annotated[str, typer.Option("--time")],
    correct: Annotated[int, typer.Option("--correct")],
    type: Annotated[list[str] | None, typer.Option("--type")] = None,
) -> None:
    time_seconds = parse_duration(time)
    config = load_math_config()
    math_log = load_math_log()

    session = MathSession(
        date=date.today(),
        time_seconds=time_seconds,
        correct=correct,
        total=config.general.problems_per_day,
        problem_types=type or [],
    )
    math_log.sessions.append(session)
    save_math_log(math_log)

    recent = [s for s in math_log.sessions if s != session][-5:]
    avg_time = ""
    if recent:
        avg = sum(s.time_seconds for s in recent) // len(recent)
        avg_time = f" (recent avg: {format_duration(avg)})"

    typer.echo(
        f"Logged: {format_duration(time_seconds)}, {correct}/{session.total} correct{avg_time}"
    )


@app.command()
def status() -> None:
    math_log = load_math_log()
    config = load_math_config()

    if not math_log.sessions:
        typer.echo("No math sessions logged yet.")
        return

    today = date.today()
    this_week_start = get_current_week_start(today)
    last_week_start = this_week_start - timedelta(days=7)

    this_week = [s for s in math_log.sessions if s.date >= this_week_start]
    last_week = [
        s for s in math_log.sessions if last_week_start <= s.date < this_week_start
    ]

    typer.echo("Recent sessions (last 2 weeks):")
    recent = [s for s in math_log.sessions if s.date >= last_week_start]
    for s in sorted(recent, key=lambda x: x.date):
        typer.echo(
            f"  [{s.date}] {format_duration(s.time_seconds)}, {s.correct}/{s.total} correct"
        )

    if this_week:
        avg_this = sum(s.time_seconds for s in this_week) // len(this_week)
        typer.echo(f"\nThis week avg: {format_duration(avg_this)}")
    else:
        typer.echo("\nNo sessions this week.")

    if last_week:
        avg_last = sum(s.time_seconds for s in last_week) // len(last_week)
        typer.echo(f"Last week avg: {format_duration(avg_last)}")
        if this_week:
            avg_this = sum(s.time_seconds for s in this_week) // len(this_week)
            if avg_this < avg_last:
                typer.echo("Trend: improving")
            elif avg_this > avg_last:
                typer.echo("Trend: declining")
            else:
                typer.echo("Trend: stable")

    typer.echo(f"\nConfig: {config.general.problems_per_day} problems/day")
    for name in ["addition", "subtraction", "multiplication", "division"]:
        tc = getattr(config, name)
        if tc.enabled:
            typer.echo(
                f"  {name}: weight={tc.weight}, digits={tc.min_digits}-{tc.max_digits}"
            )


@app.command("config")
def show_config() -> None:
    config = load_math_config()
    typer.echo(f"Problems per day: {config.general.problems_per_day}\n")
    for name in ["addition", "subtraction", "multiplication", "division"]:
        tc = getattr(config, name)
        status = "enabled" if tc.enabled else "disabled"
        typer.echo(f"{name} ({status}):")
        typer.echo(f"  weight: {tc.weight}")
        typer.echo(f"  digits: {tc.min_digits}-{tc.max_digits}")
        typer.echo(f"  trailing zeros chance: {tc.trailing_zeros_chance}")
        if hasattr(tc, "whole_numbers_only"):
            typer.echo(f"  whole numbers only: {tc.whole_numbers_only}")
