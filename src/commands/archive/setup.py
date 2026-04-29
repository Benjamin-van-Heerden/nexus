"""Archive setup — one-time bootstrap for the archive system."""

import typer

from src.models.archive.archive import ArchiveConfig, ArchiveState
from src.utils.archive import (
    QmdNotInstalledError,
    get_agent_instructions_path,
    get_archive_config_path,
    get_archive_state_path,
    get_index_path,
    get_outputs_dir,
    get_raw_dir,
    get_topics_dir,
    get_wiki_dir,
    get_work_path,
    load_archive_config,
    load_archive_state,
    qmd_check,
    qmd_run,
    save_archive_config,
    save_archive_state,
)
from src.utils.paths import get_archive_dir
from src.utils.pause import check_pause


def setup():
    """Create the archive directory tree, write defaults, and register with QMD."""
    paused = check_pause("archive")
    if paused:
        typer.echo(
            f"Nexus archive is paused. Reason: {paused.reason or 'no reason provided'}. "
            f"Will resume on {paused.resume_date}. Nothing further to do."
        )
        raise typer.Exit(0)

    archive_dir = get_archive_dir()
    wiki_dir = get_wiki_dir()
    topics_dir = get_topics_dir()
    raw_dir = get_raw_dir()
    outputs_dir = get_outputs_dir()
    config_path = get_archive_config_path()
    state_path = get_archive_state_path()
    work_path = get_work_path()
    index_path = get_index_path()

    typer.echo("=" * 60)
    typer.echo("NEXUS ARCHIVE — SETUP")
    typer.echo("=" * 60)
    typer.echo()

    # 1. Create directory tree
    created_dirs = []
    for d in (archive_dir, raw_dir, wiki_dir, topics_dir, outputs_dir):
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created_dirs.append(d)
    if created_dirs:
        typer.echo("Created directories:")
        for d in created_dirs:
            typer.echo(f"  {d}")
    else:
        typer.echo("Archive directories already exist.")
    typer.echo()

    # 2. Write default config / state if missing
    if not config_path.exists() or config_path.stat().st_size == 0:
        save_archive_config(ArchiveConfig())
        typer.echo(f"Wrote default config: {config_path}")
    else:
        load_archive_config()  # validate
        typer.echo(f"Config exists: {config_path}")

    if not state_path.exists() or state_path.stat().st_size == 0:
        save_archive_state(ArchiveState())
        typer.echo(f"Wrote default state: {state_path}")
    else:
        load_archive_state()  # validate
        typer.echo(f"State exists: {state_path}")

    if not work_path.exists():
        work_path.write_text("")
        typer.echo(f"Created empty work queue: {work_path}")
    else:
        typer.echo(f"Work queue exists: {work_path}")
    typer.echo()

    # 3. QMD registration
    config = load_archive_config()
    collection_name = config.qmd.collection_name
    typer.echo("-" * 60)
    typer.echo("QMD INTEGRATION")
    typer.echo("-" * 60)
    try:
        version = qmd_check()
    except QmdNotInstalledError as e:
        typer.echo(str(e))
        typer.echo()
        typer.echo("Archive directory is set up. Re-run `nexus archive setup` after")
        typer.echo("installing qmd to register the wiki collection.")
        raise typer.Exit(1)

    typer.echo(f"qmd detected: {version}")

    abs_wiki = str(wiki_dir)
    try:
        qmd_run(
            [
                "collection",
                "add",
                abs_wiki,
                "--name",
                collection_name,
                "--mask",
                "**/*.md",
            ]
        )
        typer.echo(f"Registered QMD collection '{collection_name}' → {abs_wiki}")
    except RuntimeError as e:
        # Re-registering an existing collection is fine; surface the message but continue.
        typer.echo(f"qmd collection add: {e}")

    try:
        qmd_run(
            [
                "context",
                "add",
                f"qmd://{collection_name}",
                "Personal knowledge base wiki entries.",
            ]
        )
        typer.echo(f"Registered QMD context for qmd://{collection_name}")
    except RuntimeError as e:
        typer.echo(f"qmd context add: {e}")

    try:
        qmd_run(["embed"])
        typer.echo("Ran qmd embed.")
    except RuntimeError as e:
        typer.echo(f"qmd embed: {e}")
    typer.echo()

    # 4. Summary
    typer.echo("-" * 60)
    typer.echo("PATHS (absolute — use these exactly, do NOT use relative paths)")
    typer.echo("-" * 60)
    typer.echo(f"Archive root:  {archive_dir}/")
    typer.echo(f"Wiki:          {wiki_dir}/")
    typer.echo(f"Topics:        {topics_dir}/")
    typer.echo(f"Raw:           {raw_dir}/")
    typer.echo(f"Outputs:       {outputs_dir}/")
    typer.echo(f"Config:        {config_path}")
    typer.echo(f"State:         {state_path}")
    typer.echo(f"Work queue:    {work_path}")
    typer.echo(f"Index:         {index_path}")
    instructions_path = get_agent_instructions_path()
    if instructions_path.exists():
        typer.echo(f"Instructions:  {instructions_path}")
    typer.echo()
    typer.echo("ALL file creation MUST happen inside these directories.")
    typer.echo("NEVER create files in your own workspace or any other location.")
    typer.echo()

    typer.echo("=" * 60)
    typer.echo("ACTION REQUIRED")
    typer.echo("=" * 60)
    typer.echo("Setup complete. Next steps:")
    typer.echo("  - Add topics with `nexus archive topic new <slug> ...`")
    typer.echo("  - Ingest sources with `nexus archive add <path-or-url>`")
    typer.echo("  - Run `nexus archive onboard` at the start of each archivist session.")
    typer.echo("=" * 60)
