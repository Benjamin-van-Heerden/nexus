"""nexus archive tag — list docs carrying a specific tag."""

import json as json_lib

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


def tag(
    tag: str = typer.Argument(..., help="Tag value to filter by (exact match, case-sensitive)"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """List docs whose `tags:` includes the given tag."""
    _ensure_archive_initialized()

    rows = []
    for slug, fm, _body in list_all_docs_with_frontmatter():
        if tag in fm.tags:
            rows.append(
                {
                    "slug": slug,
                    "title": fm.title,
                    "summary": _summary_first_line(fm.summary),
                    "topics": fm.topics,
                    "tags": fm.tags,
                    "updated": fm.updated.isoformat(),
                    "status": fm.status,
                }
            )

    rows.sort(key=lambda r: r["slug"])

    if json_out:
        typer.echo(json_lib.dumps(rows, indent=2))
        return

    if not rows:
        typer.echo(f"No docs tagged '{tag}'.")
        return

    typer.echo(f"Docs tagged '{tag}' ({len(rows)}):")
    for r in rows:
        typer.echo(f"  {r['slug']} [{r['status']}]")
        typer.echo(f"    {r['title']}")
        if r["summary"]:
            typer.echo(f"    {r['summary']}")
        if r["topics"]:
            typer.echo(f"    topics: {', '.join(r['topics'])}")
        typer.echo(f"    tags:   {', '.join(r['tags'])}")
