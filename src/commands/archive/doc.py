"""nexus archive doc — update, rename, delete, show."""

import json as json_lib
import re
from datetime import date, datetime, timezone
from pathlib import Path

import typer

from src.models.archive.archive import RenameRecord
from src.models.archive.doc import DocFrontmatter
from src.models.archive.work import WorkItem
from src.utils.archive import (
    doc_exists,
    enqueue_work,
    extract_mentions,
    get_doc_path,
    is_valid_slug,
    list_all_docs_with_frontmatter,
    list_all_outputs_with_frontmatter,
    list_all_topics,
    load_archive_state,
    load_doc,
    trigger_qmd_update_after_mutation,
    regenerate_index,
    save_archive_state,
    save_doc,
    save_output,
    save_topic,
    sync_topic_membership,
)
from src.commands.archive.write import (
    _ensure_archive_initialized,
    _read_draft,
    _resolve_links,
    _resolve_topics,
    _validate_doc_frontmatter,
)
from src.utils.path_resolution import resolve_str

app = typer.Typer(help="Manage wiki docs")


@app.command("update")
def update(
    slug: str = typer.Argument(..., help="Doc slug (must match frontmatter slug)"),
    file: Path = typer.Option(..., "--file", "-f", help="Path to the updated draft"),
    strict_topics: bool = typer.Option(
        False,
        "--strict-topics",
        help="Fail if any topic in frontmatter doesn't exist (default: auto-create)",
    ),
):
    """Update an existing wiki doc. Preserves `created`; bumps `updated` and `last_maintained`."""
    _ensure_archive_initialized()

    if not doc_exists(slug):
        typer.echo(f"Error: doc '{slug}' does not exist. Use `nexus archive write` to create it.")
        raise typer.Exit(1)

    existing_fm, _ = load_doc(slug)
    fm_dict, body = _read_draft(file)

    # Preserve created from existing; force updated/last_maintained to today.
    today = date.today().isoformat()
    fm_dict["created"] = existing_fm.created.isoformat()
    fm_dict["updated"] = today
    fm_dict["last_maintained"] = today

    fm = _validate_doc_frontmatter(fm_dict, slug)
    auto_created = _resolve_topics(fm, strict_topics)
    broken = _resolve_links(fm)
    fm.mentions = extract_mentions(body)

    save_doc(fm, body)
    sync_topic_membership(
        fm.slug,
        new_topics=fm.topics,
        old_topics=existing_fm.topics,
    )
    regenerate_index()
    trigger_qmd_update_after_mutation(typer.echo)

    added = sorted(set(fm.topics) - set(existing_fm.topics))
    removed = sorted(set(existing_fm.topics) - set(fm.topics))

    typer.echo(f"Updated doc '{slug}'.")
    typer.echo(f"  Path: {get_doc_path(slug)}")
    if added:
        typer.echo(f"  Topics added: {', '.join(added)}")
    if removed:
        typer.echo(f"  Topics removed: {', '.join(removed)}")
    if auto_created:
        typer.echo(f"  Auto-created topics: {', '.join(auto_created)}")
    typer.echo(f"  Links: {len(fm.links)} curated, {len(broken)} broken")
    if broken:
        typer.echo(f"    broken: {', '.join(broken)}")
    typer.echo(f"  Mentions: {len(fm.mentions)} extracted")


