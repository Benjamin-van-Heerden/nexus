"""Topic selection commands.

Manages weekly learning topic rotation using proportional weighting.
"""

import random
from collections import Counter
from datetime import date, timedelta

import typer

from src.models.learn.learn import TopicEntry
from src.models.learn.topic import TopicConfig
from src.utils.learn import load_learn_config, save_learn_config
from src.utils.path_resolution import resolve_str
from src.utils.paths import get_learn_dir

app = typer.Typer()


def get_week_start(d: date) -> date:
    """Get the Monday that starts the week containing the given date."""
    days_since_monday = d.weekday()
    return d - timedelta(days=days_since_monday)


def pick_topic(
    weights: dict[str, int], history: list[TopicEntry]
) -> str:
    """Pick next topic based on proportional weighting within a sliding window.

    Window size is derived from the sum of active weights for perfect resolution.
    History is pre-filtered to active topics only.
    """
    window_size = sum(weights.values())
    recent = history[-window_size:] if history else []
    total_weight = sum(weights.values())
    target_props = {k: v / total_weight for k, v in weights.items()}

    if not recent:
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

    counts = Counter(entry.topic for entry in recent)
    total_recent = len(recent)
    actual_props = {k: counts.get(k, 0) / total_recent for k in weights}

    under = [k for k in weights if actual_props[k] < target_props[k]]

    if not under:
        return random.choice(list(weights.keys()))

    return random.choice(under)


