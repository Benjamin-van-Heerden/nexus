"""nexus archive write — commit a drafted wiki doc to the archive."""

from datetime import date, datetime, timezone
from pathlib import Path

import typer
from pydantic import ValidationError

from src.models.archive.doc import DocFrontmatter
from src.models.archive.topic import TopicConfig
from src.models.archive.work import WorkItem
from src.utils.archive import (
    doc_exists,
    enqueue_work,
    extract_mentions,
    get_doc_path,
    is_valid_slug,
    parse_frontmatter,
    regenerate_index,
    save_doc,
    save_topic,
    sync_topic_membership,
    topic_exists,
    trigger_qmd_update_after_mutation,
)
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _read_draft(file: Path) -> tuple[dict, str]:
    if not file.is_file():
        typer.echo(f"Error: draft file not found: {file}")
        raise typer.Exit(1)
    text = file.read_text(encoding="utf-8")
    try:
        return parse_frontmatter(text)
    except ValueError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


def _validate_doc_frontmatter(fm_dict: dict, slug_arg: str) -> DocFrontmatter:
    if fm_dict.get("slug") != slug_arg:
        typer.echo(
            f"Error: slug mismatch. Argument='{slug_arg}', frontmatter='{fm_dict.get('slug')}'."
        )
        raise typer.Exit(1)
    if not is_valid_slug(slug_arg):
        typer.echo(f"Error: '{slug_arg}' is not a valid kebab-case slug.")
        raise typer.Exit(1)

    today = date.today().isoformat()
    fm_dict.setdefault("created", today)
    fm_dict.setdefault("updated", today)
    fm_dict["last_maintained"] = today

    try:
        fm = DocFrontmatter(**fm_dict)
    except ValidationError as e:
        typer.echo("Error: frontmatter validation failed.")
        typer.echo(str(e))
        raise typer.Exit(1)

    if not fm.topics:
        typer.echo("Error: doc must belong to at least one topic (topics is empty).")
        raise typer.Exit(1)

    return fm


def _resolve_topics(fm: DocFrontmatter, strict_topics: bool) -> list[str]:
    """Validate fm.topics. With strict_topics=False, auto-create missing topics.

    Returns the list of topics that were auto-created (for reporting).
    """
    auto_created: list[str] = []
    today = date.today()
    for topic_slug in fm.topics:
        if topic_exists(topic_slug):
            continue
        if strict_topics:
            typer.echo(f"Error: topic '{topic_slug}' does not exist (--strict-topics).")
            raise typer.Exit(1)
        placeholder = TopicConfig(
            slug=topic_slug,
            title=topic_slug.replace("-", " ").title(),
            summary=(
                f"Auto-created during write of '{fm.slug}'. "
                "Refine via `nexus archive topic update`."
            ),
            created=today,
            updated=today,
            last_maintained=today,
            docs=[],
        )
        save_topic(placeholder)
        enqueue_work(
            WorkItem(
                kind="needs_topic_review",
                slug=topic_slug,
                detail=f"auto-created during write of '{fm.slug}'; refine summary",
                created=datetime.now(timezone.utc),
            )
        )
        auto_created.append(topic_slug)
    return auto_created


def _resolve_links(fm: DocFrontmatter) -> list[str]:
    """Verify each links[].slug exists. Update fm.broken_links and enqueue.

    Returns the broken_links list (sorted, deduped).
    """
    broken: set[str] = set()
    for link in fm.links:
        if not doc_exists(link.slug):
            broken.add(link.slug)
            enqueue_work(
                WorkItem(
                    kind="broken_link",
                    slug=fm.slug,
                    detail=f"link target '{link.slug}' does not exist (relation: {link.relation})",
                    created=datetime.now(timezone.utc),
                )
            )
    fm.broken_links = sorted(broken)
    return fm.broken_links


def write(
    slug: str = typer.Argument(..., help="Doc slug (must match frontmatter slug)"),
    file: Path = typer.Option(..., "--file", "-f", help="Path to the draft markdown file"),
    strict_topics: bool = typer.Option(
        False,
        "--strict-topics",
        help="Fail if any topic in frontmatter doesn't exist (default: auto-create)",
    ),
):
    """Commit a drafted wiki doc to the archive.

    The agent drafts frontmatter + body in a temp file; this command
    validates, persists, syncs topic membership, and queues a QMD update.
    """
    _ensure_archive_initialized()

    if doc_exists(slug):
        typer.echo(f"Error: doc '{slug}' already exists. Use `nexus archive doc update` instead.")
        raise typer.Exit(1)

    fm_dict, body = _read_draft(file)
    fm = _validate_doc_frontmatter(fm_dict, slug)
    auto_created = _resolve_topics(fm, strict_topics)
    broken = _resolve_links(fm)
    fm.mentions = extract_mentions(body)

    save_doc(fm, body)
    sync_topic_membership(fm.slug, new_topics=fm.topics, old_topics=[])
    regenerate_index()
    trigger_qmd_update_after_mutation(typer.echo)

    typer.echo(f"Wrote doc '{slug}'.")
    typer.echo(f"  Path: {get_doc_path(slug)}")
    typer.echo(f"  Topics: {', '.join(fm.topics)}")
    if auto_created:
        typer.echo(f"  Auto-created topics: {', '.join(auto_created)}")
    typer.echo(f"  Links: {len(fm.links)} curated, {len(broken)} broken")
    if broken:
        typer.echo(f"    broken: {', '.join(broken)}")
    typer.echo(f"  Mentions: {len(fm.mentions)} extracted")
    typer.echo()
    typer.echo("ACTION REQUIRED:")
    typer.echo(f"  Inspect via: nexus archive doc show {slug}")
