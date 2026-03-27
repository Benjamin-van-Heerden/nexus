"""Record subcommand — log a learning session."""

from datetime import date

import typer

from src.utils.learn import get_active_context, get_records_dir


def record(
    description: str = typer.Argument(help="Description of what was done"),
    duration: str = typer.Option("", help="How long the session took (e.g. '20min', '1h')"),
    status: str = typer.Option("completed", help="Status: completed, partial, stuck"),
):
    """Log a learning session record for the active phase."""
    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, subtopic_cfg, phase_name, _ = ctx

    records_dir = get_records_dir(topic_name, subtopic_name, phase_name)
    records_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()
    existing = list(records_dir.glob(f"{today.isoformat()}*.md"))
    suffix = f"_{len(existing) + 1}" if existing else ""
    filename = f"{today.isoformat()}{suffix}.md"
    record_path = records_dir / filename

    lines = [
        f"# {today.isoformat()} — {subtopic_cfg.name} / {phase_name}",
        "",
        f"**Duration:** {duration or 'not recorded'}",
        f"**Status:** {status}",
        "",
        description,
        "",
    ]

    record_path.write_text("\n".join(lines))
    typer.echo(f"Record saved: {record_path}")
