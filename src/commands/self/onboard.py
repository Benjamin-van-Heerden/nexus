from datetime import date, timedelta
from pathlib import Path

import typer
from src.utils.self import (
    format_duration,
    get_current_week_start,
    get_days_with_activity,
    get_missing_days_this_week,
    get_sessions_this_week,
    list_active_books,
    load_exercise_log,
    load_habits_config,
    load_learning_log,
    load_math_log,
)

from src.commands.self.math_generator import generate_problems
from src.utils.pause import check_pause


def _section(title: str) -> None:
    typer.echo(f"\n{'=' * 60}")
    typer.echo(f"  {title}")
    typer.echo(f"{'=' * 60}\n")


def onboard() -> None:
    paused = check_pause("self")
    if paused:
        typer.echo(
            f"Nexus self-improvement is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    today = date.today()
    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_of_week = today.weekday()
    iso_week = today.isocalendar()[1]
    days_remaining = 7 - day_of_week

    habits = load_habits_config()

    # SECTION 1 - System Introduction
    _section("SELF-IMPROVEMENT COACH — DAILY BRIEFING")
    typer.echo("You are Benjamin's self-improvement coach. You interact via Telegram.")
    typer.echo("You track 4 habits: reading, exercise, mental math, and learning.")
    typer.echo("Below is your full context for today.\n")

    # SECTION 2 - Date Context
    _section("DATE CONTEXT")
    typer.echo(
        f"Today: {day_names[day_of_week]}, {today.strftime('%B %d, %Y')} (Week {iso_week})"
    )
    typer.echo(f"Day {day_of_week + 1} of 7, {days_remaining} days remaining")

    # SECTION 3 - Reading Status
    if habits.reading.active:
        _section("READING")
        typer.echo(f"Goal: {habits.reading.goal}\n")

        books = list_active_books()
        if not books:
            typer.echo("No active books. Ask the user what they're reading.\n")
        else:
            all_reading_sessions = []
            for book in books:
                all_reading_sessions.extend(book.sessions)

                last_session_date = book.sessions[-1].date if book.sessions else None
                days_since = (
                    (today - last_session_date).days if last_session_date else None
                )
                last_str = (
                    last_session_date.isoformat() if last_session_date else "never"
                )
                days_str = f" ({days_since} days ago)" if days_since is not None else ""

                stale_flag = " ⚠️ STALE" if days_since and days_since > 3 else ""
                typer.echo(f"📖 {book.name} by {book.author}{stale_flag}")
                typer.echo(f"   Last session: {last_str}{days_str}")

                if book.sessions:
                    last = book.sessions[-1]
                    typer.echo(f"   Last read: {last.description}")
                    typer.echo(f"   Last summary: {last.summary[:120]}")
                typer.echo()

            week_reading = get_sessions_this_week(all_reading_sessions)
            reading_days = get_days_with_activity(all_reading_sessions)
            missing = get_missing_days_this_week(all_reading_sessions)
            typer.echo(f"Reading sessions this week: {len(week_reading)}")
            if reading_days:
                typer.echo(
                    f"Active days: {', '.join(day_names[d.weekday()] for d in sorted(reading_days))}"
                )
            if missing:
                typer.echo(f"Missing days: {', '.join(missing)}")

    # SECTION 4 - Exercise Status
    if habits.exercise.active:
        _section("EXERCISE")
        typer.echo(f"Goal: {habits.exercise.goal}\n")

        exercise_log = load_exercise_log()
        week_sessions = get_sessions_this_week(exercise_log.sessions)

        if week_sessions:
            for s in week_sessions:
                typer.echo(
                    f"  [{s.date}] {s.type} — {s.intensity}, {s.duration_minutes} min"
                )
                typer.echo(f"    {s.description[:100]}")
            typer.echo(f"\nSessions this week: {len(week_sessions)}")
        else:
            typer.echo("No sessions this week.")

        missing = get_missing_days_this_week(exercise_log.sessions)
        if missing:
            typer.echo(f"Missing days: {', '.join(missing)}")

    # SECTION 5 - Mental Math
    if habits.mental_math.active:
        _section("MENTAL MATH")
        typer.echo(f"Goal: {habits.mental_math.goal}\n")

        problems, _ = generate_problems()
        typer.echo("Today's mental math problems:")
        typer.echo(problems)
        typer.echo()

        math_log = load_math_log()
        yesterday = today - timedelta(days=1)
        yesterday_sessions = [s for s in math_log.sessions if s.date == yesterday]
        if yesterday_sessions:
            ys = yesterday_sessions[-1]
            typer.echo(
                f"Yesterday: {format_duration(ys.time_seconds)}, {ys.correct}/{ys.total} correct"
            )

        this_week_start = get_current_week_start(today)
        last_week_start = this_week_start - timedelta(days=7)
        this_week = [s for s in math_log.sessions if s.date >= this_week_start]
        last_week = [
            s for s in math_log.sessions if last_week_start <= s.date < this_week_start
        ]

        if this_week:
            avg_this = sum(s.time_seconds for s in this_week) // len(this_week)
            typer.echo(f"This week avg: {format_duration(avg_this)}")
        else:
            typer.echo("No math sessions this week yet.")

        if last_week:
            avg_last = sum(s.time_seconds for s in last_week) // len(last_week)
            typer.echo(f"Last week avg: {format_duration(avg_last)}")
            if this_week:
                avg_this = sum(s.time_seconds for s in this_week) // len(this_week)
                if avg_this < avg_last:
                    typer.echo("Trend: improving ↑")
                elif avg_this > avg_last:
                    typer.echo("Trend: declining ↓")
                else:
                    typer.echo("Trend: stable →")

    # SECTION 6 - Learning Status
    if habits.learning.active:
        _section("LEARNING")
        typer.echo(f"Goal: {habits.learning.goal}\n")

        learning_log = load_learning_log()
        week_sessions = get_sessions_this_week(learning_log.sessions)

        if week_sessions:
            for s in sorted(week_sessions, key=lambda x: x.date):
                status_str = "✓ learned" if s.did_learn else "✗ skipped"
                notes_str = f" — {s.notes[:60]}" if s.notes else ""
                typer.echo(f"  [{s.date}] {status_str}{notes_str}")
        else:
            typer.echo("No check-ins this week.")

        learned_dates = sorted(
            {s.date for s in learning_log.sessions if s.did_learn}, reverse=True
        )
        streak = 0
        check = today if today in learned_dates else today - timedelta(days=1)
        if check in learned_dates:
            for d in learned_dates:
                if d == check - timedelta(days=streak):
                    streak += 1
                else:
                    break
        typer.echo(f"\nStreak: {streak} day(s)")

        missing = get_missing_days_this_week(learning_log.sessions)
        if missing:
            typer.echo(f"Missing days: {', '.join(missing)}")

    # SECTION 7 - Weekly Overview
    _section("WEEKLY OVERVIEW")

    def _status_emoji(count: int, target: int) -> str:
        if count == 0:
            return "⬜ not started"
        elif count >= target:
            return "✅ on track"
        else:
            return "🟡 behind"

    exercise_log = load_exercise_log()
    learning_log = load_learning_log()
    books = list_active_books()
    all_reading = []
    for b in books:
        all_reading.extend(b.sessions)

    reading_count = len(get_sessions_this_week(all_reading))
    exercise_count = len(get_sessions_this_week(exercise_log.sessions))
    math_count = len(get_sessions_this_week(load_math_log().sessions))
    learning_count = len(get_sessions_this_week(learning_log.sessions))

    typer.echo(
        f"  Reading:    {reading_count} sessions  {_status_emoji(reading_count, 5)}"
    )
    typer.echo(
        f"  Exercise:   {exercise_count} sessions  {_status_emoji(exercise_count, 4)}"
    )
    typer.echo(
        f"  Math:       {math_count} sessions  {_status_emoji(math_count, day_of_week + 1)}"
    )
    typer.echo(
        f"  Learning:   {learning_count} sessions  {_status_emoji(learning_count, day_of_week + 1)}"
    )

    # SECTION 8 - Agent Instructions
    _section("AGENT INSTRUCTIONS")
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if instructions_path.exists():
        typer.echo(instructions_path.read_text())
    else:
        typer.echo("WARNING: agent_instructions.md not found!")

    typer.echo("=" * 60)
    typer.echo("ACTION REQUIRED")
    typer.echo("=" * 60)
    typer.echo("Read the instructions above and send a message to the user")
    typer.echo("NOW. Do not silently process this output — the user is")
    typer.echo("waiting for your response.")
    typer.echo("=" * 60)
    typer.echo()


def refresh() -> None:
    """Lightweight context refresh — current state with condensed instructions."""
    paused = check_pause("self")
    if paused:
        typer.echo(
            f"Nexus self-improvement is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    today = date.today()
    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_of_week = today.weekday()
    iso_week = today.isocalendar()[1]
    days_remaining = 7 - day_of_week

    habits = load_habits_config()

    typer.echo("=" * 60)
    typer.echo("  SELF-IMPROVEMENT REFRESH")
    typer.echo("=" * 60)
    typer.echo(
        f"\nToday: {day_names[day_of_week]}, {today.strftime('%B %d, %Y')} (Week {iso_week})"
    )
    typer.echo(f"Day {day_of_week + 1} of 7, {days_remaining} days remaining\n")

    # Reading status
    if habits.reading.active:
        typer.echo("-" * 60)
        typer.echo("READING")
        typer.echo("-" * 60)
        books = list_active_books()
        all_reading_sessions = []
        if not books:
            typer.echo("  No active books.\n")
        else:
            for book in books:
                all_reading_sessions.extend(book.sessions)
                last_session_date = book.sessions[-1].date if book.sessions else None
                days_since = (
                    (today - last_session_date).days if last_session_date else None
                )
                stale_flag = " ⚠️ STALE" if days_since and days_since > 3 else ""
                last_read = f" — {book.sessions[-1].description}" if book.sessions else ""
                typer.echo(f"  📖 {book.name}{last_read}{stale_flag}")

            week_reading = get_sessions_this_week(all_reading_sessions)
            reading_days = get_days_with_activity(all_reading_sessions)
            missing = get_missing_days_this_week(all_reading_sessions)
            typer.echo(f"  Sessions this week: {len(week_reading)}")
            if reading_days:
                typer.echo(
                    f"  Active days: {', '.join(day_names[d.weekday()] for d in sorted(reading_days))}"
                )
            if missing:
                typer.echo(f"  Missing days: {', '.join(missing)}")
        typer.echo()

    # Exercise status
    if habits.exercise.active:
        typer.echo("-" * 60)
        typer.echo("EXERCISE")
        typer.echo("-" * 60)
        exercise_log = load_exercise_log()
        week_sessions = get_sessions_this_week(exercise_log.sessions)
        if week_sessions:
            for s in week_sessions:
                typer.echo(
                    f"  [{s.date}] {s.type} — {s.intensity}, {s.duration_minutes} min"
                )
            typer.echo(f"  Sessions this week: {len(week_sessions)}")
        else:
            typer.echo("  No sessions this week.")
        missing = get_missing_days_this_week(exercise_log.sessions)
        if missing:
            typer.echo(f"  Missing days: {', '.join(missing)}")
        typer.echo()

    # Mental math status
    if habits.mental_math.active:
        typer.echo("-" * 60)
        typer.echo("MENTAL MATH")
        typer.echo("-" * 60)
        math_log = load_math_log()
        this_week_start = get_current_week_start(today)
        this_week = [s for s in math_log.sessions if s.date >= this_week_start]
        if this_week:
            avg_time = sum(s.time_seconds for s in this_week) // len(this_week)
            typer.echo(
                f"  Sessions this week: {len(this_week)}, avg: {format_duration(avg_time)}"
            )
        else:
            typer.echo("  No sessions this week.")
        typer.echo()

    # Learning status
    if habits.learning.active:
        typer.echo("-" * 60)
        typer.echo("LEARNING")
        typer.echo("-" * 60)
        learning_log = load_learning_log()
        week_sessions = get_sessions_this_week(learning_log.sessions)
        if week_sessions:
            for s in sorted(week_sessions, key=lambda x: x.date):
                status_str = "✓ learned" if s.did_learn else "✗ skipped"
                notes_str = f" — {s.notes[:60]}" if s.notes else ""
                typer.echo(f"  [{s.date}] {status_str}{notes_str}")
        else:
            typer.echo("  No check-ins this week.")

        learned_dates = sorted(
            {s.date for s in learning_log.sessions if s.did_learn}, reverse=True
        )
        streak = 0
        check = today if today in learned_dates else today - timedelta(days=1)
        if check in learned_dates:
            for d in learned_dates:
                if d == check - timedelta(days=streak):
                    streak += 1
                else:
                    break
        typer.echo(f"  Streak: {streak} day(s)")
        typer.echo()

    # Weekly overview
    typer.echo("-" * 60)
    typer.echo("WEEKLY OVERVIEW")
    typer.echo("-" * 60)

    def _status_emoji(count: int, target: int) -> str:
        if count == 0:
            return "⬜ not started"
        elif count >= target:
            return "✅ on track"
        else:
            return "🟡 behind"

    exercise_log = load_exercise_log()
    learning_log = load_learning_log()
    books = list_active_books()
    all_reading = []
    for b in books:
        all_reading.extend(b.sessions)

    reading_count = len(get_sessions_this_week(all_reading))
    exercise_count = len(get_sessions_this_week(exercise_log.sessions))
    math_count = len(get_sessions_this_week(load_math_log().sessions))
    learning_count = len(get_sessions_this_week(learning_log.sessions))

    typer.echo(
        f"  Reading:    {reading_count} sessions  {_status_emoji(reading_count, 5)}"
    )
    typer.echo(
        f"  Exercise:   {exercise_count} sessions  {_status_emoji(exercise_count, 4)}"
    )
    typer.echo(
        f"  Math:       {math_count} sessions  {_status_emoji(math_count, day_of_week + 1)}"
    )
    typer.echo(
        f"  Learning:   {learning_count} sessions  {_status_emoji(learning_count, day_of_week + 1)}"
    )
    typer.echo()

    # Condensed instructions
    typer.echo("-" * 60)
    typer.echo("REFRESH INSTRUCTIONS")
    typer.echo("-" * 60)
    typer.echo("Report the above to Benjamin. Priority order:")
    typer.echo("  1. Stale books (>3 days) → nudge him to read")
    typer.echo("  2. Behind habits → remind and encourage")
    typer.echo("  3. Math problems → generate fresh set if not done today")
    typer.echo("  4. Learning streak → highlight if active, motivate if broken")
    typer.echo("  5. On-track items → brief acknowledgement")
    typer.echo()
    typer.echo("When he reports back:")
    typer.echo("  - Exercise/math/learning → log immediately, confirm briefly, stop")
    typer.echo(
        "  - Reading → research the section, provide recap, discuss, THEN log"
    )
    typer.echo("  - Backdated reports → use --date YYYY-MM-DD flag")
    typer.echo()
    typer.echo("=" * 60)
    typer.echo("ACTION REQUIRED")
    typer.echo("=" * 60)
    typer.echo("Report the above to Benjamin NOW. Do not silently process")
    typer.echo("this output — the user is waiting for your response.")
    typer.echo("=" * 60)
    typer.echo()
