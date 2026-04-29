"""nexus archive index — print or regenerate archive/index.toml."""

import json as json_lib

import typer

from src.utils.archive import get_index_path, load_index, regenerate_index
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def index_cmd(
    regenerate: bool = typer.Option(
        False, "--regenerate", help="Rebuild index.toml from disk before printing"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Print the archive index — counts and topics with summary lines."""
    _ensure_archive_initialized()

    if regenerate:
        index = regenerate_index()
        if not json_out:
            typer.echo("Regenerated index.toml.")
            typer.echo()
    else:
        index = load_index()
        if index is None:
            typer.echo(
                "No index.toml found. Run `nexus archive index --regenerate` to build it."
            )
            raise typer.Exit(1)

    if json_out:
        typer.echo(json_lib.dumps(index.model_dump(mode="json", exclude_none=True), indent=2))
        return

    typer.echo(f"Generated:        {index.generated.isoformat()}")
    typer.echo(f"Path:             {get_index_path()}")
    typer.echo()
    typer.echo("Counts:")
    typer.echo(f"  docs:           {index.doc_count}")
    typer.echo(f"  topics:         {index.topic_count}")
    typer.echo(f"  pending outputs:{index.pending_outputs}")
    typer.echo(f"  orphans:        {index.orphan_count}")
    typer.echo(f"  stales:         {index.stale_count}")
    typer.echo(f"  broken links:   {index.broken_link_count}")
    typer.echo()

    if not index.topics:
        typer.echo("No topics in archive yet.")
        return

    typer.echo(f"Topics ({len(index.topics)}):")
    for t in sorted(index.topics, key=lambda x: -x.doc_count):
        parent = f" ← {t.parent}" if t.parent else ""
        typer.echo(f"  {t.slug}{parent}  (docs: {t.doc_count})")
        if t.summary_line:
            typer.echo(f"    {t.summary_line}")
        if t.children:
            typer.echo(f"    children: {', '.join(t.children)}")
        if t.related:
            typer.echo(f"    related:  {', '.join(t.related)}")
