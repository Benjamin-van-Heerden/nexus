"""nexus archive output — persisted syntheses produced by agents."""

import json as json_lib
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

import typer
from pydantic import ValidationError

from src.models.archive.output import OutputFrontmatter
from src.models.archive.work import WorkItem
from src.utils.archive import (
    doc_exists,
    enqueue_work,
    get_output_path,
    is_valid_slug,
    list_all_outputs,
    load_doc,
    load_output,
    mark_work_item_resolved,
    output_exists,
    parse_frontmatter,
    regenerate_index,
    save_doc,
    save_output,
)
from src.utils.paths import get_archive_dir

app = typer.Typer(help="Manage persisted archive outputs")

OutputStatusOption = Literal["pending_review", "integrated", "archived"]


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _read_output_draft(file: Path) -> tuple[dict, str]:
    if not file.is_file():
        typer.echo(f"Error: output draft file not found: {file}")
        raise typer.Exit(1)
    text = file.read_text(encoding="utf-8")
    try:
        return parse_frontmatter(text)
    except ValueError as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)


def _validate_cites(cites: list[str]) -> None:
    missing = [slug for slug in cites if not doc_exists(slug)]
    if missing:
        typer.echo("Error: output cites missing wiki docs:")
        for slug in missing:
            typer.echo(f"  - {slug}")
        raise typer.Exit(1)


@app.command("save")
def save(
    slug: str = typer.Argument(..., help="Output slug"),
    file: Path = typer.Option(..., "--file", "-f", help="Path to output markdown draft"),
):
    """Persist a synthesis into archive/outputs and enqueue pending review."""
    _ensure_archive_initialized()

    if not is_valid_slug(slug):
        typer.echo(f"Error: '{slug}' is not a valid kebab-case slug.")
        raise typer.Exit(1)
    if output_exists(slug):
        typer.echo(f"Error: output '{slug}' already exists.")
        raise typer.Exit(1)

    fm_dict, body = _read_output_draft(file)
    if fm_dict.get("slug") != slug:
        typer.echo(
            f"Error: slug mismatch. Argument='{slug}', frontmatter='{fm_dict.get('slug')}'."
        )
        raise typer.Exit(1)

    fm_dict.setdefault("created", date.today().isoformat())
    fm_dict.setdefault("status", "pending_review")

    try:
        fm = OutputFrontmatter(**fm_dict)
    except ValidationError as e:
        typer.echo("Error: output frontmatter validation failed.")
        typer.echo(str(e))
        raise typer.Exit(1)

    if not fm.cites:
        typer.echo("Error: output must cite at least one wiki doc.")
        raise typer.Exit(1)
    if not fm.novelty.strip():
        typer.echo("Error: output novelty must not be empty.")
        raise typer.Exit(1)
    _validate_cites(fm.cites)

    save_output(fm, body)
    if fm.status == "pending_review":
        enqueue_work(
            WorkItem(
                kind="pending_output",
                slug=fm.slug,
                detail=f"output saved for query: {fm.query}",
                created=datetime.now(timezone.utc),
            )
        )
    regenerate_index()

    typer.echo(f"Output saved: {slug}")
    typer.echo(f"  Path: {get_output_path(slug)}")
    typer.echo(f"  Status: {fm.status}")
    typer.echo(f"  Cites: {', '.join(fm.cites)}")
    typer.echo()
    typer.echo("ACTION REQUIRED:")
    typer.echo(
        "  Output saved. It's on the work queue for archivist triage. "
        "Run `nexus archive maintain` to triage now, or it'll be processed "
        "in the next maintenance pass."
    )