@app.callback(invoke_without_command=True)
def topic(ctx: typer.Context):
    """Show the current week's learning topic."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_learn_config()

    if not config.current_topic:
        typer.echo("No topic selected yet. Run `nexus learn topic update` to pick one.")
        raise typer.Exit(1)

    today = date.today()
    current_week = get_week_start(today)
    week_end = current_week + timedelta(days=6)

    typer.echo(
        f"Week of {current_week.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}: {config.current_topic}"
    )


def ensure_topic_for_week() -> str | None:
    """Ensure a topic is selected for the current week. Returns the topic name if a new one was picked, None if already set."""
    config = load_learn_config()
    today = date.today()
    current_week = get_week_start(today)

    if config.history:
        last = config.history[-1]
        if last.week == current_week:
            return None

    active = config.active_weights()
    if not active:
        return None

    active_names = set(active.keys())
    active_history = [e for e in config.history if e.topic in active_names]

    new_topic = pick_topic(active, active_history)
    config.current_topic = new_topic
    config.history.append(TopicEntry(week=current_week, topic=new_topic))
    save_learn_config(config)
    return new_topic


@app.command()
def update():
    """Select topic for the current week (or confirm existing if already set this week)."""
    result = ensure_topic_for_week()
    if result is None:
        config = load_learn_config()
        typer.echo(f"Topic already set for this week: {config.current_topic}")
        return

    today = date.today()
    current_week = get_week_start(today)
    week_end = current_week + timedelta(days=6)
    typer.echo(
        f"Topic for {current_week.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}: {result}"
    )


@app.command()
def reset():
    """Reset topic selection history."""
    typer.confirm("This will clear all topic selection history. Continue?", abort=True)
    config = load_learn_config()
    config.current_topic = ""
    config.history = []
    save_learn_config(config)
    typer.echo("Topic history has been reset.")


@app.command()
def history():
    """Show topic selection history."""
    config = load_learn_config()

    if not config.history:
        typer.echo("No topic history yet.")
        return

    for entry in config.history:
        week_end = entry.week + timedelta(days=6)
        typer.echo(f"  {entry.week} - {week_end}: {entry.topic}")


@app.command()
def weights():
    """Show current weights and actual vs target proportions."""
    config = load_learn_config()

    active = config.active_weights()
    total_active_weight = sum(active.values())
    active_names = set(active.keys())
    window_size = total_active_weight
    active_history = [e for e in config.history if e.topic in active_names]
    recent = active_history[-window_size:] if active_history else []
    total_recent = len(recent)
    counts = Counter(entry.topic for entry in recent)

    typer.echo(f"Window: {window_size} weeks (derived from active weights sum, {total_recent} selections)\n")
    typer.echo(
        f"{'Topic':<16} {'Weight':<8} {'Active':<8} {'Target':<10} {'Actual':<10} {'Count':<6}"
    )
    typer.echo("-" * 58)

    for tw in sorted(config.topics, key=lambda t: t.name):
        status = "yes" if tw.active else "no"
        if tw.active:
            target = tw.weight / total_active_weight
            actual = counts.get(tw.name, 0) / total_recent if total_recent > 0 else 0.0
            count = counts.get(tw.name, 0)
            marker = " *" if actual < target else ""
            typer.echo(
                f"{tw.name:<16} {tw.weight:<8} {status:<8} {target:<10.1%} {actual:<10.1%} {count:<6}{marker}"
            )
        else:
            typer.echo(
                f"{tw.name:<16} {tw.weight:<8} {status:<8} {'—':<10} {'—':<10} {'—':<6}"
            )

    typer.echo("\n* = under-represented (eligible for selection)")


@app.command()
def new(
    name: str = typer.Argument(help="Topic name (used as directory name, e.g. 'rust')"),
    weight: int = typer.Option(1, help="Weight for topic rotation"),
):
    """Create a new learning topic."""
    learn_dir = get_learn_dir()
    topic_dir = learn_dir / name

    if topic_dir.exists():
        typer.echo(f"Topic '{name}' already exists at {topic_dir}")
        raise typer.Exit(1)

    # Create directory structure
    topic_dir.mkdir(parents=True)
    (topic_dir / "reference").mkdir()

    # Create topic.toml
    import tomli_w

    topic_cfg = TopicConfig(name=name)
    with open(topic_dir / "topic.toml", "wb") as f:
        tomli_w.dump(topic_cfg.model_dump(mode="json"), f, multiline_strings=True)

    # Create topic_info.md
    (topic_dir / "topic_info.md").write_text(
        f"# {name.title()}\n\nDescribe this topic and your background with it.\n"
    )

    # Add topic to learn.toml
    from src.models.learn.learn import TopicWeight

    config = load_learn_config()
    config.topics.append(TopicWeight(name=name, weight=weight))
    save_learn_config(config)

    info_path = resolve_str(f"learn/{name}/topic_info.md")
    ref_path = resolve_str(f"learn/{name}/reference")

    typer.echo(f"Created topic: {resolve_str(f'learn/{name}')}/")
    typer.echo()
    typer.echo("Next steps:")
    typer.echo(f"  1. Fill in the topic info (user background, goals, approach): {info_path}")
    typer.echo(f"  2. Place any reference material (books, docs, guides) in: {ref_path}/")
    typer.echo(f'  3. Create a subtopic (learning track): nexus learn subtopic new "name" --topic {name}')
    typer.echo()
    typer.echo("Discuss with the user what they want to learn, why, and how before proceeding.")


@app.command(name="list")
def list_topics():
    """List all learning topics."""
    config = load_learn_config()
    learn_dir = get_learn_dir()

    if not config.topics:
        typer.echo("No topics configured.")
        return

    for tw in sorted(config.topics, key=lambda t: t.name):
        topic_dir = learn_dir / tw.name
        exists = "✓" if topic_dir.exists() else "✗"
        current = " ← current" if tw.name == config.current_topic else ""
        active = "" if tw.active else " (inactive)"
        typer.echo(f"  [{exists}] {tw.name} (weight: {tw.weight}){active}{current}")


@app.command()
def delete(name: str = typer.Argument(help="Topic name to delete")):
    """Delete a learning topic."""
    import shutil

    learn_dir = get_learn_dir()
    topic_dir = learn_dir / name

    config = load_learn_config()
    topic_names = {t.name for t in config.topics}
    if name not in topic_names:
        typer.echo(f"Topic '{name}' not found.")
        raise typer.Exit(1)

    typer.confirm(
        f"This will delete topic '{name}' and all its contents. Continue?", abort=True
    )

    if topic_dir.exists():
        shutil.rmtree(topic_dir)

    config.topics = [t for t in config.topics if t.name != name]
    if config.current_topic == name:
        config.current_topic = ""
    save_learn_config(config)

    typer.echo(f"Deleted topic: {name}")
