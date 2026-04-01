"""Manage system utilities.

Handles TOML I/O, index management, slug resolution, cron helpers,
and task tree operations for the manage system.
"""

import re
import shutil
import tomllib
from datetime import date, datetime, timedelta
from pathlib import Path

import tomli_w
from src.models.manage.contact import ContactConfig
from src.models.manage.index import IndexEntry, ManageIndex
from src.models.manage.task import TaskConfig

from src.utils.paths import get_manage_dir

# -- TOML I/O --


def _load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _save_toml(path: Path, data: dict) -> None:
    with open(path, "wb") as f:
        tomli_w.dump(data, f, multiline_strings=True)


def load_task(path: Path) -> TaskConfig:
    return TaskConfig(**_load_toml(path))


def save_task(path: Path, task: TaskConfig) -> None:
    _save_toml(path, task.model_dump(mode="json", exclude_none=True))


def load_contact(path: Path) -> ContactConfig:
    return ContactConfig(**_load_toml(path))


def save_contact(path: Path, contact: ContactConfig) -> None:
    _save_toml(path, contact.model_dump(mode="json", exclude_none=True))


def load_index() -> ManageIndex:
    path = get_manage_dir() / "index.toml"
    if not path.exists():
        return ManageIndex()
    raw = _load_toml(path)
    return ManageIndex(**raw)


def save_index(index: ManageIndex) -> None:
    path = get_manage_dir() / "index.toml"
    _save_toml(path, index.model_dump(mode="json", exclude_none=True))


# -- Index management --


def add_to_index(entry: IndexEntry) -> None:
    index = load_index()
    index.tasks.append(entry)
    save_index(index)


def remove_from_index(slug: str) -> None:
    index = load_index()
    index.tasks = [t for t in index.tasks if t.slug != slug]
    save_index(index)


def update_index_entry(slug: str, **fields) -> None:
    index = load_index()
    for task in index.tasks:
        if task.slug == slug:
            for key, value in fields.items():
                setattr(task, key, value)
            break
    save_index(index)


# -- Slug helpers --


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


def resolve_slug(slug_or_name: str) -> IndexEntry:
    """Resolve a slug or name to an IndexEntry.

    Accepts exact slug or name (converted to slug). Raises typer.Exit on
    ambiguous or not-found results.
    """
    import typer

    index = load_index()
    candidate = slugify(slug_or_name)

    matches = [t for t in index.tasks if t.slug == candidate or t.slug == slug_or_name]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        typer.echo(f"Ambiguous slug '{slug_or_name}'. Matches:")
        for m in matches:
            typer.echo(f"  - {m.slug} ({m.name})")
        raise typer.Exit(1)

    name_matches = [t for t in index.tasks if t.name.lower() == slug_or_name.lower()]
    if len(name_matches) == 1:
        return name_matches[0]
    if len(name_matches) > 1:
        typer.echo(f"Ambiguous name '{slug_or_name}'. Matches:")
        for m in name_matches:
            typer.echo(f"  - {m.slug} ({m.name})")
        raise typer.Exit(1)

    typer.echo(f"Task not found: '{slug_or_name}'")
    raise typer.Exit(1)


# -- Contact slug resolution --


def resolve_contact_slug(slug_or_name: str) -> Path:
    """Resolve a contact slug or name to its TOML file path.

    Scans manage/contacts/ directory. Raises typer.Exit if not found.
    """
    import typer

    contacts_dir = get_contacts_dir()
    candidate = slugify(slug_or_name)

    path = contacts_dir / f"{candidate}.toml"
    if path.exists():
        return path

    for toml_file in contacts_dir.glob("*.toml"):
        contact = load_contact(toml_file)
        if contact.name.lower() == slug_or_name.lower():
            return toml_file

    typer.echo(f"Contact not found: '{slug_or_name}'")
    raise typer.Exit(1)


# -- Path helpers --


def get_tasks_dir() -> Path:
    return get_manage_dir() / "tasks"


def get_completed_dir() -> Path:
    return get_manage_dir() / "completed"


def get_contacts_dir() -> Path:
    return get_manage_dir() / "contacts"


def get_sync_dir() -> Path:
    return get_manage_dir() / "sync"


# -- Cron helpers --


