"""Record subcommand — log a learning session."""

from datetime import date

import typer

from src.utils.learn import get_active_context, get_current_goal, get_records_dir


def record(
    description: str = typer.Argument(help="Description of what was done"),
    duration: str = typer.Option(
        "", help="How long the session took (e.g. '20min', '1h')"
    ),
    status: str = typer.Option("completed", help="Status: completed, partial, stuck"),
    type: str = typer.Option("practical", help="Type: practical, theoretical, quiz"),
):
    """Log a learning session record for the active subtopic."""
    if type not in ("practical", "theoretical", "quiz"):
        typer.echo(f"Invalid type: {type}. Must be: practical, theoretical, quiz")
        raise typer.Exit(1)

    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    goal_name = goal.name if goal else "none"

    records_dir = get_records_dir(topic_name, subtopic_name)
    records_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()
    existing = list(records_dir.glob(f"{today.isoformat()}*.md"))
    suffix = f"_{len(existing) + 1}" if existing else ""
    filename = f"{today.isoformat()}{suffix}.md"
    record_path = records_dir / filename

    lines = [
        "---",
        f"date: {today.isoformat()}",
        f"phase: {phase_name}",
        f"goal: {goal_name}",
        f"type: {type}",
        f"duration: {duration or 'not recorded'}",
        f"status: {status}",
        "---",
        "",
        description,
        "",
    ]

    record_path.write_text("\n".join(lines))
    typer.echo(f"Record saved: {record_path}")
