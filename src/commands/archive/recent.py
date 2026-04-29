"""nexus archive recent — list recently updated wiki docs."""

import json as json_lib
from datetime import date, timedelta

import typer

from src.utils.archive import list_all_docs_with_frontmatter
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _summary_first_line(summary: str) -> str:
    line = (summary or "").strip().splitlines()
    return line[0] if line else ""


def recent(
    days: int = typer.Option(7, "--days", "-d", help="Window in days (default 7)"),
    n: int = typer.Option(20, "-n", help="Max results (default 20)"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """List wiki docs sorted by `updated` desc, filtered to the last N days."""
    _ensure_archive_initialized()

    threshold = date.today() - timedelta(days=days)
    rows = []
    for slug, fm, _body in list_all_docs_with_frontmatter():
        if fm.updated >= threshold:
            rows.append(
                {
                    "slug": slug,
                    "title": fm.title,
                    "summary": _summary_first_line(fm.summary),
                    "topics": fm.topics,
                    "updated": fm.updated.isoformat(),
                    "status": fm.status,
                }
            )

    rows.sort(key=lambda r: r["updated"], reverse=True)
    rows = rows[:n]

    if json_out:
        typer.echo(json_lib.dumps(rows, indent=2))
        return

    if not rows:
        typer.echo(f"No docs updated in the last {days} day(s).")
        return

    typer.echo(f"Recent docs (last {days} day(s), top {len(rows)}):")
    for r in rows:
        typer.echo(f"  {r['slug']} [{r['status']}]  ({r['updated']})")
        typer.echo(f"    {r['title']}")
        if r["summary"]:
            typer.echo(f"    {r['summary']}")
        if r["topics"]:
            typer.echo(f"    topics: {', '.join(r['topics'])}")
