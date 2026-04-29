"""Topic CRUD commands and member auto-sync.

Provides the `nexus archive topic` sub-app (new, update, delete, show) and
the `nexus archive topics` listing command (registered separately at the
archive top level).
"""

import json as json_lib
from datetime import date, datetime, timezone

import typer

from src.models.archive.topic import TopicConfig
from src.models.archive.work import WorkItem
from src.utils.archive import (
    enqueue_work,
    get_topic_path,
    get_wiki_dir,
    is_valid_slug,
    list_all_topics,
    load_doc,
    load_topic,
    regenerate_index,
    save_doc,
    save_topic,
    topic_exists,
)
from src.utils.paths import get_archive_dir

app = typer.Typer(help="Manage archive topics")


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo(
            "Archive directory does not exist. Run `nexus archive setup` first."
        )
        raise typer.Exit(1)


def _parse_related(related: str | None) -> list[str]:
    if not related:
        return []
    parts = [s.strip() for s in related.split(",")]
    return [p for p in parts if p]


def _validate_topic_refs(
    parent: str | None,
    related: list[str],
    self_slug: str,
) -> None:
    if parent is not None:
        if parent == self_slug:
            typer.echo(f"Error: parent cannot be the same as the topic slug ('{self_slug}').")
            raise typer.Exit(1)
        if not topic_exists(parent):
            typer.echo(f"Error: parent topic '{parent}' does not exist.")
            raise typer.Exit(1)

    seen = set()
    for r in related:
        if r == self_slug:
            typer.echo(f"Error: related cannot include the topic itself ('{self_slug}').")
            raise typer.Exit(1)
        if r in seen:
            typer.echo(f"Error: related contains duplicate '{r}'.")
            raise typer.Exit(1)
        seen.add(r)
        if not topic_exists(r):
            typer.echo(f"Error: related topic '{r}' does not exist.")
            raise typer.Exit(1)


@app.command("new")
def new(
    slug: str = typer.Argument(..., help="Topic slug (kebab-case, e.g. ml-architectures)"),
    title: str = typer.Option(..., "--title", "-t", help="Human-readable title"),
    summary: str = typer.Option(..., "--summary", "-s", help="Summary (2-3 sentences)"),
    parent: str | None = typer.Option(None, "--parent", "-p", help="Parent topic slug"),
    related: str | None = typer.Option(
        None, "--related", "-r", help="Comma-separated related topic slugs"
    ),
):
    """Create a new topic."""
    _ensure_archive_initialized()

    if not is_valid_slug(slug):
        typer.echo(f"Error: '{slug}' is not a valid kebab-case slug.")
        raise typer.Exit(1)

    if topic_exists(slug):
        typer.echo(f"Error: topic '{slug}' already exists.")
        raise typer.Exit(1)

    related_list = _parse_related(related)
    _validate_topic_refs(parent, related_list, slug)

    today = date.today()
    topic = TopicConfig(
        slug=slug,
        title=title,
        summary=summary,
        parent=parent,
        related=related_list,
        created=today,
        updated=today,
        last_maintained=today,
        docs=[],
    )
    save_topic(topic)
    regenerate_index()

    typer.echo(f"Created topic '{slug}'.")
    typer.echo(f"  Path: {get_topic_path(slug)}")
    typer.echo()
    typer.echo("ACTION REQUIRED:")
    typer.echo(
        "  Add docs by including this slug in their `topics:` frontmatter when "
        "running `nexus archive write` or `nexus archive doc update`."
    )


@app.command("update")
def update(
    slug: str = typer.Argument(..., help="Topic slug to update"),
    title: str | None = typer.Option(None, "--title", "-t"),
    summary: str | None = typer.Option(None, "--summary", "-s"),
    parent: str | None = typer.Option(
        None, "--parent", "-p", help="New parent slug (use empty string to clear)"
    ),
    related: str | None = typer.Option(
        None, "--related", "-r", help="Comma-separated related topic slugs (replaces existing)"
    ),
):
    """Update fields on an existing topic. Prints a before/after diff for changes."""
    _ensure_archive_initialized()

    if not topic_exists(slug):
        typer.echo(f"Error: topic '{slug}' does not exist.")
        raise typer.Exit(1)

    topic = load_topic(slug)
    changes: list[tuple[str, object, object]] = []

    if title is not None and title != topic.title:
        changes.append(("title", topic.title, title))
        topic.title = title

    if summary is not None and summary != topic.summary:
        changes.append(("summary", topic.summary, summary))
        topic.summary = summary

    if parent is not None:
        new_parent = parent if parent != "" else None
        if new_parent != topic.parent:
            if new_parent is not None:
                _validate_topic_refs(new_parent, [], slug)
            changes.append(("parent", topic.parent, new_parent))
            topic.parent = new_parent

    if related is not None:
        new_related = _parse_related(related)
        _validate_topic_refs(topic.parent, new_related, slug)
        if new_related != topic.related:
            changes.append(("related", topic.related, new_related))
            topic.related = new_related

    if not changes:
        typer.echo(f"No changes — topic '{slug}' is already in the requested state.")
        return

    topic.updated = date.today()
    save_topic(topic)
    regenerate_index()

    typer.echo(f"Updated topic '{slug}':")
    for field, old, new in changes:
        typer.echo(f"  {field}:")
        typer.echo(f"    before: {old!r}")
        typer.echo(f"    after:  {new!r}")