@app.command("list")
def list_outputs(
    status: OutputStatusOption | None = typer.Option(None, "--status", help="Filter by status"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """List persisted outputs."""
    _ensure_archive_initialized()

    rows = []
    for fm in sorted(list_all_outputs(status), key=lambda item: (item.created, item.slug)):
        query = fm.query if len(fm.query) <= 80 else fm.query[:77] + "..."
        rows.append(
            {
                "slug": fm.slug,
                "query": query,
                "status": fm.status,
                "created": fm.created.isoformat(),
                "cites_count": len(fm.cites),
            }
        )

    if json_out:
        typer.echo(json_lib.dumps(rows, indent=2))
        return

    if not rows:
        suffix = f" with status '{status}'" if status else ""
        typer.echo(f"No outputs{suffix}.")
        return

    typer.echo(f"Outputs ({len(rows)}):")
    for row in rows:
        typer.echo(f"  {row['slug']}  [{row['status']}]")
        typer.echo(f"    created: {row['created']}")
        typer.echo(f"    query:   {row['query']}")
        typer.echo(f"    cites:   {row['cites_count']}")


@app.command("show")
def show(
    slug: str = typer.Argument(..., help="Output slug"),
    body: bool = typer.Option(False, "--body", help="Include markdown body"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Display an output's frontmatter and optionally body."""
    _ensure_archive_initialized()

    if not output_exists(slug):
        typer.echo(f"Error: output '{slug}' does not exist.")
        raise typer.Exit(1)

    fm, output_body = load_output(slug)
    fm_dump = fm.model_dump(mode="json", exclude_none=True)
    out = {"frontmatter": fm_dump, "path": str(get_output_path(slug))}
    if body:
        out["body"] = output_body

    if json_out:
        typer.echo(json_lib.dumps(out, indent=2))
        return

    typer.echo(f"slug:    {fm.slug}")
    typer.echo(f"status:  {fm.status}")
    typer.echo(f"created: {fm.created}")
    typer.echo(f"path:    {get_output_path(slug)}")
    typer.echo()
    typer.echo(f"query: {fm.query}")
    typer.echo()
    typer.echo("novelty:")
    for line in fm.novelty.splitlines():
        typer.echo(f"  {line}")
    typer.echo()
    typer.echo(f"cites: {', '.join(fm.cites)}")

    if body:
        typer.echo()
        typer.echo("-" * 60)
        typer.echo("BODY")
        typer.echo("-" * 60)
        typer.echo(output_body)


@app.command("integrate")
def integrate(
    output_slug: str = typer.Argument(..., help="Output slug"),
    into: str = typer.Option(..., "--into", help="Existing wiki doc slug"),
):
    """Track that an output has been integrated into an existing doc."""
    _ensure_archive_initialized()

    if not output_exists(output_slug):
        typer.echo(f"Error: output '{output_slug}' does not exist.")
        raise typer.Exit(1)
    if not doc_exists(into):
        typer.echo(f"Error: target doc '{into}' does not exist.")
        raise typer.Exit(1)

    out_fm, out_body = load_output(output_slug)
    if out_fm.status != "pending_review":
        typer.echo(
            f"Error: output '{output_slug}' has status '{out_fm.status}', "
            "expected pending_review."
        )
        raise typer.Exit(1)

    doc_fm, doc_body = load_doc(into)
    if output_slug not in doc_fm.provenance.origin_outputs:
        doc_fm.provenance.origin_outputs.append(output_slug)
    today = date.today()
    doc_fm.updated = today
    doc_fm.last_maintained = today

    out_fm.status = "integrated"
    save_doc(doc_fm, doc_body)
    save_output(out_fm, out_body)
    mark_work_item_resolved("pending_output", output_slug)
    regenerate_index()

    typer.echo(f"Integrated output '{output_slug}' into doc '{into}'.")
    typer.echo(f"  Added provenance.origin_outputs entry: {output_slug}")
    typer.echo("  Note: doc body was not modified. Use `nexus archive doc update` if needed.")


@app.command("split")
def split(
    output_slug: str = typer.Argument(..., help="Output slug"),
    create: str = typer.Option(..., "--create", help="Comma-separated new wiki doc slugs"),
):
    """Stage a split of one output into multiple new docs."""
    _ensure_archive_initialized()

    if not output_exists(output_slug):
        typer.echo(f"Error: output '{output_slug}' does not exist.")
        raise typer.Exit(1)

    out_fm, out_body = load_output(output_slug)
    if out_fm.status != "pending_review":
        typer.echo(
            f"Error: output '{output_slug}' has status '{out_fm.status}', "
            "expected pending_review."
        )
        raise typer.Exit(1)

    slugs = [slug.strip() for slug in create.split(",") if slug.strip()]
    if not slugs:
        typer.echo("Error: --create must include at least one slug.")
        raise typer.Exit(1)

    seen: set[str] = set()
    for slug in slugs:
        if slug in seen:
            typer.echo(f"Error: duplicate slug in --create: {slug}")
            raise typer.Exit(1)
        seen.add(slug)
        if not is_valid_slug(slug):
            typer.echo(f"Error: '{slug}' is not a valid kebab-case slug.")
            raise typer.Exit(1)
        if doc_exists(slug):
            typer.echo(f"Error: target doc '{slug}' already exists.")
            raise typer.Exit(1)

    out_fm.status = "integrated"
    save_output(out_fm, out_body)
    mark_work_item_resolved("pending_output", output_slug)
    regenerate_index()

    typer.echo(f"Output split staged: {output_slug}")
    typer.echo("  Status marked integrated immediately for v1.")
    typer.echo()
    typer.echo("ACTION REQUIRED:")
    typer.echo("  Now create each new doc:")
    for slug in slugs:
        typer.echo(f"    nexus archive write {slug} --file <draft-{slug}.md>")
    typer.echo()
    typer.echo(f"  Each draft should set provenance.origin_outputs: [{output_slug}]")


@app.command("archive")
def archive_output(
    output_slug: str = typer.Argument(..., help="Output slug"),
):
    """Mark an output archived because it does not warrant integration."""
    _ensure_archive_initialized()

    if not output_exists(output_slug):
        typer.echo(f"Error: output '{output_slug}' does not exist.")
        raise typer.Exit(1)

    fm, body = load_output(output_slug)
    if fm.status == "archived":
        typer.echo(f"Output '{output_slug}' is already archived.")
        return

    fm.status = "archived"
    save_output(fm, body)
    mark_work_item_resolved("pending_output", output_slug)
    regenerate_index()

    typer.echo(f"Archived output '{output_slug}'.")
