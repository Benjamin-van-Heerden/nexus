"""Tracked-story commands for the news system.

Tracked stories are free-text topics the user wants the digest to follow over
time. The synthesis LLM matches incoming clusters against their descriptions
during onboard and appends developments.
"""

from datetime import date

import typer

from src.utils.news import (
    get_story_path,
    list_tracked_stories,
    load_tracked_story,
    save_tracked_story,
    slugify,
)
from src.models.news.story import TrackedStory


def _derive_slug(description: str, max_words: int = 6) -> str:
    words = description.strip().split()
    head = " ".join(words[:max_words])
    return slugify(head)


def track(
    description: str = typer.Argument(
        help="Free-text description of the story to follow"
    ),
    slug: str = typer.Option(
        "", help="Optional explicit slug (auto-derived from description if omitted)"
    ),
):
    """Start following a story. The LLM matches future clusters against the description."""
    description = description.strip()
    if not description:
        typer.echo("Description cannot be empty.")
        raise typer.Exit(1)

    final_slug = slugify(slug) if slug else _derive_slug(description)
    if not final_slug:
        typer.echo("Could not derive a slug from the description. Pass --slug.")
        raise typer.Exit(1)

    if get_story_path(final_slug).exists():
        typer.echo(f"Tracked story already exists: {final_slug}")
        typer.echo("Use 'nexus news stories' to view, or pick a different --slug.")
        raise typer.Exit(1)

    story = TrackedStory(
        slug=final_slug,
        description=description,
        created=date.today(),
    )
    save_tracked_story(story)

    typer.echo(f"Tracking: {final_slug}")
    typer.echo(f"  {description}")


def untrack(slug: str = typer.Argument(help="Slug of the story to deactivate")):
    """Deactivate a tracked story. History is preserved."""
    slug = slugify(slug)
    if not get_story_path(slug).exists():
        typer.echo(f"No tracked story with slug: {slug}")
        raise typer.Exit(1)

    story = load_tracked_story(slug)
    if not story.active:
        typer.echo(f"Already inactive: {slug}")
        return

    story.active = False
    save_tracked_story(story)
    typer.echo(f"Untracked: {slug}")


def stories():
    """List all tracked stories (active and inactive)."""
    all_stories = list_tracked_stories(active_only=False)
    if not all_stories:
        typer.echo("No tracked stories.")
        return

    active = [s for s in all_stories if s.active]
    inactive = [s for s in all_stories if not s.active]

    def _print(s: TrackedStory) -> None:
        last = s.last_updated.isoformat() if s.last_updated else "never"
        typer.echo(f"  {s.slug}")
        typer.echo(f"    description: {s.description}")
        typer.echo(
            f"    created: {s.created.isoformat()}  "
            f"last_updated: {last}  "
            f"developments: {len(s.developments)}"
        )

    if active:
        typer.echo(f"Active ({len(active)}):")
        for s in active:
            _print(s)

    if inactive:
        if active:
            typer.echo("")
        typer.echo(f"Inactive ({len(inactive)}):")
        for s in inactive:
            _print(s)
