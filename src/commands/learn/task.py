"""Task subcommand — manage tasks under the current goal."""

from datetime import date

import typer

from src.models.learn.phase import Task
from src.utils.learn import get_active_context, get_current_goal, get_subtopic_dir, save_phase_config

app = typer.Typer()


@app.command()
def new(
    description: str = typer.Argument(help="Task description"),
    type: str = typer.Option(
        "practical", help="Task type: practical, theoretical, quiz"
    ),
    relevant_files: list[str] = typer.Option(
        [], "--file", "-f", help="Relevant file paths (relative to subtopic dir)"
    ),
):
    """Add a new task to the current goal. Blocked if there are incomplete tasks from a previous day."""
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

    today = date.today()
    dangling = [t for t in goal.tasks if t.status == "todo" and t.created < today]
    if dangling:
        subtopic_dir = get_subtopic_dir(topic_name, subtopic_name)
        typer.echo("Cannot create new tasks — the user still has incomplete tasks from previous work on this topic:")
        typer.echo()
        for t in dangling:
            typer.echo(f"  [{t.type}] {t.name} (created {t.created.isoformat()})")
            for f in t.relevant_files:
                typer.echo(f"    file: {(subtopic_dir / f).resolve()}")
        typer.echo()
        typer.echo("Report these to the user and ask them to complete or address them first.")
        raise typer.Exit(1)

    goal.tasks.append(Task(name=description, type=type, created=today, relevant_files=relevant_files))
    save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)

    typer.echo(f"Added {type} task to '{goal.name}': {description}")
    if relevant_files:
        subtopic_dir = get_subtopic_dir(topic_name, subtopic_name)
        for f in relevant_files:
            typer.echo(f"  file: {(subtopic_dir / f).resolve()}")


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
            task.completed = date.today()
            save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
            typer.echo(f"Completed: {task.name}")

            remaining = [t for t in goal.tasks if t.status != "completed"]
            if remaining:
                typer.echo(f"\n{len(remaining)} task(s) remaining in this goal:")
                for t in remaining:
                    typer.echo(f"  [ ] [{t.type}] {t.name}")
            else:
                typer.echo(f"\nAll tasks in '{goal.name}' are complete.")
                typer.echo("Run `nexus learn goal complete` to advance to the next goal.")
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

    topic_name, _, subtopic_name, _, _, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo("No current goal set.")
        raise typer.Exit(1)

    if not goal.tasks:
        typer.echo(f"No tasks for goal: {goal.name}")
        return

    subtopic_dir = get_subtopic_dir(topic_name, subtopic_name)

    typer.echo(f"Tasks for: {goal.name}\n")
    for task in goal.tasks:
        marker = "[x]" if task.status == "completed" else "[ ]"
        date_info = f" (created {task.created.isoformat()}"
        if task.completed:
            date_info += f", completed {task.completed.isoformat()}"
        date_info += ")"
        typer.echo(f"  {marker} [{task.type}] {task.name}{date_info}")
        for f in task.relevant_files:
            typer.echo(f"      file: {(subtopic_dir / f).resolve()}")
