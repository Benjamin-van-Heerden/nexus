"""Task CRUD commands for the management system."""

from datetime import date, datetime

import typer

from src.models.management.index import IndexEntry
from src.models.management.task import TaskConfig
from src.utils.management import (
    add_to_index,
    get_subtasks,
    get_task_tree,
    get_tasks_dir,
    load_index,
    load_task,
    move_to_completed,
    next_occurrence,
    remove_from_index,
    resolve_slug,
    save_task,
    slugify,
)
from src.utils.path_resolution import to_stored_path

app = typer.Typer()


def _parse_due(due_str: str) -> datetime | date:
    """Parse a due date/datetime string."""
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(due_str, fmt)
            if "T" in due_str:
                return dt
            return dt.date()
        except ValueError:
            continue
    raise typer.BadParameter(f"Invalid date format: '{due_str}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM")


@app.command()
def new(
    title: str = typer.Argument(help="Task title"),
    description: str = typer.Option("", help="Task description"),
    due: str = typer.Option("", help="Due date (YYYY-MM-DD) or datetime (YYYY-MM-DDTHH:MM)"),
    recur: str = typer.Option("", help="Recurrence pattern (3-field cron: 'dom month dow')"),
    parent: str = typer.Option("", help="Parent task slug or name"),
    tag: list[str] = typer.Option([], help="Tags (repeatable)"),
):
    """Create a new task."""
    slug = slugify(title)
    now = datetime.now()

    due_value = _parse_due(due) if due else None

    task = TaskConfig(
        name=title,
        slug=slug,
        description=description,
        status="todo",
        created=date.today(),
        due=due_value,
        tags=tag,
        recurrence=recur,
        last_modified=now,
        parent=parent,
    )

    if parent:
        parent_entry = resolve_slug(parent)
        parent_path = _resolve_path(parent_entry.path)
        parent_task = load_task(parent_path)

        subtask_dir = parent_path.with_suffix("")
        subtask_dir.mkdir(parents=True, exist_ok=True)

        task.parent = parent_entry.slug
        task_path = subtask_dir / f"{slug}.toml"

        if not parent_task.has_subtasks:
            parent_task.has_subtasks = True
            parent_task.last_modified = now
            save_task(parent_path, parent_task)
    else:
        tasks_dir = get_tasks_dir()
        tasks_dir.mkdir(parents=True, exist_ok=True)
        task_path = tasks_dir / f"{slug}.toml"

    if task_path.exists():
        typer.echo(f"Task already exists: {slug}")
        raise typer.Exit(1)

    save_task(task_path, task)

    entry = IndexEntry(
        slug=slug,
        name=title,
        path=to_stored_path(task_path),
        due=due_value,
        parent=task.parent,
    )
    add_to_index(entry)

    typer.echo(f"Created task: {title}")
    if due_value:
        typer.echo(f"  Due: {due_value}")
    if recur:
        nxt = next_occurrence(recur)
        typer.echo(f"  Recurrence: {recur} (next: {nxt})")
    if parent:
        typer.echo(f"  Parent: {task.parent}")
    if tag:
        typer.echo(f"  Tags: {', '.join(tag)}")


@app.command(name="list")
def list_tasks(
    tag: str = typer.Option("", help="Filter by tag"),
    due: str = typer.Option("", help="Filter by due window: today, week, month"),
    flat: bool = typer.Option(False, help="Flat list instead of tree view"),
):
    """List active tasks."""
    index = load_index()

    if not index.tasks:
        typer.echo("No active tasks.")
        return

    tasks = index.tasks

    if tag:
        tagged_slugs = set()
        for entry in tasks:
            task = load_task(_resolve_path(entry.path))
            if tag in task.tags:
                tagged_slugs.add(entry.slug)
        tasks = [t for t in tasks if t.slug in tagged_slugs]

    if due:
        today = date.today()
        if due == "today":
            end = today
        elif due == "week":
            end = today + __import__("datetime").timedelta(days=7)
        elif due == "month":
            end = today + __import__("datetime").timedelta(days=30)
        else:
            typer.echo("Invalid --due value. Use: today, week, month")
            raise typer.Exit(1)
        filtered_slugs = set()
        for t in tasks:
            if t.due is not None:
                due_date = t.due.date() if isinstance(t.due, datetime) else t.due
                if due_date <= end:
                    filtered_slugs.add(t.slug)
        tasks = [t for t in tasks if t.slug in filtered_slugs]

    if not tasks:
        typer.echo("No tasks match the filter.")
        return

    if flat:
        for t in tasks:
            due_str = f" (due: {t.due})" if t.due else ""
            typer.echo(f"  {t.name}{due_str}")
        return

    top_level = [t for t in tasks if not t.parent]
    all_slugs = {t.slug for t in tasks}

    def _print_tree(entry: IndexEntry, indent: int = 0) -> None:
        due_str = f" (due: {entry.due})" if entry.due else ""
        prefix = "  " * indent + "- "
        typer.echo(f"{prefix}{entry.name}{due_str}")
        children = [t for t in tasks if t.parent == entry.slug]
        for child in children:
            _print_tree(child, indent + 1)

    for entry in top_level:
        _print_tree(entry)


