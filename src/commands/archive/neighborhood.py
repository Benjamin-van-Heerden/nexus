"""nexus archive neighborhood — multi-hop subgraph dump."""

import json as json_lib

import typer

from src.utils.archive import (
    compute_backlinks,
    compute_mentioned_by,
    compute_topic_siblings,
    doc_exists,
    load_doc,
)
from src.utils.paths import get_archive_dir

MAX_HOPS = 3


def _ensure_archive_initialized() -> None:
    if not get_archive_dir().is_dir():
        typer.echo("Archive directory does not exist. Run `nexus archive setup` first.")
        raise typer.Exit(1)


def _summary_first_line(summary: str) -> str:
    line = (summary or "").strip().splitlines()
    return line[0] if line else ""


def neighborhood(
    slug: str = typer.Argument(..., help="Doc slug at the center of the subgraph"),
    hops: int = typer.Option(1, "--hops", help=f"Hop radius (default 1, max {MAX_HOPS})"),
    siblings_per_topic: int = typer.Option(
        3, "--siblings-per-topic", help="Max sibling docs per topic to expand per hop"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON for agent consumption"),
):
    """Emit a multi-hop subgraph centered on the given doc."""
    _ensure_archive_initialized()

    if not doc_exists(slug):
        typer.echo(f"Error: doc '{slug}' does not exist.")
        raise typer.Exit(1)

    if hops < 0 or hops > MAX_HOPS:
        typer.echo(f"Error: --hops must be in [0, {MAX_HOPS}].")
        raise typer.Exit(1)

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def _add_node(node_slug: str, hop: int, via: str) -> None:
        if node_slug in nodes:
            return
        if not doc_exists(node_slug):
            nodes[node_slug] = {
                "slug": node_slug,
                "title": "",
                "summary": "",
                "hop": hop,
                "via": via,
                "missing": True,
            }
            return
        fm, _ = load_doc(node_slug)
        nodes[node_slug] = {
            "slug": node_slug,
            "title": fm.title,
            "summary": _summary_first_line(fm.summary),
            "topics": fm.topics,
            "hop": hop,
            "via": via,
        }

    _add_node(slug, hop=0, via="center")

    frontier: list[str] = [slug]
    for current_hop in range(hops):
        next_frontier: list[str] = []
        for src in frontier:
            if not doc_exists(src):
                continue
            fm, _ = load_doc(src)

            # Forward links
            for link in fm.links:
                edges.append({"from": src, "to": link.slug, "kind": "link", "relation": link.relation})
                if link.slug not in nodes:
                    _add_node(link.slug, hop=current_hop + 1, via=f"link from {src}")
                    next_frontier.append(link.slug)

            # Backlinks
            for backlink_src, relation in compute_backlinks(src):
                edges.append(
                    {"from": backlink_src, "to": src, "kind": "link", "relation": relation}
                )
                if backlink_src not in nodes:
                    _add_node(backlink_src, hop=current_hop + 1, via=f"backlink to {src}")
                    next_frontier.append(backlink_src)

            # Mentions (forward)
            for m in fm.mentions:
                edges.append({"from": src, "to": m, "kind": "mention"})
                if m not in nodes:
                    _add_node(m, hop=current_hop + 1, via=f"mention from {src}")
                    next_frontier.append(m)

            # Mentioned-by
            for mb in compute_mentioned_by(src):
                edges.append({"from": mb, "to": src, "kind": "mention"})
                if mb not in nodes:
                    _add_node(mb, hop=current_hop + 1, via=f"mention to {src}")
                    next_frontier.append(mb)

            # Topic siblings
            sibling_map = compute_topic_siblings(src, limit_per_topic=siblings_per_topic)
            for topic_slug, siblings in sibling_map.items():
                for sib in siblings:
                    edges.append(
                        {"from": src, "to": sib, "kind": "topic-sibling", "topic": topic_slug}
                    )
                    if sib not in nodes:
                        _add_node(sib, hop=current_hop + 1, via=f"sibling via {topic_slug}")
                        next_frontier.append(sib)

        frontier = next_frontier
        if not frontier:
            break

    out = {
        "center": slug,
        "hops": hops,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": edges,
    }

    if json_out:
        typer.echo(json_lib.dumps(out, indent=2))
        return

    typer.echo(f"Neighborhood of '{slug}' ({hops} hop(s)):")
    typer.echo(f"  nodes: {len(nodes)}")
    typer.echo(f"  edges: {len(edges)}")
    typer.echo()

    by_hop: dict[int, list[dict]] = {}
    for n in nodes.values():
        by_hop.setdefault(n["hop"], []).append(n)
    for hop in sorted(by_hop):
        typer.echo(f"hop {hop} ({len(by_hop[hop])}):")
        for n in by_hop[hop]:
            marker = "(missing)" if n.get("missing") else ""
            typer.echo(f"  {n['slug']} {marker}")
            if n.get("title"):
                typer.echo(f"      {n['title']}")
                if n.get("summary"):
                    typer.echo(f"      {n['summary']}")
                typer.echo(f"      via: {n['via']}")
        typer.echo()
