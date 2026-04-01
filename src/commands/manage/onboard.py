"""Onboard, refresh, and upcoming commands.

Reminder windows:
- Birthdays: at 7 days out, then daily from 2 days out (2 days, tomorrow, today)
- Recurring tasks: only on the day of
- Open todos: always shown
- Tasks with due dates: from 1 day out (tomorrow, today) + overdue
- Due this week: 2-7 days out (onboard/refresh only, not daily reminders)
"""

import tomllib
from datetime import date, datetime, timedelta
from pathlib import Path

import typer

from src.utils.manage import (
    get_contacts_dir,
    get_sync_dir,
    load_contact,
    load_index,
    load_task,
    next_occurrence,
)
from src.utils.path_resolution import resolve
from src.utils.pause import check_pause
from src.utils.weather import fetch_weather_sync, format_weather, load_weather_config

# -- Display helpers --


def _has_time(due: datetime | date | None) -> bool:
    """Check if a due value has meaningful time info (not midnight)."""
    if due is None:
        return False
    if isinstance(due, datetime):
        return due.hour != 0 or due.minute != 0
    return False


def _format_due_display(due: datetime | date | None) -> str:
    """Format a due value for display — date only for all-day, time for timed events."""
    if due is None:
        return ""
    if _has_time(due):
        return due.strftime("%a %d %b at %H:%M")
    due_date = due.date() if isinstance(due, datetime) else due
    return due_date.strftime("%a %d %b")


def _format_task_name(entry) -> str:
    """Format a task name with parent context if it's a subtask."""
    if entry.parent:
        index = load_index()
        for t in index.tasks:
            if t.slug == entry.parent:
                return f"{entry.name} (of {t.name})"
    return entry.name


# -- Data helpers --


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


def _get_due_in_range(start: date, end: date) -> list[tuple[str, str, date | datetime]]:
    """Return non-recurring tasks due within a date range (inclusive)."""
    index = load_index()
    results = []
    for entry in index.tasks:
        if entry.due is None:
            continue
        task = load_task(resolve(entry.path))
        if task.recurrence:
            continue
        due_date = entry.due.date() if isinstance(entry.due, datetime) else entry.due
        if start <= due_date <= end:
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
        try:
            month = int(contact.birthday[:2])
            day = int(contact.birthday[3:])
        except (ValueError, IndexError):
            continue
        bday_this_year = date(today.year, month, day)
        if bday_this_year < today:
            bday_this_year = date(today.year + 1, month, day)

        days_until = (bday_this_year - today).days
        age = None
        if contact.birth_year is not None:
            age = bday_this_year.year - contact.birth_year

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

        if age:
            msg += f" (turning {age})"

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


def _get_last_sync_info() -> str | None:
    """Return last sync timestamp string, or None if never synced."""
    state_path = get_sync_dir() / "sync_state.toml"
    if not state_path.exists():
        return None
    with open(state_path, "rb") as f:
        state = tomllib.load(f)
    last = state.get("last_sync", "")
    return last if last else None


def _print_task_tree():
    """Print hierarchical view of all active tasks."""
    index = load_index()
    top_level = [t for t in index.tasks if not t.parent]

    def _print_entry(entry, indent=0):
        task = load_task(resolve(entry.path))
        status = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[task.status]
        due_str = f" ({_format_due_display(entry.due)})" if entry.due else ""
        recur_str = f" [recurring: {task.recurrence}]" if task.recurrence else ""
        tags_str = f" #{' #'.join(task.tags)}" if task.tags else ""
        prefix = "  " * indent
        print(f"{prefix}{status} {entry.name}{due_str}{recur_str}{tags_str}")
        children = [t for t in index.tasks if t.parent == entry.slug]
        for child in children:
            _print_entry(child, indent + 1)

    for entry in top_level:
        _print_entry(entry)


# -- Shared section printers --


