"""Onboard subcommand — context dump for agents."""

from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import typer

from src.commands.learn.topic import get_week_start
from src.utils.learn import (
    get_active_context,
    get_current_goal,
    get_phase_dir,
    get_records_dir,
)
from src.utils.path_resolution import resolve, resolve_str


def onboard():
    """Print full learning context for the current topic. Designed for agent consumption."""
    ctx = get_active_context()
    if not ctx:
        typer.echo("No active learning context. Run `nexus learn topic update` first.")
        raise typer.Exit(1)

    topic_name, topic_cfg, subtopic_name, subtopic_cfg, phase_name, phase_cfg = ctx

    today = date.today()
    current_week = get_week_start(today)
    week_end = current_week + timedelta(days=6)

    phase_base = f"learn/{topic_name}/{subtopic_name}/{phase_name}"

    print("=" * 60)
    print("NEXUS LEARN ONBOARD")
    print("=" * 60)
    print()
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
    subtopic_info_path = resolve(f"learn/{topic_name}/{subtopic_name}/subtopic_info.md")
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

    # --- Phase status.md ---
    status_path = resolve(f"{phase_base}/status.md")
    if status_path.exists():
        print("-" * 60)
        print(f"PHASE STATUS ({status_path})")
        print("-" * 60)
        print(status_path.read_text().strip())
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
            ref = ""
            if goal.reference:
                phase_dir = get_phase_dir(topic_name, subtopic_name, phase_name)
                ref_abs = (phase_dir / goal.reference).resolve()
                ref = f"\n      ref: {ref_abs}"
            print(f"  {marker} {goal.name}{task_info}{current}{ref}")
        print()

    # --- Current goal detail ---
    current_goal = get_current_goal(phase_cfg)
    if current_goal:
        print("-" * 60)
        print(f"CURRENT GOAL: {current_goal.name}")
        print("-" * 60)
        if current_goal.reference:
            phase_dir = get_phase_dir(topic_name, subtopic_name, phase_name)
            ref_abs = (phase_dir / current_goal.reference).resolve()
            print(f"Reference: {ref_abs}")

        if current_goal.tasks:
            print(
                f"\nTasks ({sum(1 for t in current_goal.tasks if t.status == 'completed')}/{len(current_goal.tasks)} completed):"
            )
            for task in current_goal.tasks:
                marker = "[x]" if task.status == "completed" else "[ ]"
                print(f"  {marker} [{task.type}] {task.name}")
        else:
            print("\nNo tasks yet — create exercises for this goal.")
        print()

    # --- Weekly balance ---
    # Count task types from all goals in this phase (completed this week)
    records_dir = get_records_dir(topic_name, subtopic_name, phase_name)
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
                for line in content.splitlines()[:4]:
                    print(f"    {line}")
                if len(content.splitlines()) > 4:
                    print("    ...")
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
    print(
        f"Practical exercises:  {resolve_str(f'learn/{topic_name}/{subtopic_name}/practical')}/"
    )
    print(f"Theoretical reading:  {resolve_str(f'{phase_base}/theoretical')}/")
    print(f"Quizzes:              {resolve_str(f'{phase_base}/quiz')}/")
    print(f"Records:              {resolve_str(f'{phase_base}/records')}/")
    print()

    # --- Agent instructions (from file) ---
    instructions_path = Path(__file__).parent / "agent_instructions.md"
    if instructions_path.exists():
        print("-" * 60)
        print("AGENT INSTRUCTIONS")
        print("-" * 60)
        print(instructions_path.read_text().strip())
        print()
