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
    """Get the Sunday that starts the week containing the given date."""
    days_since_sunday = d.isoweekday() % 7
    return d - timedelta(days=days_since_sunday)


def pick_topic(
    weights: dict[str, int], history: list[TopicEntry], window_size: int
) -> str:
    """Pick next topic based on proportional weighting within a sliding window."""
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


@app.command()
def update():
    """Select topic for the current week (or confirm existing if already set this week)."""
    config = load_learn_config()
    today = date.today()
    current_week = get_week_start(today)

    # Check if we already have a selection for this week
    if config.history:
        last = config.history[-1]
        if last.week == current_week:
            typer.echo(f"Topic already set for this week: {last.topic}")
            return

    new_topic = pick_topic(config.weights, config.history, config.window_size)
    config.current_topic = new_topic
    config.history.append(TopicEntry(week=current_week, topic=new_topic))
    save_learn_config(config)

    week_end = current_week + timedelta(days=6)
    typer.echo(
        f"Topic for {current_week.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}: {new_topic}"
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

    total_weight = sum(config.weights.values())
    recent = config.history[-config.window_size :] if config.history else []
    total_recent = len(recent)
    counts = Counter(entry.topic for entry in recent)

    typer.echo(f"Window: last {config.window_size} weeks ({total_recent} selections)\n")
    typer.echo(
        f"{'Topic':<12} {'Weight':<8} {'Target':<10} {'Actual':<10} {'Count':<6}"
    )
    typer.echo("-" * 46)

    for topic_name, weight in sorted(config.weights.items()):
        target = weight / total_weight
        actual = counts.get(topic_name, 0) / total_recent if total_recent > 0 else 0.0
        count = counts.get(topic_name, 0)
        marker = " *" if actual < target else ""
        typer.echo(
            f"{topic_name:<12} {weight:<8} {target:<10.1%} {actual:<10.1%} {count:<6}{marker}"
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

    # Create topic.toml
    import tomli_w

    topic_cfg = TopicConfig(name=name)
    with open(topic_dir / "topic.toml", "wb") as f:
        tomli_w.dump(topic_cfg.model_dump(mode="json"), f)

    # Create topic_info.md
    (topic_dir / "topic_info.md").write_text(
        f"# {name.title()}\n\nDescribe this topic and your background with it.\n"
    )

    # Add weight to learn.toml
    config = load_learn_config()
    config.weights[name] = weight
    save_learn_config(config)

    typer.echo(f"Created topic: {resolve_str(f'learn/{name}')}/")
    typer.echo(f"Edit topic info: {resolve_str(f'learn/{name}/topic_info.md')}")
    typer.echo('Next: create a subtopic with `nexus learn subtopic new "name"`')


@app.command(name="list")
def list_topics():
    """List all learning topics."""
    config = load_learn_config()
    learn_dir = get_learn_dir()

    if not config.weights:
        typer.echo("No topics configured.")
        return

    for name, weight in sorted(config.weights.items()):
        topic_dir = learn_dir / name
        exists = "✓" if topic_dir.exists() else "✗"
        current = " ← current" if name == config.current_topic else ""
        typer.echo(f"  [{exists}] {name} (weight: {weight}){current}")


@app.command()
def delete(name: str = typer.Argument(help="Topic name to delete")):
    """Delete a learning topic."""
    import shutil

    learn_dir = get_learn_dir()
    topic_dir = learn_dir / name

    config = load_learn_config()
    if name not in config.weights:
        typer.echo(f"Topic '{name}' not found in weights.")
        raise typer.Exit(1)

    typer.confirm(
        f"This will delete topic '{name}' and all its contents. Continue?", abort=True
    )

    if topic_dir.exists():
        shutil.rmtree(topic_dir)

    del config.weights[name]
    if config.current_topic == name:
        config.current_topic = ""
    save_learn_config(config)

    typer.echo(f"Deleted topic: {name}")
