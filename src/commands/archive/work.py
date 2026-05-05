"""nexus archive work — list persisted and computed archive work."""

import json as json_lib
from datetime import datetime, timezone
from typing import Literal

import typer

from src.utils.archive import (
    compute_orphans,
    compute_stales,
    load_archive_config,
    load_work_queue,
)
from src.utils.paths import get_archive_dir

WorkKindOption = Literal[
    "broken_link",
    "pending_output",
    "orphan",
    "stale",
    "contradiction",
    "needs_topic_review",
]

app = typer.Typer(help="Show archive work queue")


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def collect_work_items(kind: WorkKindOption | None = None) -> list[dict]:
    config = load_archive_config()
    rows: list[dict] = []

    for item in load_work_queue().items:
        rows.append(
            {
                "kind": item.kind,
                "slug": item.slug,
                "detail": item.detail,
                "created": item.created.isoformat(),
                "source": "persisted",
            }
        )

    computed_at = datetime.now(timezone.utc).isoformat()
    for slug in compute_orphans():
        rows.append(
            {
                "kind": "orphan",
                "slug": slug,
                "detail": "doc has no topics or no inbound links/mentions",
                "created": computed_at,
                "source": "computed",
            }
        )

    for slug in compute_stales(config.maintenance.staleness_days):
        rows.append(
            {
                "kind": "stale",
                "slug": slug,
                "detail": f"last maintained older than {config.maintenance.staleness_days} days",
                "created": computed_at,
                "source": "computed",
            }
        )

    if kind is not None:
        rows = [row for row in rows if row["kind"] == kind]

    return sorted(rows, key=lambda row: (row["kind"], row["created"], row["slug"]))


@app.command("list")
def list_work(
    kind: WorkKindOption | None = typer.Option(None, "--kind", help="Filter by work kind"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """List persisted work plus computed orphan/stale items."""
    _ensure_archive_initialized()

    rows = collect_work_items(kind)
    if json_out:
        typer.echo(json_lib.dumps(rows, indent=2))
        return

    if not rows:
        suffix = f" for kind '{kind}'" if kind else ""
        typer.echo(f"No archive work items{suffix}.")
        return

    typer.echo(f"Archive work items ({len(rows)}):")
    current_kind = None
    for row in rows:
        if row["kind"] != current_kind:
            current_kind = row["kind"]
            typer.echo()
            typer.echo(f"{current_kind}:")
        typer.echo(f"  - {row['slug']} [{row['source']}]")
        if row["detail"]:
            typer.echo(f"    {row['detail']}")
        typer.echo(f"    created: {row['created']}")
