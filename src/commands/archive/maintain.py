"""nexus archive maintain — archivist maintenance session scaffold."""

from typing import Literal

import typer

from src.commands.archive.work import collect_work_items
from src.utils.archive import (
    compute_contradictions,
    get_topic_member_freshness,
    list_all_topics,
    load_archive_config,
)
from src.utils.paths import get_archive_dir

MaintainTask = Literal[
    "output_triage",
    "broken_links",
    "orphans",
    "stale",
    "topic_summaries",
    "contradictions",
]

def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _recommendation(kind: str, slug: str, detail: str = "") -> list[str]:
    if kind == "pending_output":
        return [
            f"nexus archive output show {slug} --body",
            f"nexus archive output integrate {slug} --into <doc-slug>",
            f"nexus archive output split {slug} --create <new-a>,<new-b>",
            f"nexus archive output archive {slug}",
        ]
    if kind == "broken_link":
        if detail.startswith("output cites"):
            return [
                f"nexus archive output show {slug} --body",
                "Decide whether to archive the output or repair it in a new saved output.",
                f"nexus archive output archive {slug}",
            ]
        return [
            f"nexus archive doc show {slug} --body",
            f"nexus archive link add {slug} <replacement-slug> --relation references",
            f"nexus archive link remove {slug} <broken-target>",
            f"nexus archive doc update {slug} --file <resolved-draft.md>",
        ]
    if kind == "orphan":
        return [
            f"nexus archive doc show {slug}",
            f"nexus archive query \"<title or key phrase from {slug}>\"",
            f"nexus archive doc update {slug} --file <draft-with-topics-or-links.md>",
        ]
    if kind == "stale":
        return [
            f"nexus archive doc show {slug} --body",
            f"nexus archive related {slug}",
            f"nexus archive doc update {slug} --file <refreshed-draft.md>",
        ]
    if kind == "topic_summary":
        return [
            f"nexus archive topic show {slug}",
            f"nexus archive topic update {slug} --summary \"<refreshed summary>\"",
        ]
    if kind == "contradiction":
        return [
            "nexus archive query \"<recent topic or summary>\"",
            "nexus archive related <slug>",
            "nexus archive link add <a> <b> --relation contradicts",
        ]
    return []


def _topic_summary_items() -> list[dict]:
    rows = []
    for topic in list_all_topics():
        if get_topic_member_freshness(topic.slug):
            rows.append(
                {
                    "kind": "topic_summary",
                    "slug": topic.slug,
                    "detail": "topic members changed or member docs updated since last maintained",
                    "created": topic.updated.isoformat(),
                    "source": "computed",
                }
            )
    return rows


def maintain(
    task: MaintainTask | None = typer.Option(None, "--task", help="Show one maintenance job"),
    limit: int | None = typer.Option(None, "--limit", help="Max items per job"),
):
    """Surface the archive maintenance queue in recommended order."""
    _ensure_archive_initialized()

    config = load_archive_config()
    if limit is None:
        limit = config.maintenance.batch_size

    all_items = collect_work_items()
    task_order: list[tuple[MaintainTask, str, list[dict]]] = [
        (
            "output_triage",
            "Output triage",
            [row for row in all_items if row["kind"] == "pending_output"],
        ),
        (
            "broken_links",
            "Broken-link resolution",
            [row for row in all_items if row["kind"] == "broken_link"],
        ),
        (
            "orphans",
            "Orphan rescue",
            [row for row in all_items if row["kind"] == "orphan"],
        ),
        (
            "stale",
            "Stale doc review",
            [row for row in all_items if row["kind"] == "stale"],
        ),
        ("topic_summaries", "Topic summary refresh", _topic_summary_items()),
        (
            "contradictions",
            "Contradiction scan",
            [
                {
                    "kind": "contradiction",
                    "slug": f"{a} / {b}",
                    "detail": "best-effort QMD contradiction candidate",
                    "created": "",
                    "source": "computed",
                }
                for a, b in compute_contradictions()
            ],
        ),
    ]

    if task is not None:
        task_order = [item for item in task_order if item[0] == task]

    typer.echo("NEXUS ARCHIVE — MAINTENANCE")
    typer.echo("=" * 60)
    typer.echo("This command is read-only. Work through items with targeted commands.")
    typer.echo()

    any_items = False
    for task_key, title, rows in task_order:
        rows = rows[:limit]
        typer.echo(title)
        typer.echo("-" * len(title))
        if not rows:
            if task_key == "contradictions":
                typer.echo("  No automatic candidates. Run a manual scan with QMD/query as needed.")
            else:
                typer.echo("  (none)")
            typer.echo()
            continue

        any_items = True
        for row in rows:
            typer.echo(f"  {row['kind']}: {row['slug']}")
            if row.get("detail"):
                typer.echo(f"    {row['detail']}")
            typer.echo("    Recommended commands:")
            for command in _recommendation(
                row["kind"], row["slug"], row.get("detail", "")
            ):
                typer.echo(f"      {command}")
        typer.echo()

    if not any_items:
        typer.echo("No actionable maintenance items in the selected scope.")
        typer.echo()

    typer.echo("ACTION REQUIRED:")
    typer.echo("  Work through these in order. After each resolution, re-run:")
    typer.echo("    nexus archive work list")
