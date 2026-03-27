"""Phase subcommand — manage phases in the active subtopic."""

import shutil

import tomli_w
import typer

from src.models.learn.phase import PhaseConfig
from src.models.learn.subtopic import PhaseEntry
from src.utils.learn import (
    get_active_context,
    get_phase_dir,
    get_subtopic_dir,
    load_learn_config,
    load_subtopic_config,
    load_topic_config,
    save_subtopic_config,
)
from src.utils.path_resolution import resolve_str

app = typer.Typer()


@app.command()
def new(
    name: str = typer.Argument(help="Phase name (used as directory name)"),
):
    """Create a new phase in the active subtopic."""
    config = load_learn_config()
    topic_name = config.current_topic
    if not topic_name:
        typer.echo("No current topic set.")
        raise typer.Exit(1)

    topic_cfg = load_topic_config(topic_name)
    subtopic_name = topic_cfg.current_subtopic
    if not subtopic_name:
        typer.echo("No current subtopic set.")
        raise typer.Exit(1)

    phase_dir = get_phase_dir(topic_name, subtopic_name, name)
    if phase_dir.exists():
        typer.echo(f"Phase '{name}' already exists.")
        raise typer.Exit(1)

    # Create directory structure
    phase_dir.mkdir(parents=True)
    (phase_dir / "practical").mkdir()
    (phase_dir / "theoretical").mkdir()
    (phase_dir / "quiz").mkdir()

    # Create phase.toml
    phase_cfg = PhaseConfig(name=name)
    with open(phase_dir / "phase.toml", "wb") as f:
        tomli_w.dump(phase_cfg.model_dump(mode="json"), f)

    # Add to subtopic.toml
    subtopic_cfg = load_subtopic_config(topic_name, subtopic_name)
    subtopic_cfg.phases.append(PhaseEntry(name=name, status="todo"))

    # If this is the first phase, make it current
    if not subtopic_cfg.current_phase:
        subtopic_cfg.current_phase = name
        subtopic_cfg.phases[-1].status = "in_progress"

    save_subtopic_config(topic_name, subtopic_name, subtopic_cfg)

    typer.echo(f"Created phase: {resolve_str(f'learn/{topic_name}/{subtopic_name}/{name}')}/")
    typer.echo(f"Next: add goals with `nexus learn goal new \"goal name\"`")


@app.command()
def complete():
    """Mark the current phase as completed and advance to the next."""
    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, subtopic_cfg, phase_name, phase_cfg = ctx

    # Check for incomplete goals
    incomplete = [g for g in phase_cfg.goals if g.status != "completed"]
    if incomplete:
        typer.echo(f"Cannot complete phase '{phase_name}' — {len(incomplete)} incomplete goal(s):")
        for g in incomplete:
            typer.echo(f"  [{g.status}] {g.name}")
        raise typer.Exit(1)

    # Mark current phase completed
    for p in subtopic_cfg.phases:
        if p.name == phase_name:
            p.status = "completed"
            break

    # Find and activate next phase
    phase_names = [p.name for p in subtopic_cfg.phases]
    current_idx = phase_names.index(phase_name)

    if current_idx + 1 < len(phase_names):
        next_phase = subtopic_cfg.phases[current_idx + 1]
        next_phase.status = "in_progress"
        subtopic_cfg.current_phase = next_phase.name
        save_subtopic_config(topic_name, subtopic_name, subtopic_cfg)
        typer.echo(f"Phase '{phase_name}' completed. Now on: {next_phase.name}")
    else:
        subtopic_cfg.current_phase = ""
        save_subtopic_config(topic_name, subtopic_name, subtopic_cfg)
        typer.echo(f"Phase '{phase_name}' completed. All phases in this subtopic are done!")


@app.command()
def delete(name: str = typer.Argument(help="Phase name to delete")):
    """Delete a phase and all its contents."""
    config = load_learn_config()
    topic_name = config.current_topic
    if not topic_name:
        typer.echo("No current topic set.")
        raise typer.Exit(1)

    topic_cfg = load_topic_config(topic_name)
    subtopic_name = topic_cfg.current_subtopic
    if not subtopic_name:
        typer.echo("No current subtopic set.")
        raise typer.Exit(1)

    phase_dir = get_phase_dir(topic_name, subtopic_name, name)
    if not phase_dir.exists():
        typer.echo(f"Phase '{name}' does not exist.")
        raise typer.Exit(1)

    typer.confirm(f"This will delete phase '{name}' and all its contents. Continue?", abort=True)

    shutil.rmtree(phase_dir)

    # Remove from subtopic.toml
    subtopic_cfg = load_subtopic_config(topic_name, subtopic_name)
    subtopic_cfg.phases = [p for p in subtopic_cfg.phases if p.name != name]
    if subtopic_cfg.current_phase == name:
        subtopic_cfg.current_phase = ""
    save_subtopic_config(topic_name, subtopic_name, subtopic_cfg)

    typer.echo(f"Deleted phase: {name}")


@app.command()
def status():
    """Show all phases and their status."""
    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    _, _, _, subtopic_cfg, phase_name, _ = ctx

    for p in subtopic_cfg.phases:
        marker = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[p.status]
        current = " ← current" if p.name == phase_name else ""
        typer.echo(f"  {marker} {p.name}{current}")
