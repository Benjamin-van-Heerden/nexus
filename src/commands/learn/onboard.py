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
    print("  Priority: practical > theoretical > quiz")
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
            print("\n  [PRACTICAL]")
            for line in subtopic_cfg.practical.description.strip().splitlines():
                print(f"    {line.strip()}")
        if subtopic_cfg.theoretical.description:
            print("\n  [THEORETICAL]")
            for line in subtopic_cfg.theoretical.description.strip().splitlines():
                print(f"    {line.strip()}")
        if subtopic_cfg.quiz.description:
            print("\n  [QUIZ]")
            for line in subtopic_cfg.quiz.description.strip().splitlines():
                print(f"    {line.strip()}")
        print()

    # --- Paths ---
    print("-" * 60)
    print("PATHS")
    print("-" * 60)
    print(f"Phase directory:      {resolve_str(phase_base)}/")
    print(f"Practical exercises:  {resolve_str(f'{phase_base}/practical')}/")
    print(f"Theoretical reading:  {resolve_str(f'{phase_base}/theoretical')}/")
    print(f"Quizzes:              {resolve_str(f'{phase_base}/quiz')}/")
    print(f"Reference:            {resolve_str(f'learn/{topic_name}/reference')}/")
    print(f"Records:              {resolve_str(f'{subtopic_base}/records')}/")
    print()

    # --- Agent instructions (from file) ---
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if instructions_path.exists():
        print("-" * 60)
        print("AGENT INSTRUCTIONS")
        print("-" * 60)
        print(instructions_path.read_text().strip())
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

    # Condensed instructions
    print("-" * 60)
    print("REFRESH INSTRUCTIONS")
    print("-" * 60)
    print("Check the state above and proceed:")
    print(
        "  1. Incomplete tasks from last session → ask if completed or needs follow-up"
    )
    print("  2. No incomplete tasks on current goal → compose new exercises")
    print("  3. Reference material exhausted → suggest goal completion (user decides)")
    print("  4. Quiz balance → ensure at least 1 quiz per week")
    print("  5. Session count → suggest short/long based on weekly progress")
    print()
    print("Use `nexus learn task new` to create exercises.")
    print("Use `nexus learn record` to log completed sessions.")
    print()
