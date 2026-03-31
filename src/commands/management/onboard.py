"""Onboard and upcoming commands — context dump for agents and quick daily check.

Reminder windows:
- Birthdays: at 7 days out, then daily from 2 days out (2 days, tomorrow, today)
- Recurring tasks: only on the day of
- Open todos: always shown
- Tasks with due dates: from 1 day out (tomorrow, today) + overdue
"""

from datetime import date, datetime, timedelta
from pathlib import Path

import typer

from src.utils.management import (
    get_contacts_dir,
    load_contact,
    load_index,
    load_task,
    next_occurrence,
)
from src.utils.path_resolution import resolve


def _has_time(due: datetime | date | None) -> bool:
    """Check if a due value has meaningful time info (not midnight)."""
    if due is None:
        return False
    if isinstance(due, datetime):
        return due.hour != 0 or due.minute != 0
    return False


def _format_task_name(entry) -> str:
    """Format a task name with parent context if it's a subtask."""
    if entry.parent:
        index = load_index()
        for t in index.tasks:
            if t.slug == entry.parent:
                return f"{entry.name} (of {t.name})"
        return entry.name
    return entry.name


def _get_overdue_tasks() -> list[tuple[str, str, date, int]]:
    """Return (display_name, slug, due_date, days_overdue) for overdue non-recurring tasks."""
    index = load_index()
    today = date.today()
    results = []
    for entry in index.tasks:
        if entry.due is None:
            continue
        task = load_task(resolve(entry.path))
        if task.recurrence:
            continue
        due_date = entry.due.date() if isinstance(entry.due, datetime) else entry.due
        if due_date < today and task.status != "completed":
            days = (today - due_date).days
            results.append((_format_task_name(entry), entry.slug, due_date, days))
    return sorted(results, key=lambda x: x[2])


def _get_due_on(target: date) -> list[tuple[str, str, date | datetime]]:
    """Return non-recurring tasks due on a specific date."""
    index = load_index()
    results = []
    for entry in index.tasks:
        if entry.due is None:
            continue
        task = load_task(resolve(entry.path))
        if task.recurrence:
            continue
        due_date = entry.due.date() if isinstance(entry.due, datetime) else entry.due
        if due_date == target:
            results.append((_format_task_name(entry), entry.slug, entry.due))
    return sorted(results, key=lambda x: x[2])


def _get_birthday_reminders() -> list[tuple[str, date, int | None, str]]:
    """Return (name, bday_date, age_or_none, message) for birthdays that should be shown.

    Shows at exactly 7 days out, then daily from 2 days out.
    """
    contacts_dir = get_contacts_dir()
    if not contacts_dir.exists():
        return []

    today = date.today()
    results = []

    for f in contacts_dir.glob("*.toml"):
        contact = load_contact(f)
        if not contact.birthday:
            continue
        bday_this_year = contact.birthday.replace(year=today.year)
        if bday_this_year < today:
            bday_this_year = contact.birthday.replace(year=today.year + 1)

        days_until = (bday_this_year - today).days
        age = bday_this_year.year - contact.birthday.year

        if days_until == 7:
            msg = f"{contact.name}'s birthday is in a week ({bday_this_year.strftime('%a %d %B')})"
        elif days_until == 2:
            msg = f"{contact.name}'s birthday is in 2 days"
        elif days_until == 1:
            msg = f"{contact.name}'s birthday is tomorrow"
        elif days_until == 0:
            msg = f"It's {contact.name}'s birthday today!"
        else:
            continue

        age_str = f" (turning {age})" if age else None
        if age_str:
            msg += age_str

        results.append((contact.name, bday_this_year, age, msg))

    return sorted(results, key=lambda x: x[1])


def _get_recurring_today() -> list[tuple[str, str]]:
    """Return (name, recurrence) for recurring tasks due today."""
    index = load_index()
    today = date.today()
    results = []
    for entry in index.tasks:
        task = load_task(resolve(entry.path))
        if not task.recurrence:
            continue
        nxt = next_occurrence(task.recurrence, datetime.now() - timedelta(days=1))
        if nxt and nxt == today:
            results.append((entry.name, task.recurrence))
    return results


def _get_open_todos() -> list[tuple[str, str, date]]:
    """Return (name, slug, created) for tasks with no due date and no recurrence."""
    index = load_index()
    results = []
    for entry in index.tasks:
        if entry.due is not None:
            continue
        task = load_task(resolve(entry.path))
        if task.recurrence or task.status == "completed":
            continue
        results.append((entry.name, entry.slug, task.created))
    return results