def parse_recurrence(cron_3field: str) -> tuple[str, str, str]:
    """Parse a 3-field cron string: 'dom month dow'.

    Returns (dom, month, dow) as strings.
    """
    parts = cron_3field.strip().split()
    if len(parts) != 3:
        raise ValueError(
            f"Expected 3-field cron format 'dom month dow', got: '{cron_3field}'"
        )
    return parts[0], parts[1], parts[2]


def _parse_cron_field(field: str, min_val: int, max_val: int) -> list[int]:
    """Parse a single cron field into a list of matching values."""
    if field == "*":
        return list(range(min_val, max_val + 1))

    values = set()
    for part in field.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            values.update(range(int(start), int(end) + 1))
        else:
            values.add(int(part))
    return sorted(values)


def next_occurrence(cron_3field: str, after: datetime | None = None) -> date | None:
    """Calculate the next occurrence from a 3-field cron pattern.

    Searches up to 2 years ahead. Returns None if no match found.
    """
    if after is None:
        after = datetime.now()

    dom_str, month_str, dow_str = parse_recurrence(cron_3field)

    dom_values = _parse_cron_field(dom_str, 1, 31)
    month_values = _parse_cron_field(month_str, 1, 12)
    dow_values = _parse_cron_field(dow_str, 0, 6)

    has_dom = dom_str != "*"
    has_month = month_str != "*"
    has_dow = dow_str != "*"

    check_date = after.date() + timedelta(days=1)
    end_date = check_date + timedelta(days=730)

    while check_date <= end_date:
        month_ok = check_date.month in month_values
        dom_ok = check_date.day in dom_values
        dow_ok = (
            check_date.isoweekday() % 7 in dow_values
        )  # isoweekday: Mon=1..Sun=7, cron: Sun=0..Sat=6

        if has_dow and not has_dom and not has_month:
            if dow_ok:
                return check_date
        elif has_dom and has_month and not has_dow:
            if month_ok and dom_ok:
                return check_date
        elif has_dom and not has_month and not has_dow:
            if dom_ok:
                return check_date
        else:
            if month_ok and dom_ok and dow_ok:
                return check_date

        check_date += timedelta(days=1)

    return None


def is_due_in_window(cron_3field: str, days: int = 14) -> bool:
    """Check if the next occurrence of a cron pattern is within the given window."""
    nxt = next_occurrence(cron_3field)
    if nxt is None:
        return False
    return nxt <= date.today() + timedelta(days=days)


# -- Task tree helpers --


def get_subtasks(slug: str) -> list[IndexEntry]:
    """Get direct children of a task from the index."""
    index = load_index()
    return [t for t in index.tasks if t.parent == slug]


def get_task_tree(slug: str) -> list[tuple[IndexEntry, int]]:
    """Get a recursive tree of task + all descendants.

    Returns list of (entry, depth) tuples.
    """
    result = []

    def _walk(parent_slug: str, depth: int) -> None:
        children = get_subtasks(parent_slug)
        for child in children:
            result.append((child, depth))
            _walk(child.slug, depth + 1)

    _walk(slug, 0)
    return result


def move_to_completed(slug: str) -> None:
    """Move a task (and its subtask directory) to completed/, preserving structure.

    The path relative to tasks/ is mirrored under completed/.
    Removes the task and all descendants from the index.
    """
    from src.utils.path_resolution import resolve

    index = load_index()
    entry = None
    for t in index.tasks:
        if t.slug == slug:
            entry = t
            break

    if entry is None:
        return

    task_path = resolve(entry.path)
    tasks_dir = get_tasks_dir()
    completed_dir = get_completed_dir()

    # Preserve relative path from tasks/ into completed/
    try:
        rel = task_path.relative_to(tasks_dir)
    except ValueError:
        rel = Path(task_path.name)

    dest = completed_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    if task_path.exists():
        shutil.move(str(task_path), str(dest))

    # Move subtask directory too (same relative structure)
    subtask_dir = task_path.with_suffix("")
    if subtask_dir.is_dir():
        subtask_dest = completed_dir / rel.with_suffix("")
        shutil.move(str(subtask_dir), str(subtask_dest))

    slugs_to_remove = {slug}

    def _collect_descendants(parent: str) -> None:
        for t in index.tasks:
            if t.parent == parent and t.slug not in slugs_to_remove:
                slugs_to_remove.add(t.slug)
                _collect_descendants(t.slug)

    _collect_descendants(slug)

    index.tasks = [t for t in index.tasks if t.slug not in slugs_to_remove]
    save_index(index)
