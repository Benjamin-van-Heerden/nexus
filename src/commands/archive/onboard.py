"""nexus archive onboard — full archivist context dump."""

from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Literal

import typer

from src.commands.archive.work import collect_work_items
from src.utils.archive import (
    compute_orphans,
    compute_stales,
    get_agent_instructions_path,
    get_archive_config_path,
    get_archive_state_path,
    get_index_path,
    get_outputs_dir,
    get_raw_dir,
    get_topics_dir,
    get_wiki_dir,
    get_work_path,
    list_all_docs_with_frontmatter,
    list_all_outputs,
    load_archive_config,
    load_archive_state,
    load_index,
    regenerate_index,
)
from src.utils.paths import get_archive_dir
from src.utils.pause import check_pause

ArchiveTask = Literal["add", "query", "maintain", "ingest"]


def _section(title: str) -> None:
    typer.echo("-" * 60)
    typer.echo(title)
    typer.echo("-" * 60)


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _task_framing(task: ArchiveTask | None) -> str:
    if task in {"add", "ingest"}:
        return "Task: ingestion — stage source material and decide write/update/duplicate."
    if task == "query":
        return "Task: query — use recall plus graph traversal to answer a focused request."
    if task == "maintain":
        return "Task: maintenance — surface and drain bounded work queue items."
    return "Task: direct archive session — wait for the user's requested archive work."


def _summary_line(text: str) -> str:
    lines = (text or "").strip().splitlines()
    return lines[0] if lines else ""


def _recent_docs(limit: int = 5) -> list[dict]:
    rows = []
    for slug, fm, _body in list_all_docs_with_frontmatter():
        rows.append(
            {
                "slug": slug,
                "title": fm.title,
                "summary": _summary_line(fm.summary),
                "updated": fm.updated,
                "status": fm.status,
            }
        )
    rows.sort(key=lambda row: (row["updated"], row["slug"]), reverse=True)
    return rows[:limit]


def _filtered_work(task: ArchiveTask | None) -> list[dict]:
    rows = collect_work_items()
    if task in {"add", "ingest"}:
        return [row for row in rows if row["kind"] in {"broken_link", "pending_output"}]
    if task == "query":
        return [row for row in rows if row["kind"] in {"orphan", "stale", "broken_link"}]
    return rows


def _print_work_summary(task: ArchiveTask | None) -> None:
    rows = _filtered_work(task)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["kind"]].append(row)

    if not rows:
        typer.echo("No work items in scope.")
        return

    per_kind_limit = 10 if task else 3
    for kind in sorted(grouped):
        items = grouped[kind][:per_kind_limit]
        typer.echo(f"{kind} ({len(grouped[kind])}):")
        for item in items:
            typer.echo(f"  - {item['slug']} [{item['source']}]")
            if item["detail"]:
                typer.echo(f"    {item['detail']}")
        if len(grouped[kind]) > per_kind_limit:
            typer.echo(f"    ... {len(grouped[kind]) - per_kind_limit} more")


