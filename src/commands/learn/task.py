"""Task subcommand — manage tasks under the current goal."""

import typer

from src.models.learn.phase import Task
from src.utils.learn import get_active_context, get_current_goal, save_phase_config

app = typer.Typer()


@app.command()
def new(
    description: str = typer.Argument(help="Task description"),
    type: str = typer.Option(
        "practical", help="Task type: practical, theoretical, quiz"
    ),
):
    """Add a new task to the current goal."""
    if type not in ("practical", "theoretical", "quiz"):
        typer.echo(f"Invalid type: {type}. Must be: practical, theoretical, quiz")
        raise typer.Exit(1)

    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo('No current goal set. Set one with `nexus learn goal set "name"`')
        raise typer.Exit(1)

    goal.tasks.append(Task(name=description, type=type))
    save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
    typer.echo(f"Added {type} task to '{goal.name}': {description}")


@app.command()
def complete(
    description: str = typer.Argument(help="Task description to mark complete"),
):
    """Mark a task as completed."""
    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo("No current goal set.")
        raise typer.Exit(1)

    for task in goal.tasks:
        if task.name.lower() == description.lower():
            task.status = "completed"
            save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
            typer.echo(f"Completed: {task.name}")
            return

    typer.echo(f"Task not found: {description}")
    raise typer.Exit(1)


@app.command(name="list")
def list_tasks():
    """List all tasks in the current goal."""
    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    _, _, _, _, _, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo("No current goal set.")
        raise typer.Exit(1)

    if not goal.tasks:
        typer.echo(f"No tasks for goal: {goal.name}")
        return

    typer.echo(f"Tasks for: {goal.name}\n")
    for task in goal.tasks:
        marker = "[x]" if task.status == "completed" else "[ ]"
        typer.echo(f"  {marker} [{task.type}] {task.name}")
