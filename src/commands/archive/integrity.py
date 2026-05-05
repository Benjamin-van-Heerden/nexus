"""nexus archive integrity — scan and repair archive graph drift."""

import json as json_lib
from datetime import datetime, timezone

import typer

from src.models.archive.work import WorkItem
from src.utils.archive import (
    doc_exists,
    enqueue_work,
    list_all_docs_with_frontmatter,
    list_all_outputs_with_frontmatter,
    list_all_topics,
    load_work_queue,
    regenerate_index,
    save_doc,
    save_topic,
    topic_exists,
)
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _work_exists(kind: str, slug: str, detail: str) -> bool:
    return any(
        item.kind == kind and item.slug == slug and item.detail == detail
        for item in load_work_queue().items
    )


def _enqueue_once(kind: str, slug: str, detail: str, added: list[dict]) -> None:
    if _work_exists(kind, slug, detail):
        return
    enqueue_work(
        WorkItem(
            kind=kind,  # type: ignore[arg-type]
            slug=slug,
            detail=detail,
            created=datetime.now(timezone.utc),
        )
    )
    added.append({"kind": kind, "slug": slug, "detail": detail})


def integrity(
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Scan archive refs, enqueue fixes, and strip invalid topic members."""
    _ensure_archive_initialized()

    added: list[dict] = []
    counts = {
        "broken_links": 0,
        "missing_topics": 0,
        "missing_mentions": 0,
        "orphan_topic_members_removed": 0,
        "broken_output_cites": 0,
    }

    for slug, fm, body in list_all_docs_with_frontmatter():
        modified = False
        broken_links = set(fm.broken_links)

        for link in fm.links:
            if not doc_exists(link.slug):
                counts["broken_links"] += 1
                broken_links.add(link.slug)
                _enqueue_once(
                    "broken_link",
                    slug,
                    f"link target '{link.slug}' does not exist (relation: {link.relation})",
                    added,
                )

        for topic_slug in fm.topics:
            if not topic_exists(topic_slug):
                counts["missing_topics"] += 1
                _enqueue_once(
                    "needs_topic_review",
                    slug,
                    f"topic '{topic_slug}' does not exist",
                    added,
                )

        for mention in fm.mentions:
            if not doc_exists(mention):
                counts["missing_mentions"] += 1

        if sorted(broken_links) != fm.broken_links:
            fm.broken_links = sorted(broken_links)
            modified = True

        if modified:
            save_doc(fm, body)

    for topic in list_all_topics():
        before = len(topic.docs)
        topic.docs = [member for member in topic.docs if doc_exists(member.slug)]
        removed = before - len(topic.docs)
        if removed:
            counts["orphan_topic_members_removed"] += removed
            save_topic(topic)

    for output_slug, fm, _body in list_all_outputs_with_frontmatter():
        for cite in fm.cites:
            if not doc_exists(cite):
                counts["broken_output_cites"] += 1
                _enqueue_once(
                    "broken_link",
                    output_slug,
                    f"output cites missing doc '{cite}'",
                    added,
                )

    regenerate_index()
    report = {"counts": counts, "new_work_items": added}

    if json_out:
        typer.echo(json_lib.dumps(report, indent=2))
        return

    typer.echo("Archive integrity scan complete.")
    typer.echo("Counts:")
    for key, value in counts.items():
        typer.echo(f"  {key}: {value}")
    typer.echo()
    if added:
        typer.echo(f"New work items ({len(added)}):")
        for item in added:
            typer.echo(f"  - {item['kind']}: {item['slug']} — {item['detail']}")
    else:
        typer.echo("No new work items enqueued.")
