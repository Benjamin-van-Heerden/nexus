"""Onboard subcommand — context dump for agents."""

import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import typer

from src.commands.learn.topic import ensure_topic_for_week, get_week_start
from src.utils.learn import (
    get_active_context,
    get_current_goal,
    get_records_dir,
)
from src.utils.path_resolution import resolve, resolve_str
from src.utils.pause import check_pause


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a compact ASCII table for human-facing CLI output."""
    if not rows:
        return

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]
    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    header = "| " + " | ".join(
        headers[i].ljust(widths[i]) for i in range(len(headers))
    ) + " |"

    print(border)
    print(header)
    print(border)
    for row in rows:
        print(
            "| "
            + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers)))
            + " |"
        )
    print(border)


def _section(icon: str, title: str) -> None:
    print(f"{icon} {title}")
    print("-" * 60)


def _status_marker(status: str) -> str:
    return {
        "todo": "⬜ todo",
        "in_progress": "🔄 current",
        "completed": "✅ done",
    }.get(status, status)


def _parse_duration_minutes(duration_str: str) -> int | None:
    """Parse a duration string like '20min', '1h', '1h30min' into minutes."""
    if not duration_str or duration_str == "not recorded":
        return None
    total = 0
    h_match = re.search(r"(\d+)\s*h", duration_str)
    m_match = re.search(r"(\d+)\s*m", duration_str)
    if h_match:
        total += int(h_match.group(1)) * 60
    if m_match:
        total += int(m_match.group(1))
    return total if total > 0 else None


def _parse_record_frontmatter(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter fields from a record file."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fields = {}
    for line in parts[1].strip().splitlines():
        if ": " in line:
            key, val = line.split(": ", 1)
            fields[key.strip()] = val.strip()
    return fields


def _weekly_session_summary(records_dir: Path, week_start: date) -> str | None:
    """Summarize this week's sessions from records for agent decision-making."""
    if not records_dir.exists():
        return None

    week_end = week_start + timedelta(days=6)
    sessions: list[dict[str, str]] = []
    for record_path in sorted(records_dir.glob("*.md")):
        fm = _parse_record_frontmatter(record_path)
        if not fm.get("date"):
            continue
        try:
            record_date = date.fromisoformat(fm["date"])
        except ValueError:
            continue
        if week_start <= record_date <= week_end:
            sessions.append(fm)

    if not sessions:
        return "No sessions logged this week yet."

    total_minutes = 0
    long_sessions = 0
    type_counts: Counter[str] = Counter()
    days_active: set[date] = set()

    for s in sessions:
        minutes = _parse_duration_minutes(s.get("duration", ""))
        if minutes:
            total_minutes += minutes
            if minutes >= 60:
                long_sessions += 1
        t = s.get("type", "")
        if t:
            type_counts[t] += 1
        try:
            days_active.add(date.fromisoformat(s["date"]))
        except (ValueError, KeyError):
            pass

    lines = [
        f"Sessions this week: {len(sessions)} across {len(days_active)} day(s)",
        f"Total time: ~{total_minutes} min",
        f"Long sessions (1h+): {long_sessions}/2 target",
        f"Types: {type_counts.get('practical', 0)} practical, {type_counts.get('theoretical', 0)} theoretical, {type_counts.get('quiz', 0)} quiz",
    ]
    return "\n  ".join(lines)