def _print_actionable_sections():
    """Print all actionable sections (shared by onboard, refresh, upcoming)."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    has_content = False

    # Overdue
    overdue = _get_overdue_tasks()
    if overdue:
        print("-" * 60)
        print("OVERDUE")
        print("-" * 60)
        for name, slug, due_date, days in overdue:
            print(
                f"  ⚠ {name} — due {due_date.strftime('%a %d %b')} ({days} day(s) overdue)"
            )
        print()
        has_content = True

    # Due today
    due_today = _get_due_on(today)
    if due_today:
        print("-" * 60)
        print("TODAY")
        print("-" * 60)
        for name, slug, due in due_today:
            if _has_time(due):
                print(f"  {name} at {due.strftime('%H:%M')}")
            else:
                print(f"  {name}")
        print()
        has_content = True

    # Due tomorrow
    due_tomorrow = _get_due_on(tomorrow)
    if due_tomorrow:
        print("-" * 60)
        print("TOMORROW")
        print("-" * 60)
        for name, slug, due in due_tomorrow:
            if _has_time(due):
                print(f"  {name} at {due.strftime('%H:%M')}")
            else:
                print(f"  {name}")
        print()
        has_content = True

    # Due this week (2-7 days out)
    week_start = today + timedelta(days=2)
    week_end = today + timedelta(days=7)
    due_week = _get_due_in_range(week_start, week_end)
    if due_week:
        print("-" * 60)
        print("THIS WEEK")
        print("-" * 60)
        for name, slug, due in due_week:
            print(f"  {name} — {_format_due_display(due)}")
        print()
        has_content = True

    # Birthdays
    birthdays = _get_birthday_reminders()
    if birthdays:
        print("-" * 60)
        print("BIRTHDAYS")
        print("-" * 60)
        for name, bday, age, msg in birthdays:
            print(f"  🎂 {msg}")
        print()
        has_content = True

    # Recurring today
    recurring = _get_recurring_today()
    if recurring:
        print("-" * 60)
        print("RECURRING (today)")
        print("-" * 60)
        for name, recur in recurring:
            print(f"  ↻ {name}")
        print()
        has_content = True

    # Open todos (always shown)
    todos = _get_open_todos()
    if todos:
        print("-" * 60)
        print("OPEN TODOS")
        print("-" * 60)
        for name, slug, created in todos:
            print(f"  ○ {name} (created: {created})")
        print()
        has_content = True

    return has_content


def _print_weather() -> bool:
    """Print weather section if configured. Returns True if weather was shown."""
    config = load_weather_config()
    if not config:
        return False
    try:
        weather_data = fetch_weather_sync(config)
        print("-" * 60)
        print("WEATHER")
        print("-" * 60)
        print(format_weather(weather_data))
        print()
        return True
    except Exception:
        return False


# -- Commands --


def onboard():
    """Full manage context dump for agents."""
    paused = check_pause("manage")
    if paused:
        print(
            f"Nexus manage is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    today = date.today()

    print("=" * 60)
    print("NEXUS MANAGE ONBOARD")
    print("=" * 60)
    print(f"Date: {today.strftime('%A, %B %d, %Y')}")
    print("User: Benjamin van Heerden")
    print()

    # Last sync info
    last_sync = _get_last_sync_info()
    if last_sync:
        print(f"Last Google Calendar sync: {last_sync}")
    else:
        print("Google Calendar: never synced")
    print()

    # Weather
    _print_weather()

    # All actionable sections
    _print_actionable_sections()

    # Task tree
    index = load_index()
    if index.tasks:
        print("-" * 60)
        print("ALL ACTIVE TASKS")
        print("-" * 60)
        _print_task_tree()
        print()

    # Agent instructions
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if instructions_path.exists():
        print("-" * 60)
        print("AGENT INSTRUCTIONS")
        print("-" * 60)
        print(instructions_path.read_text().strip())
        print()


def refresh():
    """Lightweight context refresh — current state with condensed instructions."""
    paused = check_pause("manage")
    if paused:
        print(
            f"Nexus manage is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    today = date.today()

    print("=" * 60)
    print("NEXUS MANAGE REFRESH")
    print("=" * 60)
    print(f"Date: {today.strftime('%A, %B %d, %Y')}")
    print()

    # Last sync info
    last_sync = _get_last_sync_info()
    if last_sync:
        print(f"Last Google Calendar sync: {last_sync}")
    else:
        print("Google Calendar: never synced")
    print()

    # Weather
    _print_weather()

    has_content = _print_actionable_sections()

    # Task tree
    index = load_index()
    if index.tasks:
        print("-" * 60)
        print("ALL ACTIVE TASKS")
        print("-" * 60)
        _print_task_tree()
        print()
        has_content = True

    if not has_content:
        print("Nothing actionable right now.")
        print()

    # Condensed instructions
    print("-" * 60)
    print("REFRESH INSTRUCTIONS")
    print("-" * 60)
    print("Present the information to Benjamin. Priority order:")
    print("  1. Overdue → alert, ask: complete, reschedule, or delete?")
    print("  2. Due today → list what's happening")
    print("  3. Tomorrow / this week → brief summary")
    print("  4. Birthdays → mention so he can prepare")
    print("  5. Open todos → surface if nothing urgent")
    print("  6. Weather → include if available")
    print()
    print("Be direct and informational. Present facts, offer to help if needed.")
    print("Do not create/delete/complete tasks without his input.")
    print("If he asks about his calendar and sync is stale, run: nexus manage sync")
    print()


def upcoming(
    days: int = typer.Option(14, help="Lookahead window in days"),
):
    """Show upcoming tasks, birthdays, and recurring events."""
    today = date.today()

    print(f"Upcoming — {today.strftime('%A, %B %d, %Y')}")
    print()

    has_content = _print_actionable_sections()

    if not has_content:
        print("Nothing upcoming.")