@app.command("rename")
def rename(
    old_slug: str = typer.Argument(..., help="Existing slug"),
    new_slug: str = typer.Argument(..., help="New slug"),
):
    """Atomically rename a doc and rewrite every reference across the archive."""
    _ensure_archive_initialized()

    if not doc_exists(old_slug):
        typer.echo(f"Error: doc '{old_slug}' does not exist.")
        raise typer.Exit(1)
    if not is_valid_slug(new_slug):
        typer.echo(f"Error: '{new_slug}' is not a valid kebab-case slug.")
        raise typer.Exit(1)
    if doc_exists(new_slug):
        typer.echo(f"Error: doc '{new_slug}' already exists.")
        raise typer.Exit(1)
    if old_slug == new_slug:
        typer.echo("Error: old and new slugs are identical.")
        raise typer.Exit(1)

    body_pattern = re.compile(r"\[\[" + re.escape(old_slug) + r"\]\]")

    # Plan all writes in memory; commit at the end.
    doc_writes: list[tuple[DocFrontmatter, str]] = []
    topic_updates: list[str] = []  # slugs of topics to re-save
    output_updates: list[str] = []  # slugs of outputs to re-save

    # Load topics/outputs upfront so we can update them in memory.
    topics_index = {t.slug: t for t in list_all_topics()}
    outputs_pending: dict[str, tuple] = {}

    for slug, fm, body in list_all_docs_with_frontmatter():
        modified = False

        # Renaming the doc itself
        if slug == old_slug:
            fm.slug = new_slug
            modified = True

        # Update links pointing to old_slug
        new_links = []
        for link in fm.links:
            if link.slug == old_slug:
                link.slug = new_slug
                modified = True
            new_links.append(link)
        fm.links = new_links

        # Update mentions list (will also be regenerated from body below)
        if old_slug in fm.mentions:
            fm.mentions = [new_slug if m == old_slug else m for m in fm.mentions]
            modified = True

        # Update body [[old_slug]] -> [[new_slug]]
        new_body, n_subs = body_pattern.subn(f"[[{new_slug}]]", body)
        if n_subs > 0:
            body = new_body
            modified = True

        # Update broken_links (some other doc may have flagged old_slug as broken)
        if old_slug in fm.broken_links:
            fm.broken_links = sorted(
                {(new_slug if x == old_slug else x) for x in fm.broken_links}
            )
            modified = True

        if modified:
            doc_writes.append((fm, body))

    # Update topic [[docs]] entries
    for topic in topics_index.values():
        modified = False
        for member in topic.docs:
            if member.slug == old_slug:
                member.slug = new_slug
                modified = True
        if modified:
            topic_updates.append(topic.slug)

    # Update output cites
    for slug, fm, body in list_all_outputs_with_frontmatter():
        if old_slug in fm.cites:
            fm.cites = [new_slug if c == old_slug else c for c in fm.cites]
            outputs_pending[slug] = (fm, body)
            output_updates.append(slug)

    # Commit phase: save all updated docs to the new slug name (the renamed
    # doc gets written under new_slug; the old file is removed at the end).
    for fm, body in doc_writes:
        save_doc(fm, body)
    for topic_slug in topic_updates:
        save_topic(topics_index[topic_slug])
    for slug in output_updates:
        fm, body = outputs_pending[slug]
        save_output(fm, body)

    # Remove the old wiki file (the renamed doc was saved under new_slug above)
    old_path = get_doc_path(old_slug)
    if old_path.exists():
        old_path.unlink()

    # Append rename record to state
    state = load_archive_state()
    state.renames.append(
        RenameRecord(old=old_slug, new=new_slug, at=datetime.now(timezone.utc))
    )
    save_archive_state(state)

    regenerate_index()
    trigger_qmd_update_after_mutation(typer.echo)

    typer.echo(f"Renamed '{old_slug}' → '{new_slug}'.")
    typer.echo(f"  Docs touched: {len(doc_writes)}")
    typer.echo(f"  Topics touched: {len(topic_updates)}")
    typer.echo(f"  Outputs touched: {len(output_updates)}")
    typer.echo(f"  New path: {get_doc_path(new_slug)}")


