"""nexus archive search — raw QMD search hits, no enrichment."""

import json as json_lib

import typer

from src.utils.archive import (
    QmdNotInstalledError,
    load_archive_config,
    qmd_search,
)
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def search(
    q: str = typer.Argument(..., help="Search query"),
    n: int | None = typer.Option(
        None, "-n", help="Max hits (default: archive.toml's qmd.default_recall_n)"
    ),
    json_out: bool = typer.Option(False, "--json", help="Pass through QMD's JSON output"),
):
    """Raw QMD search hits — no doc-frontmatter enrichment.

    Use this when you want QMD's view directly. For the enriched
    structured-graph view, use `nexus archive query` instead.
    """
    _ensure_archive_initialized()

    if n is None:
        n = load_archive_config().qmd.default_recall_n

    try:
        hits = qmd_search(q, n)
    except QmdNotInstalledError as e:
        typer.echo(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.echo(f"qmd search failed: {e}")
        raise typer.Exit(1)

    if json_out:
        typer.echo(json_lib.dumps(hits, indent=2))
        return

    if not hits:
        typer.echo(f"No hits for query: {q!r}")
        return

    typer.echo(f"QMD search hits for {q!r} ({len(hits)}):")
    for i, h in enumerate(hits, 1):
        typer.echo(f"  {i}. {h.get('path', '(no path)')}")
        if "score" in h:
            typer.echo(f"     score: {h['score']}")
        if "title" in h:
            typer.echo(f"     title: {h['title']}")
        if "snippet" in h:
            snippet = str(h["snippet"]).strip().replace("\n", " ")
            if len(snippet) > 200:
                snippet = snippet[:200] + "…"
            typer.echo(f"     snippet: {snippet}")
