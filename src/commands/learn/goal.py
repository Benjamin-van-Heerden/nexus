"""Goal subcommand — manage goals in the active phase."""

import typer

from src.models.learn.phase import Goal
from src.utils.learn import get_active_context, get_current_goal, get_topic_dir, save_phase_config

app = typer.Typer()

TOPIC_OPT = typer.Option("", help="Topic (defaults to current topic)")
SUBTOPIC_OPT = typer.Option("", help="Subtopic (defaults to current subtopic)")


@app.command()
def complete(
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Mark the current goal as completed. Fails if there are open tasks."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo("No current goal set.")
        raise typer.Exit(1)

    # Check for open tasks
    open_tasks = [t for t in goal.tasks if t.status != "completed"]
    if open_tasks:
        typer.echo(
            f"Cannot complete goal '{goal.name}' — {len(open_tasks)} open task(s):"
        )
        for t in open_tasks:
            typer.echo(f"  [ ] [{t.type}] {t.name}")
        raise typer.Exit(1)

    goal.status = "completed"

    # Advance to next incomplete goal
    goal_names = [g.name for g in phase_cfg.goals]
    current_idx = goal_names.index(goal.name)
    next_goal = None

    for g in phase_cfg.goals[current_idx + 1 :]:
        if g.status != "completed":
            next_goal = g
            break

    if next_goal:
        next_goal.status = "in_progress"
        phase_cfg.current_goal = next_goal.name
        save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
        typer.echo(f"Goal '{goal.name}' completed. Now on: {next_goal.name}")
    else:
        phase_cfg.current_goal = ""
        save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
        typer.echo(f"Goal '{goal.name}' completed. All goals in this phase are done!")
        typer.echo("Run `nexus learn phase complete` to advance to the next phase.")


@app.command()
def new(
    name: str = typer.Argument(help="Goal name"),
    reference: str = typer.Argument(help="Reference document path (relative to topic dir, e.g. reference/doc.md)"),
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Add a new goal to the active phase. Requires a reference document."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx

    topic_dir = get_topic_dir(topic_name)
    ref_path = topic_dir / reference
    if not ref_path.exists():
        typer.echo(f"Reference does not exist: {ref_path.resolve()}")
        typer.echo("Create the reference document first, then create the goal.")
        raise typer.Exit(1)

    phase_cfg.goals.append(Goal(name=name, reference=reference))

    # If this is the first goal, make it current
    if not phase_cfg.current_goal:
        phase_cfg.current_goal = name
        phase_cfg.goals[-1].status = "in_progress"

    save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
    typer.echo(f"Added goal: {name}")
    typer.echo(f"Reference: {ref_path.resolve()}")
    typer.echo('Next: create tasks with `nexus learn task new "description" --type practical`')


@app.command()
def delete(
    name: str = typer.Argument(help="Goal name to delete"),
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Delete a goal from the active phase."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx

    original_len = len(phase_cfg.goals)
    phase_cfg.goals = [g for g in phase_cfg.goals if g.name.lower() != name.lower()]

    if len(phase_cfg.goals) == original_len:
        typer.echo(f"Goal not found: {name}")
        raise typer.Exit(1)

    if phase_cfg.current_goal.lower() == name.lower():
        phase_cfg.current_goal = ""

    save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
    typer.echo(f"Deleted goal: {name}")


@app.command(name="set")
def set_goal(
    name: str = typer.Argument(help="Goal name to set as current"),
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Set the current goal."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, phase_name, phase_cfg = ctx

    for goal in phase_cfg.goals:
        if goal.name.lower() == name.lower():
            phase_cfg.current_goal = goal.name
            if goal.status == "todo":
                goal.status = "in_progress"
            save_phase_config(topic_name, subtopic_name, phase_name, phase_cfg)
            typer.echo(f"Current goal set to: {goal.name}")
            return

    typer.echo(f"Goal not found: {name}")
    raise typer.Exit(1)


@app.command(name="list")
def list_goals(
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """List all goals in the active phase."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    _, _, _, _, _, phase_cfg = ctx

    if not phase_cfg.goals:
        typer.echo("No goals in current phase.")
        return

    for goal in phase_cfg.goals:
        marker = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[goal.status]
        current = " ← current" if goal.name == phase_cfg.current_goal else ""
        task_count = len(goal.tasks)
        done_count = sum(1 for t in goal.tasks if t.status == "completed")
        task_info = f" ({done_count}/{task_count} tasks)" if task_count else ""
        typer.echo(f"  {marker} {goal.name}{task_info}{current}")


@app.command()
def status(
    topic: str = TOPIC_OPT,
    subtopic: str = SUBTOPIC_OPT,
):
    """Show detailed status of the current goal."""
    ctx = get_active_context(topic, subtopic)
    if not ctx:
        typer.echo("No active learning context.")
        raise typer.Exit(1)

    topic_name, _, subtopic_name, _, _, phase_cfg = ctx
    goal = get_current_goal(phase_cfg)
    if not goal:
        typer.echo("No current goal set.")
        raise typer.Exit(1)

    topic_dir = get_topic_dir(topic_name)
    ref_abs = (topic_dir / goal.reference).resolve()

    typer.echo(f"Goal: {goal.name}")
    typer.echo(f"Status: {goal.status}")
    typer.echo(f"Reference: {ref_abs}")

    if goal.tasks:
        typer.echo(
            f"\nTasks ({sum(1 for t in goal.tasks if t.status == 'completed')}/{len(goal.tasks)} completed):"
        )
        for task in goal.tasks:
            marker = "[x]" if task.status == "completed" else "[ ]"
            typer.echo(f"  {marker} [{task.type}] {task.name}")
    else:
        typer.echo("\nNo tasks yet.")