@app.command("delete")
def delete(
    slug: str = typer.Argument(..., help="Doc slug to delete"),
):
    """Delete a doc. Affected references are stripped and broken_link work items are enqueued."""
    _ensure_archive_initialized()

    if not doc_exists(slug):
        typer.echo(f"Error: doc '{slug}' does not exist.")
        raise typer.Exit(1)

    body_pattern = re.compile(r"\[\[" + re.escape(slug) + r"\]\]")
    affected_docs: list[str] = []
    affected_outputs: list[str] = []

    for other_slug, fm, body in list_all_docs_with_frontmatter():
        if other_slug == slug:
            continue
        modified = False

        new_links = [link for link in fm.links if link.slug != slug]
        if len(new_links) != len(fm.links):
            fm.links = new_links
            modified = True

        if slug in fm.mentions:
            fm.mentions = [m for m in fm.mentions if m != slug]
            modified = True

        body_has_mention = body_pattern.search(body) is not None

        if modified or body_has_mention:
            if slug not in fm.broken_links:
                fm.broken_links = sorted({*fm.broken_links, slug})
            save_doc(fm, body)
            enqueue_work(
                WorkItem(
                    kind="broken_link",
                    slug=other_slug,
                    detail=f"'{slug}' was deleted; '{other_slug}' referenced it",
                    created=datetime.now(timezone.utc),
                )
            )
            affected_docs.append(other_slug)

    # Walk topics: remove the deleted slug from every topic's [[docs]] list
    for topic in list_all_topics():
        before = len(topic.docs)
        topic.docs = [d for d in topic.docs if d.slug != slug]
        if len(topic.docs) != before:
            save_topic(topic)

    # Walk outputs: outputs that cite this slug get a work item.
    # Preserve cites (historical record) per spec.
    for output_slug, fm, _body in list_all_outputs_with_frontmatter():
        if slug in fm.cites:
            enqueue_work(
                WorkItem(
                    kind="broken_link",
                    slug=output_slug,
                    detail=f"output cites deleted doc '{slug}'",
                    created=datetime.now(timezone.utc),
                )
            )
            affected_outputs.append(output_slug)

    get_doc_path(slug).unlink()
    regenerate_index()
    trigger_qmd_update_after_mutation(typer.echo)

    typer.echo(f"Deleted doc '{slug}'.")
    typer.echo(f"  Docs flagged with broken_links: {len(affected_docs)}")
    if affected_docs:
        for d in affected_docs:
            typer.echo(f"    - {d}")
    typer.echo(f"  Outputs flagged: {len(affected_outputs)}")
    if affected_outputs:
        for o in affected_outputs:
            typer.echo(f"    - {o}")


@app.command("show")
def show(
    slug: str = typer.Argument(..., help="Doc slug"),
    body: bool = typer.Option(False, "--body", help="Include the markdown body"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Display a doc's frontmatter (and optionally body)."""
    _ensure_archive_initialized()

    if not doc_exists(slug):
        typer.echo(f"Error: doc '{slug}' does not exist.")
        raise typer.Exit(1)

    fm, doc_body = load_doc(slug)
    fm_dump = fm.model_dump(mode="json", exclude_none=True)
    fm_dump["sources"] = [resolve_str(s) for s in fm.sources]

    if json_out:
        out = {"frontmatter": fm_dump, "path": str(get_doc_path(slug))}
        if body:
            out["body"] = doc_body
        typer.echo(json_lib.dumps(out, indent=2))
        return

    typer.echo(f"slug:    {fm.slug}")
    typer.echo(f"title:   {fm.title}")
    typer.echo(f"status:  {fm.status}")
    typer.echo(f"created: {fm.created}")
    typer.echo(f"updated: {fm.updated}")
    typer.echo(f"last_maintained: {fm.last_maintained or '(never)'}")
    typer.echo(f"path:    {get_doc_path(slug)}")
    typer.echo()
    typer.echo("summary:")
    for line in fm.summary.splitlines():
        typer.echo(f"  {line}")
    typer.echo()
    typer.echo(f"topics: {', '.join(fm.topics) if fm.topics else '(none)'}")
    typer.echo(f"tags:   {', '.join(fm.tags) if fm.tags else '(none)'}")
    typer.echo()
    typer.echo(f"links ({len(fm.links)}):")
    for link in fm.links:
        typer.echo(f"  - {link.slug} [{link.relation}]")
    typer.echo(f"mentions: {', '.join(fm.mentions) if fm.mentions else '(none)'}")
    typer.echo(f"broken_links: {', '.join(fm.broken_links) if fm.broken_links else '(none)'}")
    typer.echo()
    typer.echo("sources:")
    if fm.sources:
        for s in fm.sources:
            typer.echo(f"  - {resolve_str(s)}")
    else:
        typer.echo("  (none)")
    typer.echo()
    typer.echo(f"provenance: ingested_from={fm.provenance.ingested_from}, "
               f"origin_outputs={fm.provenance.origin_outputs}")

    if body:
        typer.echo()
        typer.echo("-" * 60)
        typer.echo("BODY")
        typer.echo("-" * 60)
        typer.echo(doc_body)