def _print_task_tree():
    """Print hierarchical view of all active tasks."""
    index = load_index()
    top_level = [t for t in index.tasks if not t.parent]

    def _print_entry(entry, indent=0):
        task = load_task(resolve(entry.path))
        status = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[task.status]
        due_str = f" (due: {entry.due})" if entry.due else ""
        recur_str = f" [recurring: {task.recurrence}]" if task.recurrence else ""
        tags_str = f" #{' #'.join(task.tags)}" if task.tags else ""
        prefix = "  " * indent
        print(f"{prefix}{status} {entry.name}{due_str}{recur_str}{tags_str}")
        children = [t for t in index.tasks if t.parent == entry.slug]
        for child in children:
            _print_entry(child, indent + 1)

    for entry in top_level:
        _print_entry(entry)


def onboard():
    """Full management context dump for agents."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    print("=" * 60)
    print("NEXUS MANAGE ONBOARD")
    print("=" * 60)
    print(f"Date: {today.strftime('%A, %B %d, %Y')}")
    print()

    # 1. Overdue tasks
    overdue = _get_overdue_tasks()
    if overdue:
        print("-" * 60)
        print("OVERDUE TASKS")
        print("-" * 60)
        for name, slug, due_date, days in overdue:
            print(f"  ⚠ {name} — due {due_date} ({days} day(s) overdue)")
        print()

    # 2. Due today
    due_today = _get_due_on(today)
    if due_today:
        print("-" * 60)
        print("DUE TODAY")
        print("-" * 60)
        for name, slug, due in due_today:
            time_str = f" at {due.strftime('%H:%M')}" if _has_time(due) else ""
            print(f"  Remember {name} is due today{time_str}")
        print()

    # 3. Due tomorrow
    due_tomorrow = _get_due_on(tomorrow)
    if due_tomorrow:
        print("-" * 60)
        print("DUE TOMORROW")
        print("-" * 60)
        for name, slug, due in due_tomorrow:
            time_str = f" at {due.strftime('%H:%M')}" if _has_time(due) else ""
            print(f"  Remember you have {name} tomorrow{time_str}")
        print()

    # 4. Birthday reminders
    birthdays = _get_birthday_reminders()
    if birthdays:
        print("-" * 60)
        print("BIRTHDAYS")
        print("-" * 60)
        for name, bday, age, msg in birthdays:
            print(f"  🎂 {msg}")
        print()

    # 5. Recurring tasks due today
    recurring = _get_recurring_today()
    if recurring:
        print("-" * 60)
        print("RECURRING (today)")
        print("-" * 60)
        for name, recur in recurring:
            print(f"  ↻ {name}")
        print()

    # 6. Open todos (always shown)
    todos = _get_open_todos()
    if todos:
        print("-" * 60)
        print("OPEN TODOS")
        print("-" * 60)
        for name, slug, created in todos:
            print(f"  ○ {name} (created: {created})")
        print()

    # 7. Task tree
    index = load_index()
    if index.tasks:
        print("-" * 60)
        print("ALL ACTIVE TASKS")
        print("-" * 60)
        _print_task_tree()
        print()

    # 8. Agent instructions
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if instructions_path.exists():
        print("-" * 60)
        print("AGENT INSTRUCTIONS")
        print("-" * 60)
        print(instructions_path.read_text().strip())
        print()


def upcoming(
    days: int = typer.Option(14, help="Lookahead window in days"),
):
    """Show upcoming tasks, birthdays, and recurring events."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    print(f"Upcoming — {today.strftime('%A, %B %d, %Y')}")
    print()

    # Overdue
    overdue = _get_overdue_tasks()
    if overdue:
        print("OVERDUE:")
        for name, slug, due_date, days_overdue in overdue:
            print(f"  ⚠ {name} — due {due_date} ({days_overdue} day(s) overdue)")
        print()

    # Due today
    due_today = _get_due_on(today)
    if due_today:
        print("DUE TODAY:")
        for name, slug, due in due_today:
            time_str = f" at {due.strftime('%H:%M')}" if _has_time(due) else ""
            print(f"  Remember {name} is due today{time_str}")
        print()

    # Due tomorrow
    due_tomorrow = _get_due_on(tomorrow)
    if due_tomorrow:
        print("DUE TOMORROW:")
        for name, slug, due in due_tomorrow:
            time_str = f" at {due.strftime('%H:%M')}" if _has_time(due) else ""
            print(f"  Remember you have {name} tomorrow{time_str}")
        print()

    # Birthdays
    birthdays = _get_birthday_reminders()
    if birthdays:
        print("BIRTHDAYS:")
        for name, bday, age, msg in birthdays:
            print(f"  🎂 {msg}")
        print()

    # Recurring today
    recurring = _get_recurring_today()
    if recurring:
        print("RECURRING (today):")
        for name, recur in recurring:
            print(f"  ↻ {name}")
        print()

    # Open todos (always shown)
    todos = _get_open_todos()
    if todos:
        print("OPEN TODOS:")
        for name, slug, created in todos:
            print(f"  ○ {name} (created: {created})")
        print()

    if not overdue and not due_today and not due_tomorrow and not birthdays and not recurring and not todos:
        print("Nothing upcoming.")
