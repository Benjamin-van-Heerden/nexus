"""nexus archive add — stage raw source material for archivist ingestion."""

import tomllib
from pathlib import Path
from urllib.parse import urlparse

import typer

from src.utils.archive import (
    QmdNotInstalledError,
    doc_exists,
    extract_excerpt,
    fetch_url_to_temp,
    find_candidate_topics_by_keywords,
    get_raw_sidecar_path,
    hash_file,
    load_archive_config,
    load_doc,
    qmd_path_to_slug,
    qmd_query,
    read_first_h1,
    save_raw,
    slugify,
)
from src.utils.paths import get_archive_dir

_MARKDOWN_SOURCE_ERROR = (
    "Only markdown sources supported for v1; PDFs/HTML belong in raw/unprocessed/ "
    "(future spec)."
)


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _resolve_source(path_or_url: str) -> tuple[Path, bool]:
    if _is_url(path_or_url):
        try:
            return fetch_url_to_temp(path_or_url), True
        except Exception as e:
            typer.echo(f"Error: {e}")
            raise typer.Exit(1)

    source_path = Path(path_or_url).expanduser()
    if not source_path.is_file():
        typer.echo(f"Error: source file not found: {source_path}")
        raise typer.Exit(1)
    if source_path.suffix.lower() != ".md":
        typer.echo(f"Error: {_MARKDOWN_SOURCE_ERROR}")
        raise typer.Exit(1)
    return source_path.resolve(), False


def _load_sidecar(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _first_paragraph(markdown_text: str) -> str:
    paragraphs = [p.strip() for p in markdown_text.split("\n\n") if p.strip()]
    return paragraphs[0] if paragraphs else ""


def _score(hit: dict) -> str:
    for key in ("score", "rerank_score", "similarity"):
        if key in hit:
            return str(hit[key])
    return "n/a"


def _recall_hits(query_text: str) -> tuple[list[dict], str | None]:
    if not query_text.strip():
        return [], None

    n = min(5, load_archive_config().qmd.default_recall_n)
    try:
        hits = qmd_query(query_text, n)
    except QmdNotInstalledError:
        return [], "qmd is not installed; recall skipped."
    except RuntimeError as e:
        return [], f"qmd query failed; recall skipped: {e}"

    out: list[dict] = []
    seen: set[str] = set()
    for hit in hits:
        slug = qmd_path_to_slug(hit.get("path") or hit.get("file"))
        if slug is None or slug in seen or not doc_exists(slug):
            continue
        try:
            fm, _body = load_doc(slug)
        except Exception:
            continue
        out.append(
            {
                "slug": slug,
                "summary": fm.summary,
                "score": _score(hit),
            }
        )
        seen.add(slug)
        if len(out) >= 5:
            break
    return out, None


def _suggest_slug(title_guess: str, source: str, content_hash: str) -> str:
    if title_guess:
        candidate = slugify(title_guess)
        if candidate:
            return candidate

    parsed = urlparse(source)
    fallback = Path(parsed.path if parsed.scheme else source).stem
    candidate = slugify(fallback)
    return candidate or f"raw-{content_hash}"


def add(
    path_or_url: str = typer.Argument(..., help="Local .md path or http(s) markdown URL"),
):
    """Stage a markdown source in archive/raw and print archivist next steps."""
    _ensure_archive_initialized()

    source_path, is_temp = _resolve_source(path_or_url)
    try:
        content_hash = hash_file(source_path)
        existing_sidecar = get_raw_sidecar_path(content_hash)
        duplicate_metadata = _load_sidecar(existing_sidecar)

        raw_path, sidecar_path = save_raw(
            source_path,
            content_hash,
            original_path=path_or_url,
        )
        markdown_text = raw_path.read_text(encoding="utf-8", errors="replace")
    finally:
        if is_temp:
            source_path.unlink(missing_ok=True)

    title_guess = read_first_h1(markdown_text) or ""
    query_text = extract_excerpt(markdown_text, word_count=500)
    recall_hits, recall_warning = _recall_hits(query_text)

    topic_hint_text = f"{title_guess}\n\n{_first_paragraph(markdown_text)}"
    candidate_topics = find_candidate_topics_by_keywords(topic_hint_text)[:5]
    suggested_slug = _suggest_slug(title_guess, path_or_url, content_hash)

    typer.echo("Source ingested.")
    typer.echo(f"  hash: {content_hash}")
    typer.echo(f"  raw file: {raw_path}")
    typer.echo(f"  sidecar: {sidecar_path}")
    typer.echo(f"  title guess: {title_guess or '(none)'}")
    typer.echo()

    if duplicate_metadata:
        typer.echo("Duplicate warning:")
        typer.echo(f"  raw hash already existed: {content_hash}")
        original_path = duplicate_metadata.get("original_path", "(unknown)")
        typer.echo(f"  previous original_path: {original_path}")
        typer.echo(f"  previous fetched_at: {duplicate_metadata.get('fetched_at', '(unknown)')}")
        typer.echo("  The raw file and sidecar were refreshed; confirm whether to proceed.")
        typer.echo()

    typer.echo("QMD recall — similar existing docs:")
    if recall_warning:
        typer.echo(f"  {recall_warning}")
    elif not recall_hits:
        typer.echo("  (none)")
    else:
        for hit in recall_hits:
            summary_line = hit["summary"].strip().splitlines()[0] if hit["summary"] else ""
            summary = summary_line or "(no summary)"
            typer.echo(f"  {hit['slug']} — {summary} (score: {hit['score']})")
    typer.echo()

    typer.echo("Candidate topics (keyword match):")
    if not candidate_topics:
        typer.echo("  (none)")
    else:
        for topic in candidate_topics:
            summary_line = topic.summary.strip().splitlines()[0] if topic.summary else ""
            typer.echo(f"  {topic.slug} — {summary_line or '(no summary)'}")
    typer.echo()

    typer.echo("ACTION REQUIRED:")
    typer.echo(f"  1. Read the raw file: {raw_path}")
    typer.echo("  2. Decide:")
    typer.echo("     a) New doc → draft frontmatter + body to a temp file, then run:")
    typer.echo(f"        nexus archive write {suggested_slug} --file <temp-file>")
    typer.echo("     b) Augment existing doc → run:")
    typer.echo("        nexus archive doc update <existing-slug> --file <temp-file>")
    typer.echo("     c) Already-known content (duplicate or trivially redundant) → no action;")
    typer.echo("        the raw stays as a record.")
    typer.echo(f"  3. Suggested slug: {suggested_slug}")
    typer.echo(
        "  4. Use the QMD recall and candidate topics above to inform link and "
        "topic assignments."
    )
