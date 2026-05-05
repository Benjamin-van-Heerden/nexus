"""nexus archive reindex — rebuild index.toml and refresh QMD."""

from datetime import datetime, timezone
from time import perf_counter

import typer

from src.utils.archive import (
    QmdNotInstalledError,
    load_archive_state,
    qmd_update_collection,
    regenerate_index,
    save_archive_state,
)
from src.utils.paths import get_archive_dir


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def reindex():
    """Regenerate archive/index.toml and update the QMD collection."""
    _ensure_archive_initialized()

    start = perf_counter()
    index = regenerate_index()
    index_duration = perf_counter() - start

    state = load_archive_state()
    state.last_reindex = datetime.now(timezone.utc)
    save_archive_state(state)

    qmd_status = "ok"
    qmd_start = perf_counter()
    try:
        qmd_update_collection()
    except QmdNotInstalledError:
        qmd_status = "qmd is not installed; skipped"
    except RuntimeError as e:
        qmd_status = f"failed: {e}"
    qmd_duration = perf_counter() - qmd_start

    typer.echo("Archive reindex complete.")
    typer.echo(f"  Docs walked:   {index.doc_count}")
    typer.echo(f"  Topics walked: {index.topic_count}")
    typer.echo(f"  Index time:    {index_duration:.2f}s")
    typer.echo(f"  QMD status:    {qmd_status}")
    typer.echo(f"  QMD time:      {qmd_duration:.2f}s")
