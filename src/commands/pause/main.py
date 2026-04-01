"""Nexus pause command — pause and resume subsystems."""

from datetime import date

import typer

from src.models.pause import PauseConfig
from src.utils.pause import (
    get_pause_config_path,
    load_pause_config,
    pause_feature,
    resume_feature,
)


def _print_status() -> None:
    config = load_pause_config()
    path = get_pause_config_path()

    if path.exists() and path.stat().st_size > 0:
        typer.echo(f"Pause config: {path}")
    else:
        typer.echo("No pause config found. All systems active.")
        return

    typer.echo("\nPause status:")
    has_paused = False
    for feature in ["learn", "self", "manage"]:
        entry = getattr(config, feature)
        if entry.active:
            has_paused = True
            reason_str = f" (reason: {entry.reason})" if entry.reason else ""
            typer.echo(f"  {feature}: PAUSED until {entry.resume_date}{reason_str}")
        else:
            typer.echo(f"  {feature}: active")

    if not has_paused:
        typer.echo("  All systems active.")


app = typer.Typer(help="Pause and resume nexus subsystems")


@app.command()
def status():
    """Show current pause status for all subsystems."""
    _print_status()


@app.command()
def learn(
    until: date = typer.Option(
        ..., "--until", "-u", help="Date to resume (YYYY-MM-DD)"
    ),
    reason: str | None = typer.Option(
        None, "--reason", "-r", help="Reason for pausing"
    ),
):
    """Pause the learn subsystem until a date."""
    pause_feature("learn", until, reason)
    typer.echo(f"Learn paused until {until}.")
    if reason:
        typer.echo(f"Reason: {reason}")


@app.command()
def self(
    until: date = typer.Option(
        ..., "--until", "-u", help="Date to resume (YYYY-MM-DD)"
    ),
    reason: str | None = typer.Option(
        None, "--reason", "-r", help="Reason for pausing"
    ),
):
    """Pause the self-improvement subsystem until a date."""
    pause_feature("self", until, reason)
    typer.echo(f"Self-improvement paused until {until}.")
    if reason:
        typer.echo(f"Reason: {reason}")


@app.command()
def resume(
    feature: str = typer.Argument(..., help="Feature to resume (learn, self, manage)"),
):
    """Manually resume a paused subsystem."""
    if feature not in ["learn", "self", "manage"]:
        typer.echo(f"Unknown feature: {feature}. Choose from: learn, self, manage")
        raise typer.Exit(1)

    resume_feature(feature)
    typer.echo(f"{feature} resumed.")