@app.command()
def show(slug: str = typer.Argument(help="Task slug or name")):
    """Show task details."""
    entry = resolve_slug(slug)
    task = load_task(_resolve_path(entry.path))

    typer.echo(f"Name: {task.name}")
    typer.echo(f"Slug: {task.slug}")
    typer.echo(f"Status: {task.status}")
    typer.echo(f"Created: {task.created}")
    if task.description:
        typer.echo(f"Description: {task.description}")
    if task.due:
        typer.echo(f"Due: {task.due}")
    if task.tags:
        typer.echo(f"Tags: {', '.join(task.tags)}")
    if task.recurrence:
        nxt = next_occurrence(task.recurrence)
        typer.echo(f"Recurrence: {task.recurrence} (next: {nxt})")
    if task.parent:
        typer.echo(f"Parent: {task.parent}")
    if task.completed_at:
        typer.echo(f"Completed: {task.completed_at}")
    if task.gcal_event_id:
        typer.echo(f"GCal Event: {task.gcal_event_id}")
    typer.echo(f"Last modified: {task.last_modified}")

    if task.has_subtasks:
        typer.echo("\nSubtasks:")
        tree = get_task_tree(task.slug)
        for sub_entry, depth in tree:
            sub_task = load_task(_resolve_path(sub_entry.path))
            status_marker = "✓" if sub_task.status == "completed" else "○"
            prefix = "  " * (depth + 1)
            typer.echo(f"{prefix}{status_marker} {sub_entry.name}")


@app.command()
def complete(
    slug: str = typer.Argument(help="Task slug or name"),
    force: bool = typer.Option(False, help="Force completion even if subtasks are incomplete"),
):
    """Mark a task as completed."""
    entry = resolve_slug(slug)
    task = load_task(_resolve_path(entry.path))

    if task.has_subtasks and not force:
        subtasks = get_subtasks(task.slug)
        incomplete = []
        for sub in subtasks:
            sub_task = load_task(_resolve_path(sub.path))
            if sub_task.status != "completed":
                incomplete.append(sub.name)
        if incomplete:
            typer.echo("Cannot complete — subtasks are incomplete:")
            for name in incomplete:
                typer.echo(f"  - {name}")
            typer.echo("Use --force to complete anyway.")
            raise typer.Exit(1)

    now = datetime.now()

    if task.recurrence:
        task.status = "todo"
        task.completed_at = date.today()
        task.last_modified = now
        nxt = next_occurrence(task.recurrence)
        if nxt:
            task.due = nxt
        save_task(_resolve_path(entry.path), task)
        typer.echo(f"Completed recurring task: {task.name}")
        typer.echo(f"  Next due: {nxt}")
        return

    task.status = "completed"
    task.completed_at = date.today()
    task.last_modified = now
    save_task(_resolve_path(entry.path), task)

    if task.parent:
        # Subtasks stay in place — only top-level tasks move to completed/
        typer.echo(f"Completed: {task.name}")
    else:
        move_to_completed(task.slug)
        typer.echo(f"Completed: {task.name}")


@app.command()
def edit(
    slug: str = typer.Argument(help="Task slug or name"),
    due: str = typer.Option("", help="New due date (YYYY-MM-DD or YYYY-MM-DDTHH:MM)"),
    description: str = typer.Option("", help="New description"),
    tag: list[str] = typer.Option([], help="Add tags"),
    remove_tag: list[str] = typer.Option([], help="Remove tags"),
    status: str = typer.Option("", help="New status: todo, in_progress, completed"),
):
    """Edit task fields."""
    entry = resolve_slug(slug)
    task_path = _resolve_path(entry.path)
    task = load_task(task_path)

    changed = False

    if due:
        task.due = _parse_due(due)
        changed = True
    if description:
        task.description = description
        changed = True
    if tag:
        task.tags = list(set(task.tags + tag))
        changed = True
    if remove_tag:
        task.tags = [t for t in task.tags if t not in remove_tag]
        changed = True
    if status:
        if status not in ("todo", "in_progress", "completed"):
            typer.echo("Invalid status. Use: todo, in_progress, completed")
            raise typer.Exit(1)
        task.status = status
        changed = True

    if not changed:
        typer.echo("No changes specified.")
        return

    task.last_modified = datetime.now()
    save_task(task_path, task)

    if due:
        from src.utils.management import update_index_entry
        update_index_entry(task.slug, due=task.due)

    typer.echo(f"Updated: {task.name}")


@app.command()
def delete(slug: str = typer.Argument(help="Task slug or name")):
    """Delete a task and its subtasks."""
    import shutil

    entry = resolve_slug(slug)
    task = load_task(_resolve_path(entry.path))

    subtask_count = len(get_task_tree(task.slug))
    msg = f"Delete task '{task.name}'"
    if subtask_count > 0:
        msg += f" and {subtask_count} subtask(s)"
    msg += "?"

    typer.confirm(msg, abort=True)

    task_path = _resolve_path(entry.path)
    subtask_dir = task_path.with_suffix("")

    if subtask_dir.is_dir():
        shutil.rmtree(subtask_dir)
    if task_path.exists():
        task_path.unlink()

    index = load_index()
    slugs_to_remove = {task.slug}

    def _collect(parent: str) -> None:
        for t in index.tasks:
            if t.parent == parent and t.slug not in slugs_to_remove:
                slugs_to_remove.add(t.slug)
                _collect(t.slug)

    _collect(task.slug)

    for s in slugs_to_remove:
        remove_from_index(s)

    typer.echo(f"Deleted: {task.name}")


def _resolve_path(stored_path: str):
    """Resolve a stored ./ path to absolute Path."""
    from src.utils.path_resolution import resolve
    return resolve(stored_path)
