"""Subtopic subcommand — CRUD for subtopics within a topic."""

import shutil

import tomli_w
import typer

from src.models.learn.subtopic import ExerciseTypeConfig, SubtopicConfig
from src.models.learn.topic import TopicConfig
from src.utils.learn import (
    get_subtopic_dir,
    get_topic_dir,
    load_learn_config,
    load_topic_config,
)
from src.utils.paths import get_learn_dir
from src.utils.path_resolution import resolve_str

app = typer.Typer()

SUBTOPIC_INFO_TEMPLATE = """\
# {name}

## What are we learning?
<!-- Describe the subject matter and scope. What specific area does this cover? -->

## Why are we learning this?
<!-- Motivation: what will this enable? Why is it worth the time? -->

## How will we learn?
<!-- Approach and methodology. What resources will we use? How will we structure
the learning — reading, exercises, projects? -->

## Proposed Phases
<!-- List the phases you plan to work through. These will be created with
`nexus learn phase new "name"` once the plan is agreed on. -->

1. ...
2. ...
3. ...

## Resources
<!-- Links, books, repos, documentation, courses, etc. -->

"""


@app.command()
def new(
    name: str = typer.Argument(help="Subtopic name (used as directory name)"),
    topic: str = typer.Option("", help="Topic to create under (defaults to current topic)"),
):
    """Create a new subtopic. Generates a subtopic_info.md to kick off planning."""
    config = load_learn_config()
    topic_name = topic or config.current_topic
    if not topic_name:
        typer.echo("No topic specified and no current topic set.")
        raise typer.Exit(1)

    topic_dir = get_topic_dir(topic_name)
    if not topic_dir.exists():
        typer.echo(f"Topic '{topic_name}' does not exist.")
        raise typer.Exit(1)

    subtopic_dir = topic_dir / name
    if subtopic_dir.exists():
        typer.echo(f"Subtopic '{name}' already exists at {subtopic_dir}")
        raise typer.Exit(1)

    # Create directory structure
    subtopic_dir.mkdir(parents=True)
    (subtopic_dir / "practical").mkdir()
    (subtopic_dir / "theoretical").mkdir()
    (subtopic_dir / "quiz").mkdir()

    # Create subtopic.toml
    subtopic_cfg = SubtopicConfig(
        name=name,
        practical=ExerciseTypeConfig(description="Describe how practical exercises work for this subtopic."),
        theoretical=ExerciseTypeConfig(description="Describe how theoretical reading works for this subtopic."),
        quiz=ExerciseTypeConfig(description="Describe how quizzes work for this subtopic."),
    )
    with open(subtopic_dir / "subtopic.toml", "wb") as f:
        tomli_w.dump(subtopic_cfg.model_dump(mode="json"), f)

    # Create subtopic_info.md with deliberation template
    (subtopic_dir / "subtopic_info.md").write_text(SUBTOPIC_INFO_TEMPLATE.format(name=name))

    info_path = resolve_str(f"learn/{topic_name}/{name}/subtopic_info.md")
    toml_path = resolve_str(f"learn/{topic_name}/{name}/subtopic.toml")

    typer.echo(f"Created subtopic: {resolve_str(f'learn/{topic_name}/{name}')}/")
    typer.echo()
    typer.echo("Next steps:")
    typer.echo(f"  1. Review and fill in the learning plan: {info_path}")
    typer.echo(f"  2. Update exercise type descriptions in: {toml_path}")
    typer.echo(f"  3. Create phases with: nexus learn phase new \"phase-name\"")
    typer.echo(f"  4. Set as active: nexus learn subtopic set \"{name}\"")
    typer.echo()
    typer.echo("Take time to deliberate on what and how you want to learn before proceeding.")


@app.command(name="set")
def set_subtopic(
    name: str = typer.Argument(help="Subtopic name to set as current"),
    topic: str = typer.Option("", help="Topic (defaults to current topic)"),
):
    """Set the active subtopic for a topic."""
    config = load_learn_config()
    topic_name = topic or config.current_topic
    if not topic_name:
        typer.echo("No topic specified and no current topic set.")
        raise typer.Exit(1)

    subtopic_dir = get_subtopic_dir(topic_name, name)
    if not subtopic_dir.exists():
        typer.echo(f"Subtopic '{name}' does not exist under {topic_name}/")
        raise typer.Exit(1)

    # Update topic.toml
    topic_cfg = load_topic_config(topic_name)
    topic_cfg.current_subtopic = name
    with open(get_topic_dir(topic_name) / "topic.toml", "wb") as f:
        tomli_w.dump(topic_cfg.model_dump(mode="json"), f)

    typer.echo(f"Active subtopic set to: {name}")


@app.command(name="list")
def list_subtopics(
    topic: str = typer.Option("", help="Topic (defaults to current topic)"),
):
    """List all subtopics under a topic."""
    config = load_learn_config()
    topic_name = topic or config.current_topic
    if not topic_name:
        typer.echo("No topic specified and no current topic set.")
        raise typer.Exit(1)

    topic_dir = get_topic_dir(topic_name)
    if not topic_dir.exists():
        typer.echo(f"Topic '{topic_name}' does not exist.")
        raise typer.Exit(1)

    topic_cfg = load_topic_config(topic_name)

    subtopics = [
        d.name for d in topic_dir.iterdir()
        if d.is_dir() and (d / "subtopic.toml").exists()
    ]

    if not subtopics:
        typer.echo(f"No subtopics under {topic_name}/")
        return

    for name in sorted(subtopics):
        current = " ← current" if name == topic_cfg.current_subtopic else ""
        typer.echo(f"  {name}{current}")


@app.command()
def delete(
    name: str = typer.Argument(help="Subtopic name to delete"),
    topic: str = typer.Option("", help="Topic (defaults to current topic)"),
):
    """Delete a subtopic and all its contents."""
    config = load_learn_config()
    topic_name = topic or config.current_topic
    if not topic_name:
        typer.echo("No topic specified and no current topic set.")
        raise typer.Exit(1)

    subtopic_dir = get_subtopic_dir(topic_name, name)
    if not subtopic_dir.exists():
        typer.echo(f"Subtopic '{name}' does not exist under {topic_name}/")
        raise typer.Exit(1)

    typer.confirm(f"This will delete subtopic '{name}' and all its contents. Continue?", abort=True)

    shutil.rmtree(subtopic_dir)

    # Clear current_subtopic if it was the deleted one
    topic_cfg = load_topic_config(topic_name)
    if topic_cfg.current_subtopic == name:
        topic_cfg.current_subtopic = ""
        with open(get_topic_dir(topic_name) / "topic.toml", "wb") as f:
            tomli_w.dump(topic_cfg.model_dump(mode="json"), f)

    typer.echo(f"Deleted subtopic: {name}")
