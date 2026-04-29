"""nexus archive related — graph neighbours for a doc."""

import json as json_lib

import typer

from src.utils.archive import (
    compute_backlinks,
    compute_mentioned_by,
    compute_topic_siblings,
    doc_exists,
    load_doc,
)
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _summary_first_line(summary: str) -> str:
    line = (summary or "").strip().splitlines()
    return line[0] if line else ""


def _enrich(slug: str) -> dict | None:
    if not doc_exists(slug):
        return None
    fm, _ = load_doc(slug)
    return {
        "slug": slug,
        "title": fm.title,
        "summary": _summary_first_line(fm.summary),
    }


def related(
    slug: str = typer.Argument(..., help="Doc slug to inspect"),
    siblings_per_topic: int = typer.Option(
        5, "--siblings-per-topic", help="Max sibling docs per topic to show"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Show direct neighbours: forward links, backlinks, mentions, mentioned-by, topic siblings."""
    _ensure_archive_initialized()

    if not doc_exists(slug):
        typer.echo(f"Error: doc '{slug}' does not exist.")
        raise typer.Exit(1)

    fm, _ = load_doc(slug)

    forward_links = []
    for link in fm.links:
        enriched = _enrich(link.slug)
        if enriched is None:
            forward_links.append({"slug": link.slug, "relation": link.relation, "missing": True})
        else:
            forward_links.append({**enriched, "relation": link.relation})

    backlinks = []
    for source_slug, relation in compute_backlinks(slug):
        enriched = _enrich(source_slug)
        if enriched is None:
            continue
        backlinks.append({**enriched, "relation": relation})

    mentions = []
    for m in fm.mentions:
        enriched = _enrich(m)
        if enriched is None:
            mentions.append({"slug": m, "missing": True})
        else:
            mentions.append(enriched)

    mentioned_by = []
    for source_slug in compute_mentioned_by(slug):
        enriched = _enrich(source_slug)
        if enriched is None:
            continue
        mentioned_by.append(enriched)

    sibling_map = compute_topic_siblings(slug, limit_per_topic=siblings_per_topic)
    topic_siblings: dict[str, list[dict]] = {}
    for topic_slug, siblings in sibling_map.items():
        topic_siblings[topic_slug] = [_enrich(s) or {"slug": s, "missing": True} for s in siblings]

    out = {
        "center": slug,
        "forward_links": forward_links,
        "backlinks": backlinks,
        "mentions": mentions,
        "mentioned_by": mentioned_by,
        "topic_siblings": topic_siblings,
    }

    if json_out:
        typer.echo(json_lib.dumps(out, indent=2))
        return

    typer.echo(f"Related neighbours for '{slug}':")
    typer.echo()

    typer.echo(f"forward links ({len(forward_links)}):")
    for x in forward_links:
        marker = "(missing)" if x.get("missing") else ""
        typer.echo(f"  -[{x['relation']}]-> {x['slug']} {marker}")
        if x.get("title"):
            typer.echo(f"      {x['title']}")
            if x.get("summary"):
                typer.echo(f"      {x['summary']}")
    typer.echo()

    typer.echo(f"backlinks ({len(backlinks)}):")
    for x in backlinks:
        typer.echo(f"  <-[{x['relation']}]- {x['slug']}")
        typer.echo(f"      {x['title']}")
        if x.get("summary"):
            typer.echo(f"      {x['summary']}")
    typer.echo()

    typer.echo(f"mentions ({len(mentions)}):")
    for x in mentions:
        marker = "(missing)" if x.get("missing") else ""
        typer.echo(f"  {x['slug']} {marker}")
        if x.get("title"):
            typer.echo(f"      {x['title']}")
    typer.echo()

    typer.echo(f"mentioned-by ({len(mentioned_by)}):")
    for x in mentioned_by:
        typer.echo(f"  {x['slug']} — {x['title']}")
    typer.echo()

    if topic_siblings:
        typer.echo("topic siblings:")
        for topic_slug, siblings in topic_siblings.items():
            typer.echo(f"  [{topic_slug}] ({len(siblings)})")
            for s in siblings:
                marker = "(missing)" if s.get("missing") else ""
                title = f" — {s['title']}" if s.get("title") else ""
                typer.echo(f"    {s['slug']}{title} {marker}")
