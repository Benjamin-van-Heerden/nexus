"""Task subcommand — manage tasks under the current goal."""

from datetime import date

import typer

from src.models.learn.phase import Task
from src.utils.learn import get_active_context, get_current_goal, save_phase_config
from src.utils.path_resolution import resolve_str, to_stored_path

app = typer.Typer()

TOPIC_OPT = typer.Option("", help="Topic (defaults to current topic)")
SUBTOPIC_OPT = typer.Option("", help="Subtopic (defaults to current subtopic)")


@app.command()
def new(
    description: str = typer.Argument(help="Task description"),
    type: str = typer.Option(
        "practical", help="Task type: practical, theoretical, quiz"
    ),
    relevant_files: list[str] = typer.Option(
        [], "--file", "-f", help="Relevant file paths (e.g. ./learn/jax/from-scratch/foundations/practical/examples/2026-03-30.py)"
    ),
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Add a new task to the current goal. Blocked if there are incomplete tasks from a previous day."""
    if not relevant_files:
        typer.echo("Error: At least one --file/-f is required. Every task must be linked to a concrete file.")
        typer.echo('  Example: nexus learn task new "description" --type practical -f "./learn/jax/.../file.py"')
        raise typer.Exit(1)

    if type not in ("practical", "theoretical", "quiz"):
        typer.echo(f"Invalid type: {type}. Must be: practical, theoretical, quiz")
        raise typer.Exit(1)

    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo('No current goal set. Set one with `nexus learn goal set "name"`')
        raise typer.Exit(1)

    today = date.today()
    dangling = [t for t in goal.tasks if t.status == "todo" and t.created < today]
    if dangling:
        typer.echo("Cannot create new tasks — the user still has incomplete tasks from previous work on this topic:")
        typer.echo()
        for t in dangling:
            typer.echo(f"  [{t.type}] {t.name} (created {t.created.isoformat()})")
            for f in t.relevant_files:
                typer.echo(f"    file: {resolve_str(f)}")
        typer.echo()
        typer.echo("Report these to the user and ask them to complete or address them first.")
        raise typer.Exit(1)

    stored_files = [to_stored_path(f) for f in relevant_files]
    goal.tasks.append(Task(name=description, type=type, created=today, relevant_files=stored_files))
    save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)

    typer.echo(f"Added {type} task to '{goal.name}': {description}")
    if stored_files:
        for f in stored_files:
            typer.echo(f"  file: {resolve_str(f)}")


@app.command()
def complete(
    description: str = typer.Argument(help="Task description to mark complete"),
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Mark a task as completed."""
    ctx = get_active_context(topic, subtopic)
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
            task.completed = date.today()
            save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
            typer.echo(f"Completed: {task.name}")

            if task.relevant_files:
                typer.echo("\nRelevant files:")
                for f in task.relevant_files:
                    typer.echo(f"  {resolve_str(f)}")

            remaining = [t for t in goal.tasks if t.status != "completed"]
            if remaining:
                typer.echo(f"\n{len(remaining)} task(s) remaining in this goal:")
                for t in remaining:
                    typer.echo(f"  [ ] [{t.type}] {t.name}")
            else:
                typer.echo(f"\nAll tasks in '{goal.name}' are complete. New exercises will be composed next session.")
            typer.echo()
            typer.echo("Remember to log a record of what the USER did (not agent actions):")
            typer.echo("IMPORTANT: Always ask the user how long the work took — never assume duration.")
            typer.echo('  nexus learn record "what the user accomplished, struggled with, feedback" --duration "Xmin" --type ...')
            return

    typer.echo(f"Task not found: {description}")
    raise typer.Exit(1)


@app.command(name="list")
def list_tasks(
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """List all tasks in the current goal."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, _, phase_cfg = ctx
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
        date_info = f" (created {task.created.isoformat()}"
        if task.completed:
            date_info += f", completed {task.completed.isoformat()}"
        date_info += ")"
        typer.echo(f"  {marker} [{task.type}] {task.name}{date_info}")
        for f in task.relevant_files:
            typer.echo(f"      file: {resolve_str(f)}")
