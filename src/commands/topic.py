"""Topic selection commands.

Manages weekly learning topic rotation using proportional weighting.
Topics that are under-represented relative to their weight get priority.
Uses a sliding window so weight changes take effect naturally.
"""

import random
from collections import Counter
from datetime import date, timedelta

import typer

from src.utils.config import load_config
from src.utils.state import TopicEntry, load_state, save_state

app = typer.Typer()


def get_week_start(d: date) -> date:
    """Get the Sunday that starts the week containing the given date."""
    days_since_sunday = d.isoweekday() % 7
    return d - timedelta(days=days_since_sunday)


def pick_topic(weights: dict[str, int], history: list[TopicEntry], window_size: int) -> str:
    """Pick next topic based on proportional weighting.

    Compares actual selection frequency (within the sliding window)
    against target proportions from weights. Picks randomly from
    under-represented topics. If all topics are at or above target,
    picks randomly from all.
    """
    recent = history[-window_size:] if history else []
    total_weight = sum(weights.values())
    target_props = {k: v / total_weight for k, v in weights.items()}

    if not recent:
        # No history — weighted random pick
        topics = list(weights.keys())
        cumulative = []
        running = 0.0
        for t in topics:
            running += target_props[t]
            cumulative.append(running)
        r = random.random()
        for i, c in enumerate(cumulative):
            if r <= c:
                return topics[i]
        return topics[-1]

    # Count recent selections
    counts = Counter(entry.topic for entry in recent)
    total_recent = len(recent)
    actual_props = {k: counts.get(k, 0) / total_recent for k in weights}

    # Find under-represented topics
    under = [k for k in weights if actual_props[k] < target_props[k]]

    if not under:
        return random.choice(list(weights.keys()))

    return random.choice(under)


@app.callback(invoke_without_command=True)
def topic(ctx: typer.Context):
    """Show or pick the current week's learning topic."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    state = load_state()

    today = date.today()
    current_week = get_week_start(today)

    # Check if we need to pick a new topic
    if state.learn.current_week is None or current_week > state.learn.current_week:
        new_topic = pick_topic(
            config.learn.weights,
            state.learn.history,
            config.learn.window_size,
        )
        state.learn.current_topic = new_topic
        state.learn.current_week = current_week
        state.learn.history.append(TopicEntry(week=current_week, topic=new_topic))
        save_state(state)

    week_end = current_week + timedelta(days=6)
    week_start_fmt = current_week.strftime("%B %d")
    week_end_fmt = week_end.strftime("%B %d, %Y")

    typer.echo(f"Week of {week_start_fmt} - {week_end_fmt}: {state.learn.current_topic}")


@app.command()
def reset():
    """Reset topic selection history."""
    typer.confirm("This will clear all topic selection history. Continue?", abort=True)
    state = load_state()
    state.learn.current_topic = ""
    state.learn.current_week = None
    state.learn.history = []
    save_state(state)
    typer.echo("Topic history has been reset.")


@app.command()
def history():
    """Show topic selection history."""
    state = load_state()

    if not state.learn.history:
        typer.echo("No topic history yet.")
        return

    for entry in state.learn.history:
        week_end = entry.week + timedelta(days=6)
        typer.echo(f"  {entry.week} - {week_end}: {entry.topic}")


@app.command()
def weights():
    """Show current weights and actual vs target proportions."""
    config = load_config()
    state = load_state()

    total_weight = sum(config.learn.weights.values())
    recent = state.learn.history[-config.learn.window_size:] if state.learn.history else []
    total_recent = len(recent)
    counts = Counter(entry.topic for entry in recent)

    typer.echo(f"Window: last {config.learn.window_size} weeks ({total_recent} selections)\n")
    typer.echo(f"{'Topic':<12} {'Weight':<8} {'Target':<10} {'Actual':<10} {'Count':<6}")
    typer.echo("-" * 46)

    for topic_name, weight in sorted(config.learn.weights.items()):
        target = weight / total_weight
        actual = counts.get(topic_name, 0) / total_recent if total_recent > 0 else 0.0
        count = counts.get(topic_name, 0)
        marker = " *" if actual < target else ""
        typer.echo(
            f"{topic_name:<12} {weight:<8} {target:<10.1%} {actual:<10.1%} {count:<6}{marker}"
        )

    typer.echo("\n* = under-represented (eligible for selection)")