@app.command("delete")
def delete(
    slug: str = typer.Argument(..., help="Topic slug to delete"),
):
    """Delete a topic. Affected docs get a `needs_topic_review` work item.

    Walks every doc, removes this topic from `topics:` lists, enqueues
    review items. Reference integrity is preserved — no silent data loss.
    """
    _ensure_archive_initialized()

    if not topic_exists(slug):
        typer.echo(f"Error: topic '{slug}' does not exist.")
        raise typer.Exit(1)

    affected_docs: list[str] = []
    wiki_dir = get_wiki_dir()
    if wiki_dir.is_dir():
        for path in sorted(wiki_dir.glob("*.md")):
            try:
                fm, body = load_doc(path.stem)
            except Exception:
                continue
            if slug in fm.topics:
                fm.topics = [t for t in fm.topics if t != slug]
                save_doc(fm, body)
                affected_docs.append(fm.slug)
                enqueue_work(
                    WorkItem(
                        kind="needs_topic_review",
                        slug=fm.slug,
                        detail=f"topic '{slug}' was deleted; reassign or accept",
                        created=datetime.now(timezone.utc),
                    )
                )

    topic_path = get_topic_path(slug)
    topic_path.unlink()
    regenerate_index()

    typer.echo(f"Deleted topic '{slug}'.")
    typer.echo(f"  Removed file: {topic_path}")
    typer.echo(f"  Docs affected: {len(affected_docs)}")
    if affected_docs:
        for d in affected_docs:
            typer.echo(f"    - {d}")
        typer.echo(f"  Enqueued {len(affected_docs)} `needs_topic_review` work item(s).")


@app.command("show")
def show(
    slug: str = typer.Argument(..., help="Topic slug"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Show a topic's title, summary, parent, related, and member docs."""
    _ensure_archive_initialized()

    if not topic_exists(slug):
        typer.echo(f"Error: topic '{slug}' does not exist.")
        raise typer.Exit(1)

    topic = load_topic(slug)

    if json_out:
        typer.echo(json_lib.dumps(topic.model_dump(mode="json", exclude_none=True), indent=2))
        return

    typer.echo(f"slug:    {topic.slug}")
    typer.echo(f"title:   {topic.title}")
    typer.echo(f"parent:  {topic.parent or '(none)'}")
    typer.echo(f"related: {', '.join(topic.related) if topic.related else '(none)'}")
    typer.echo(f"created: {topic.created}")
    typer.echo(f"updated: {topic.updated}")
    typer.echo(f"last_maintained: {topic.last_maintained or '(never)'}")
    typer.echo()
    typer.echo("summary:")
    for line in topic.summary.splitlines():
        typer.echo(f"  {line}")
    typer.echo()
    typer.echo(f"docs ({len(topic.docs)}):")
    if not topic.docs:
        typer.echo("  (no member docs yet)")
    for d in topic.docs:
        hook = d.hook or "(no hook)"
        typer.echo(f"  - {d.slug}: {hook}")


def topics(
    match: str | None = typer.Option(
        None, "--match", "-m", help="Case-insensitive substring match against title or summary"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """List all topics. Use --match to filter by keyword (structural, not QMD)."""
    _ensure_archive_initialized()
    all_topics = list_all_topics()

    if match:
        needle = match.lower()
        all_topics = [
            t
            for t in all_topics
            if needle in t.title.lower() or needle in (t.summary or "").lower()
        ]

    if json_out:
        typer.echo(
            json_lib.dumps(
                [t.model_dump(mode="json", exclude_none=True) for t in all_topics],
                indent=2,
            )
        )
        return

    if not all_topics:
        typer.echo("No topics found." + (f" (filter: {match!r})" if match else ""))
        return

    typer.echo(f"Topics ({len(all_topics)}):")
    for t in all_topics:
        summary_line = (t.summary or "").strip().splitlines()[0] if t.summary else ""
        parent_str = f" ← {t.parent}" if t.parent else ""
        typer.echo(f"  {t.slug}{parent_str}")
        typer.echo(f"    {t.title}")
        if summary_line:
            typer.echo(f"    {summary_line}")
        typer.echo(f"    docs: {len(t.docs)}")