def onboard():
    """Print full learning context for the current topic. Designed for agent consumption."""
    paused = check_pause("learn")
    if paused:
        typer.echo(
            f"Nexus learn is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    new_topic = ensure_topic_for_week()
    if new_topic:
        typer.echo(f"New week — topic rotated to: {new_topic}\n")

    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context. Run `nexus learn topic update` first.")
        raise typer.Exit(1)

    topic_name, topic_cfg, subtopic_name, subtopic_cfg, phase_name, phase_cfg = ctx

    today = date.today()
    current_week = get_week_start(today)
    week_end = current_week + timedelta(days=6)

    subtopic_base = f"learn/{topic_name}/{subtopic_name}"
    phase_base = f"{subtopic_base}/{phase_name}"

    print("=" * 60)
    print("NEXUS LEARN — DAILY ONBOARD")
    print("=" * 60)
    print()
    print("Nexus is Benjamin's personal structured learning system.")
    print("You are the learning agent. You compose daily exercises,")
    print("track progress, and maintain continuity across sessions.")
    print("The user interacts with you via Telegram. You wake up")
    print("cold each session — this output is your full context.")
    print()
    print(f"DATE: {today.strftime('%A, %B %d, %Y')}")
    print(f"TOPIC: {topic_name}")
    print(f"SUBTOPIC: {subtopic_cfg.name}")
    print(f"PHASE: {phase_cfg.name} [{phase_name}]")
    print(f"WEEK: {current_week.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    print()

    # --- Topic info ---
    topic_info_path = resolve(f"learn/{topic_name}/topic_info.md")
    if topic_info_path.exists():
        print("-" * 60)
        print(f"TOPIC INFO ({topic_info_path})")
        print("-" * 60)
        print(topic_info_path.read_text().strip())
        print()

    # --- Subtopic info ---
    subtopic_info_path = resolve(f"{subtopic_base}/subtopic_info.md")
    if subtopic_info_path.exists():
        print("-" * 60)
        print(f"SUBTOPIC INFO ({subtopic_info_path})")
        print("-" * 60)
        print(subtopic_info_path.read_text().strip())
        print()

    # --- Phase progress ---
    print("-" * 60)
    print("PHASE PROGRESS")
    print("-" * 60)
    for p in subtopic_cfg.phases:
        marker = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[p.status]
        current = " ← current" if p.name == phase_name else ""
        print(f"  {marker} {p.name}{current}")
    print()

    # --- Goals ---
    if phase_cfg.goals:
        print("-" * 60)
        print("GOALS")
        print("-" * 60)
        for goal in phase_cfg.goals:
            marker = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[
                goal.status
            ]
            current = " ← current" if goal.name == phase_cfg.current_goal else ""
            task_count = len(goal.tasks)
            done_count = sum(1 for t in goal.tasks if t.status == "completed")
            task_info = f" ({done_count}/{task_count} tasks)" if task_count else ""
            ref = f"\n      ref: {resolve_str(goal.reference)}"
            print(f"  {marker} {goal.name}{task_info}{current}{ref}")
        print()

    # --- Current goal detail ---
    current_goal = get_current_goal(phase_cfg)
    if current_goal:
        print("-" * 60)
        print(f"CURRENT GOAL: {current_goal.name}")
        print("-" * 60)
        ref_abs = resolve(current_goal.reference)
        print(f"Reference: {ref_abs}")

        if ref_abs.exists():
            print()
            print(ref_abs.read_text().strip())

        if current_goal.tasks:
            print(
                f"\nTasks ({sum(1 for t in current_goal.tasks if t.status == 'completed')}/{len(current_goal.tasks)} completed):"
            )
            for task in current_goal.tasks:
                marker = "[x]" if task.status == "completed" else "[ ]"
                print(f"  {marker} [{task.type}] {task.name}")
                for f in task.relevant_files:
                    print(f"      file: {resolve_str(f)}")
        else:
            print("\nNo tasks yet — create exercises for this goal.")
        print()

    # --- Weekly balance ---
    type_counts = Counter()
    for goal in phase_cfg.goals:
        for task in goal.tasks:
            if task.status == "completed":
                type_counts[task.type] += 1

    print("-" * 60)
    print("EXERCISE BALANCE (this phase)")
    print("-" * 60)
    print(f"  Practical:   {type_counts.get('practical', 0)}")
    print(f"  Theoretical: {type_counts.get('theoretical', 0)}")
    print(f"  Quiz:        {type_counts.get('quiz', 0)}")
    print()
    print("  Default: pair practical with theoretical reading")
    print("  Requirement: at least 1 quiz per week")
    print()

    # --- Weekly session summary ---
    records_dir = get_records_dir(topic_name, subtopic_name)
    weekly_summary = _weekly_session_summary(records_dir, current_week)
    if weekly_summary:
        print("-" * 60)
        print("THIS WEEK'S SESSIONS")
        print("-" * 60)
        print(f"  {weekly_summary}")
        print()

    # --- Last session highlight ---
    if records_dir.exists():
        all_records = sorted(records_dir.glob("*.md"), reverse=True)
        if all_records:
            last_record = all_records[0]
            last_fm = _parse_record_frontmatter(last_record)
            last_content = last_record.read_text().strip()
            # Strip frontmatter for display
            if last_content.startswith("---"):
                parts = last_content.split("---", 2)
                last_body = parts[2].strip() if len(parts) >= 3 else ""
            else:
                last_body = last_content

            print("-" * 60)
            print("LAST SESSION")
            print("-" * 60)
            print(f"  Date: {last_fm.get('date', last_record.stem)}")
            print(f"  Duration: {last_fm.get('duration', 'not recorded')}")
            print(f"  Type: {last_fm.get('type', 'unknown')}")
            print(f"  Status: {last_fm.get('status', 'unknown')}")
            if last_body:
                print()
                for line in last_body.splitlines():
                    print(f"  {line}")
            print()

    # --- Recent records ---
    if records_dir.exists():
        records = sorted(records_dir.glob("*.md"), reverse=True)[:8]
        if records:
            print("-" * 60)
            print(f"RECENT ACTIVITY (last {len(records)} records)")
            print("-" * 60)
            for record_path in records:
                content = record_path.read_text().strip()
                print(f"\n  [{record_path.stem}] ({record_path})")
                for line in content.splitlines():
                    print(f"    {line}")
            print()

    # --- Paths (printed BEFORE exercise instructions so the agent sees them first) ---
    practical_abs = resolve_str(f"{phase_base}/practical")
    theoretical_abs = resolve_str(f"{phase_base}/theoretical")
    quiz_abs = resolve_str(f"{phase_base}/quiz")
    reference_abs = resolve_str(f"learn/{topic_name}/reference")
    records_abs = resolve_str(f"{subtopic_base}/records")

    print("-" * 60)
    print("PATHS (absolute — use these exactly, do NOT use relative paths)")
    print("-" * 60)
    print(f"Phase directory:      {resolve_str(phase_base)}/")
    print(f"Practical exercises:  {practical_abs}/")
    print(f"Theoretical reading:  {theoretical_abs}/")
    print(f"Quizzes:              {quiz_abs}/")
    print(f"Reference:            {reference_abs}/")
    print(f"Records:              {records_abs}/")
    print()
    print("ALL file creation MUST happen inside these directories.")
    print("NEVER create files in your own workspace or any other location.")
    print()

    # --- Exercise type descriptions ---
    if (
        subtopic_cfg.practical.description
        or subtopic_cfg.theoretical.description
        or subtopic_cfg.quiz.description
    ):
        print("-" * 60)
        print("EXERCISE TYPE INSTRUCTIONS")
        print("-" * 60)
        if subtopic_cfg.practical.description:
            print(f"\n  [PRACTICAL] → create files in: {practical_abs}/")
            for line in subtopic_cfg.practical.description.strip().splitlines():
                print(f"    {line.strip()}")
        if subtopic_cfg.theoretical.description:
            print(f"\n  [THEORETICAL] → create files in: {theoretical_abs}/")
            for line in subtopic_cfg.theoretical.description.strip().splitlines():
                print(f"    {line.strip()}")
        if subtopic_cfg.quiz.description:
            print(f"\n  [QUIZ] → create files in: {quiz_abs}/")
            for line in subtopic_cfg.quiz.description.strip().splitlines():
                print(f"    {line.strip()}")
        print()

    # --- Agent instructions (from file) ---
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if instructions_path.exists():
        print("-" * 60)
        print("AGENT INSTRUCTIONS")
        print("-" * 60)
        print(instructions_path.read_text().strip())
        print()

    # --- Action required (last thing the agent sees) ---
    print("=" * 60)
    print("ACTION REQUIRED")
    print("=" * 60)
    print("Follow the wake-up checklist above and send a message to the")
    print("user NOW. Do not silently process this output — the user is")
    print("waiting for your response.")
    print("=" * 60)
    print()


def refresh():
    """Lightweight context refresh — current state with condensed instructions."""
    paused = check_pause("learn")
    if paused:
        typer.echo(
            f"Nexus learn is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    new_topic = ensure_topic_for_week()
    if new_topic:
        typer.echo(f"New week — topic rotated to: {new_topic}\n")

    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context. Run `nexus learn topic update` first.")
        raise typer.Exit(1)

    topic_name, topic_cfg, subtopic_name, subtopic_cfg, phase_name, phase_cfg = ctx

    today = date.today()
    current_week = get_week_start(today)
    week_end = current_week + timedelta(days=6)

    print("=" * 60)
    print("NEXUS LEARN REFRESH")
    print("=" * 60)
    print(f"\nDate: {today.strftime('%A, %B %d, %Y')}")
    print(f"Topic: {topic_name} / {subtopic_cfg.name} / {phase_cfg.name}")
    print(f"Week: {current_week.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    print()

    # Phase progress
    print("-" * 60)
    print("PHASE PROGRESS")
    print("-" * 60)
    for p in subtopic_cfg.phases:
        marker = {"todo": "[ ]", "in_progress": "[~]", "completed": "[x]"}[p.status]
        current = " ← current" if p.name == phase_name else ""
        print(f"  {marker} {p.name}{current}")
    print()

    # Current goal + tasks
    current_goal = get_current_goal(phase_cfg)
    if current_goal:
        done_count = sum(1 for t in current_goal.tasks if t.status == "completed")
        total_count = len(current_goal.tasks)
        print("-" * 60)
        print(f"CURRENT GOAL: {current_goal.name} ({done_count}/{total_count} tasks)")
        print("-" * 60)
        if current_goal.tasks:
            for task in current_goal.tasks:
                marker = "[x]" if task.status == "completed" else "[ ]"
                print(f"  {marker} [{task.type}] {task.name}")
                for f in task.relevant_files:
                    print(f"      file: {resolve_str(f)}")
        else:
            print("  No tasks yet — create exercises for this goal.")
        print()

    # Exercise balance
    type_counts = Counter()
    for goal in phase_cfg.goals:
        for task in goal.tasks:
            if task.status == "completed":
                type_counts[task.type] += 1

    print("-" * 60)
    print("EXERCISE BALANCE (this phase)")
    print("-" * 60)
    print(
        f"  Practical: {type_counts.get('practical', 0)}  |  Theoretical: {type_counts.get('theoretical', 0)}  |  Quiz: {type_counts.get('quiz', 0)}"
    )
    print()

    # Weekly session summary
    records_dir = get_records_dir(topic_name, subtopic_name)
    weekly_summary = _weekly_session_summary(records_dir, current_week)
    if weekly_summary:
        print("-" * 60)
        print("THIS WEEK'S SESSIONS")
        print("-" * 60)
        print(f"  {weekly_summary}")
        print()

    # Last session highlight
    if records_dir.exists():
        all_records = sorted(records_dir.glob("*.md"), reverse=True)
        if all_records:
            last_record = all_records[0]
            last_fm = _parse_record_frontmatter(last_record)
            last_content = last_record.read_text().strip()
            if last_content.startswith("---"):
                parts = last_content.split("---", 2)
                last_body = parts[2].strip() if len(parts) >= 3 else ""
            else:
                last_body = last_content

            print("-" * 60)
            print("LAST SESSION")
            print("-" * 60)
            print(f"  Date: {last_fm.get('date', last_record.stem)}")
            print(f"  Duration: {last_fm.get('duration', 'not recorded')}")
            print(f"  Type: {last_fm.get('type', 'unknown')}")
            print(f"  Status: {last_fm.get('status', 'unknown')}")
            if last_body:
                print()
                for line in last_body.splitlines()[:10]:
                    print(f"  {line}")
            print()

    # Paths
    subtopic_base = f"learn/{topic_name}/{subtopic_name}"
    phase_base = f"{subtopic_base}/{phase_name}"

    print("-" * 60)
    print("PATHS (absolute — use these exactly, do NOT use relative paths)")
    print("-" * 60)
    print(f"  Practical:   {resolve_str(f'{phase_base}/practical')}/")
    print(f"  Theoretical: {resolve_str(f'{phase_base}/theoretical')}/")
    print(f"  Quiz:        {resolve_str(f'{phase_base}/quiz')}/")
    print(f"  Records:     {resolve_str(f'{subtopic_base}/records')}/")
    print()
    print("  ALL files MUST be created inside these directories.")
    print("  NEVER create files in your own workspace or any other location.")
    print()

    # Condensed instructions
    print("-" * 60)
    print("REFRESH INSTRUCTIONS")
    print("-" * 60)
    print()
    print("Hierarchy: topic → subtopic → phase → goal → task")
    print("You manage: task completion, goal completion, phase completion.")
    print()
    print("WAKE-UP CHECKLIST (follow in order, stop at first match):")
    print()
    print("  1. Incomplete tasks from a previous day?")
    print("     → Report them (names + file paths). Stop and wait.")
    print("       Do NOT create new tasks. Do NOT ask what user wants to do.")
    print()
    print("  2. Incomplete tasks from today?")
    print("     → List them. Tell user to report back when done. Stop and wait.")
    print()
    print("  3. No incomplete tasks?")
    print("     → Ask the user TWO questions in a single message:")
    print('       a) "More exercises for this goal, or ready to move on?"')
    print('       b) "How much time do you have today?"')
    print("     → If move on: run `nexus learn goal complete`, then STOP.")
    print("     → If more exercises: compose a session (see agent instructions).")
    print()
    print("  4. All goals in phase completed?")
    print("     → Run `nexus learn phase complete`. Then STOP.")
    print()
    print("STATE MANAGEMENT (non-negotiable):")
    print("  - User completes a task → `nexus learn task complete` IMMEDIATELY")
    print("  - User says move to next goal → `nexus learn goal complete` IMMEDIATELY")
    print("  - All goals done → `nexus learn phase complete` IMMEDIATELY")
    print("  - NEVER skip completion commands. NEVER just talk about moving on")
    print("    without running the command.")
    print()
    print("Commands: task new/complete, goal complete, phase complete, record")
    print()
    print("=" * 60)
    print("ACTION REQUIRED")
    print("=" * 60)
    print("Follow the wake-up checklist above and send a message to the")
    print("user NOW. Do not silently process this output — the user is")
    print("waiting for your response.")
    print("=" * 60)
    print()


def status():
    """Print a human-friendly summary of the current learning state."""
    paused = check_pause("learn")

    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context. Run `nexus learn topic update` first.")
        raise typer.Exit(1)

    topic_name, _topic_cfg, subtopic_name, subtopic_cfg, phase_name, phase_cfg = ctx
    current_goal = get_current_goal(phase_cfg)

    today = date.today()
    current_week = get_week_start(today)
    week_end = current_week + timedelta(days=6)

    print()
    print("🎓 Nexus Learn Status")
    print("=" * 60)
    if paused:
        print(
            f"⏸️  Paused: {paused.reason or 'no reason provided'} "
            f"(resumes {paused.resume_date})"
        )
        print()

    _section("📍", "Current Context")
    _print_table(
        ["Field", "Value"],
        [
            ["Topic", f"📚 {topic_name}"],
            ["Subtopic", f"🧵 {subtopic_cfg.name} ({subtopic_name})"],
            ["Phase", f"🧱 {phase_cfg.name} ({phase_name})"],
            ["Goal", f"🎯 {current_goal.name}" if current_goal else "No current goal"],
            [
                "Week",
                f"🗓️  {current_week.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
            ],
        ],
    )
    print()

    if subtopic_cfg.phases:
        _section("🧭", "Phase Roadmap")
        phase_rows = []
        for phase in subtopic_cfg.phases:
            pointer = "➜" if phase.name == phase_name else ""
            phase_rows.append([pointer, _status_marker(phase.status), phase.name])
        _print_table(["", "Status", "Phase"], phase_rows)
        print()

    if phase_cfg.goals:
        _section("🎯", "Goals In Current Phase")
        goal_rows = []
        for goal in phase_cfg.goals:
            done_count = sum(1 for task in goal.tasks if task.status == "completed")
            total_count = len(goal.tasks)
            pointer = "➜" if goal.name == phase_cfg.current_goal else ""
            goal_rows.append(
                [
                    pointer,
                    _status_marker(goal.status),
                    goal.name,
                    f"{done_count}/{total_count}",
                ]
            )
        _print_table(["", "Status", "Goal", "Tasks"], goal_rows)
        print()

    if not current_goal:
        print("No current goal is set for this phase.")
        print()
        return

    _section("📌", f"Current Goal: {current_goal.name}")
    print(f"Reference: {resolve_str(current_goal.reference)}")
    print()

    if not current_goal.tasks:
        print("📝 No tasks yet for this goal.")
        print()
        return

    _section("📋", "Tasks")
    task_rows = []
    for task in current_goal.tasks:
        completed = task.completed.isoformat() if task.completed else ""
        task_rows.append(
            [
                "✅ done" if task.status == "completed" else "⬜ todo",
                task.type,
                task.name,
                task.created.isoformat(),
                completed,
            ]
        )
    _print_table(["Status", "Type", "Task", "Created", "Completed"], task_rows)
    print()

    _section("📎", "Relevant Files")
    for task in current_goal.tasks:
        marker = "✅" if task.status == "completed" else "⬜"
        print(f"{marker} {task.name}")
        if not task.relevant_files:
            print("  (none)")
            continue
        for file_path in task.relevant_files:
            print(f"  • {resolve_str(file_path)}")
        print()
    print()