def onboard(
    task: ArchiveTask | None = typer.Option(None, "--task", help="Task framing for this wake"),
):
    """Print the full archive context for a fresh archivist session."""
    paused = check_pause("archive")
    if paused:
        typer.echo(
            f"Nexus archive is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    _ensure_archive_initialized()

    today = date.today()
    config = load_archive_config()
    state = load_archive_state()
    index = load_index() or regenerate_index()
    work_rows = collect_work_items()
    work_counts = Counter(row["kind"] for row in work_rows)
    outputs_by_status = Counter(output.status for output in list_all_outputs())

    typer.echo("=" * 60)
    typer.echo("NEXUS ARCHIVE — ONBOARD")
    typer.echo("=" * 60)
    typer.echo(f"Date: {today.strftime('%A, %B %d, %Y')}")
    typer.echo("You are the archivist of Benjamin's second brain.")
    typer.echo(_task_framing(task))
    typer.echo()

    _section("ARCHIVE STATE")
    typer.echo(f"Docs:           {index.doc_count}")
    typer.echo(f"Topics:         {index.topic_count}")
    typer.echo(
        "Outputs:        "
        f"pending={outputs_by_status.get('pending_review', 0)}, "
        f"integrated={outputs_by_status.get('integrated', 0)}, "
        f"archived={outputs_by_status.get('archived', 0)}"
    )
    typer.echo(f"Orphans:        {len(compute_orphans())}")
    typer.echo(f"Stales:         {len(compute_stales(config.maintenance.staleness_days))}")
    typer.echo(f"Broken links:   {work_counts.get('broken_link', 0)}")
    typer.echo(f"Last reindex:   {state.last_reindex or '(never)'}")
    typer.echo(f"Last QMD update:{state.last_qmd_update or '(never)'}")
    typer.echo()
    typer.echo("Pending work by kind:")
    if work_counts:
        for kind, count in sorted(work_counts.items()):
            typer.echo(f"  {kind}: {count}")
    else:
        typer.echo("  (none)")
    typer.echo()

    _section("TOP-LEVEL INDEX SUMMARY")
    if not index.topics:
        typer.echo("No topics yet. Use `nexus archive topic new` before writing docs.")
    else:
        for topic in sorted(index.topics, key=lambda t: (-t.doc_count, t.slug))[:10]:
            parent = f" parent={topic.parent}" if topic.parent else ""
            typer.echo(f"  {topic.slug} (docs: {topic.doc_count}){parent}")
            if topic.summary_line:
                typer.echo(f"    {topic.summary_line}")
    typer.echo()
    typer.echo("Use `nexus archive index` for the full map.")
    typer.echo("Use `nexus archive topic <slug>` for a single topic.")
    typer.echo()

    _section("RECENT ACTIVITY")
    recent = _recent_docs()
    if not recent:
        typer.echo("No wiki docs yet.")
    else:
        for row in recent:
            typer.echo(f"  {row['slug']} [{row['status']}] updated={row['updated']}")
            typer.echo(f"    {row['title']}")
            if row["summary"]:
                typer.echo(f"    {row['summary']}")
    typer.echo()

    _section("WORK QUEUE SUMMARY")
    _print_work_summary(task)
    typer.echo()

    _section("PATHS")
    typer.echo(f"Archive root: {get_archive_dir()}/")
    typer.echo(f"Wiki:         {get_wiki_dir()}/")
    typer.echo(f"Topics:       {get_topics_dir()}/")
    typer.echo(f"Raw:          {get_raw_dir()}/")
    typer.echo(f"Outputs:      {get_outputs_dir()}/")
    typer.echo(f"Index:        {get_index_path()}")
    typer.echo(f"Work queue:   {get_work_path()}")
    typer.echo(f"Config:       {get_archive_config_path()}")
    typer.echo(f"State:        {get_archive_state_path()}")
    typer.echo("Run cycle:    " + str(get_archive_dir().parent / "archive_run_cycle.md"))
    typer.echo("QMD install:  " + str(get_archive_dir().parent / "scripts" / "install-qmd.sh"))
    typer.echo()
    typer.echo("ALL file creation MUST happen inside archive/ subdirectories or /tmp drafts.")
    typer.echo("NEVER create archive content in your own workspace or any other location.")
    typer.echo()

    _section("AGENT INSTRUCTIONS")
    instructions_path = get_agent_instructions_path()
    if instructions_path.exists():
        typer.echo(instructions_path.read_text().strip())
    else:
        typer.echo(f"WARNING: agent instructions not found: {instructions_path}")
    typer.echo()

    typer.echo("=" * 60)
    typer.echo("ACTION REQUIRED")
    typer.echo("=" * 60)
    typer.echo("Read the instructions above and send a message to the user")
    typer.echo("NOW. Do not silently process this output — the user is")
    typer.echo("waiting for your response.")
    typer.echo("=" * 60)
