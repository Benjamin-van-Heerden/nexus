"""nexus archive link — manage curated typed links between docs."""

from datetime import date
from typing import get_args

import typer

from src.models.archive.doc import LinkRef, LinkRelation
from src.utils.archive import (
    doc_exists,
    load_doc,
    mark_pending_qmd_update,
    regenerate_index,
    save_doc,
)
from src.utils.paths import get_archive_dir

app = typer.Typer(help="Manage curated links between docs")

VALID_RELATIONS = list(get_args(LinkRelation))


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


@app.command("add")
def add(
    from_slug: str = typer.Argument(..., help="Source doc slug"),
    to_slug: str = typer.Argument(..., help="Target doc slug"),
    relation: str = typer.Option(
        ...,
        "--relation",
        "-r",
        help=f"Relation type. One of: {', '.join(VALID_RELATIONS)}",
    ),
):
    """Add a typed link from one doc to another."""
    _ensure_archive_initialized()

    if relation not in VALID_RELATIONS:
        typer.echo(
            f"Error: invalid relation '{relation}'. "
            f"Must be one of: {', '.join(VALID_RELATIONS)}."
        )
        raise typer.Exit(1)
    if not doc_exists(from_slug):
        typer.echo(f"Error: source doc '{from_slug}' does not exist.")
        raise typer.Exit(1)
    if not doc_exists(to_slug):
        typer.echo(f"Error: target doc '{to_slug}' does not exist.")
        raise typer.Exit(1)
    if from_slug == to_slug:
        typer.echo("Error: a doc cannot link to itself.")
        raise typer.Exit(1)

    fm, body = load_doc(from_slug)
    for link in fm.links:
        if link.slug == to_slug and link.relation == relation:
            typer.echo(f"No change: link '{from_slug}' --[{relation}]--> '{to_slug}' already exists.")
            return

    fm.links.append(LinkRef(slug=to_slug, relation=relation))  # type: ignore[arg-type]
    fm.updated = date.today()
    save_doc(fm, body)
    regenerate_index()
    mark_pending_qmd_update()

    typer.echo(f"Linked '{from_slug}' --[{relation}]--> '{to_slug}'.")


@app.command("remove")
def remove(
    from_slug: str = typer.Argument(..., help="Source doc slug"),
    to_slug: str = typer.Argument(..., help="Target doc slug"),
):
    """Remove all link entries from one doc to another (any relation)."""
    _ensure_archive_initialized()

    if not doc_exists(from_slug):
        typer.echo(f"Error: source doc '{from_slug}' does not exist.")
        raise typer.Exit(1)

    fm, body = load_doc(from_slug)
    before = len(fm.links)
    fm.links = [link for link in fm.links if link.slug != to_slug]
    removed = before - len(fm.links)
    if removed == 0:
        typer.echo(f"No matching link from '{from_slug}' to '{to_slug}'.")
        return

    fm.updated = date.today()
    save_doc(fm, body)
    regenerate_index()
    mark_pending_qmd_update()

    typer.echo(f"Removed {removed} link(s) from '{from_slug}' to '{to_slug}'.")
