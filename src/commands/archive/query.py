"""nexus archive query — recall mode: QMD hits enriched with frontmatter-summary view."""

import json as json_lib

import typer

from src.utils.archive import (
    QmdNotInstalledError,
    load_archive_config,
    load_doc,
    load_topic,
    qmd_path_to_slug,
    qmd_query,
    topic_exists,
)
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _doc_summary_view(slug: str) -> dict | None:
    try:
        fm, _body = load_doc(slug)
    except Exception:
        return None
    return {
        "slug": fm.slug,
        "title": fm.title,
        "summary": fm.summary,
        "topics": fm.topics,
        "links": [{"slug": link.slug, "relation": link.relation} for link in fm.links],
        "tags": fm.tags,
        "status": fm.status,
    }


def _topic_summary_line(topic_slug: str) -> str:
    if not topic_exists(topic_slug):
        return ""
    try:
        topic = load_topic(topic_slug)
    except Exception:
        return ""
    summary = (topic.summary or "").strip().splitlines()
    return summary[0] if summary else ""


def query(
    q: str = typer.Argument(..., help="Recall query"),
    n: int | None = typer.Option(
        None, "-n", help="Max hits (default: archive.toml's qmd.default_recall_n)"
    ),
    no_breadcrumbs: bool = typer.Option(
        False, "--no-breadcrumbs", help="Omit the 'Relevant topics' section"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Recall mode — QMD hits surfaced as frontmatter-summary doc views + topic breadcrumbs.

    Never returns doc bodies, raw QMD snippets, or LLM-synthesised prose. The
    CLI is a data primitive; the calling agent does the synthesis.
    """
    _ensure_archive_initialized()

    if n is None:
        n = load_archive_config().qmd.default_recall_n

    try:
        hits = qmd_query(q, n)
    except QmdNotInstalledError as e:
        typer.echo(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.echo(f"qmd query failed: {e}")
        raise typer.Exit(1)

    docs: list[dict] = []
    seen_slugs: set[str] = set()
    skipped_paths: list[str] = []
    for hit in hits:
        path = hit.get("path")
        slug = qmd_path_to_slug(path)
        if slug is None or slug in seen_slugs:
            if slug is None and path:
                skipped_paths.append(str(path))
            continue
        view = _doc_summary_view(slug)
        if view is None:
            skipped_paths.append(str(path))
            continue
        seen_slugs.add(slug)
        docs.append(view)

    topic_union: list[str] = []
    seen_topics: set[str] = set()
    for d in docs:
        for t in d["topics"]:
            if t not in seen_topics:
                topic_union.append(t)
                seen_topics.add(t)

    topics_view = [
        {"slug": t, "summary_line": _topic_summary_line(t)} for t in topic_union
    ]

    out = {"query": q, "topics": topics_view, "docs": docs, "skipped": skipped_paths}

    if json_out:
        typer.echo(json_lib.dumps(out, indent=2))
        return

    if not docs:
        typer.echo(f"No matching docs for query: {q!r}")
        if skipped_paths:
            typer.echo(f"  ({len(skipped_paths)} qmd hit(s) could not be resolved to wiki slugs)")
        return

    if not no_breadcrumbs and topics_view:
        typer.echo(f"Relevant topics ({len(topics_view)}):")
        for t in topics_view:
            line = t["summary_line"] or "(no summary)"
            typer.echo(f"  {t['slug']} — {line}")
        typer.echo()

    typer.echo(f"Relevant docs ({len(docs)}):")
    for d in docs:
        typer.echo(f"  {d['slug']}  [{d['status']}]")
        typer.echo(f"    Title:    {d['title']}")
        if d["summary"]:
            first_line = d["summary"].strip().splitlines()[0]
            typer.echo(f"    Summary:  {first_line}")
        if d["topics"]:
            typer.echo(f"    Topics:   {', '.join(d['topics'])}")
        if d["links"]:
            link_strs = [f"{link['relation']} → {link['slug']}" for link in d["links"]]
            typer.echo(f"    Links:    {'; '.join(link_strs)}")
        if d["tags"]:
            typer.echo(f"    Tags:     {', '.join(d['tags'])}")

    if skipped_paths:
        typer.echo()
        typer.echo(f"Note: {len(skipped_paths)} qmd hit(s) could not be resolved to wiki slugs.")
