---
title: 'Traversal primitives: index, recent, tag, related, neighborhood'
status: todo
created_at: '2026-04-17T14:02:51.963349'
updated_at: '2026-04-17T14:02:51.963349'
completed_at: null
---
Phase 4 of the implementation plan in spec.md. Implements the structural-entry and traversal primitives the librarian uses to walk the archive.

Files to create:

src/commands/archive/index_cmd.py — `nexus archive index [--regenerate] [--json]`:
- Default: read archive/index.toml and pretty-print (top-level counts + each topic with summary_line, doc_count, parent, related, children).
- --regenerate: walk wiki + topics on disk, rebuild IndexFile, write to archive/index.toml, print "regenerated".
- --json: structured output for agent consumption.
- This is the librarian's entry point for systematic traversal.

src/commands/archive/recent.py — `nexus archive recent [--days N] [-n M] [--json]`:
- Walk wiki frontmatter, sort by `updated` desc.
- --days filters to docs updated within N days (default 7).
- -n caps results (default 20).
- Output per doc: slug, title, summary (first line), topics, updated date.
- Temporal entry point.

src/commands/archive/tag.py — `nexus archive tag <tag> [--json]`:
- Walk wiki, return docs whose `tags:` contains the given tag.
- Output per doc: slug, title, summary (first line), topics, all tags.

src/commands/archive/related.py — `nexus archive related <slug> [--json]`:
- For the given slug, return:
  - Forward links: docs in this doc's `links:` field, with relation type.
  - Backlinks: docs that have this slug in their `links:` field, with the inverse relation labelled.
  - Mentions: from this doc's `mentions:` field.
  - Mentioned-by: docs whose body contains [[<slug>]] (computed by walking).
  - Topic siblings: for each topic this doc belongs to, list up to N other member docs (configurable, default 5 per topic).
- Each result item shows slug + title + summary first line.

src/commands/archive/neighborhood.py — `nexus archive neighborhood <slug> [--hops N] [--json]`:
- Single-call subgraph dump centered on `slug`.
- Default --hops 1; max 3.
- Walk: links, mentions, topic-siblings; for each found doc at hop k, recurse to hop k+1 if k < hops.
- Return as a structured blob: { center: <slug>, nodes: [{slug, title, summary, hop, via}], edges: [{from, to, kind}] } where kind is "link"|"mention"|"topic-sibling" and via explains why this node was included.
- Designed to save the agent N×K calls when it wants breadth.

src/utils/archive.py additions:

- compute_backlinks(target_slug) -> list[(source_slug, relation)] — walk all docs, find inbound links.
- compute_mentioned_by(target_slug) -> list[str] — walk all docs, scan for [[target_slug]] in body or mentions.
- compute_topic_siblings(slug, limit_per_topic=5) -> dict[topic_slug, list[doc_slug]].
- regenerate_index() — already added in phase 3; ensure it computes orphan_count (docs with no topics OR zero inbound refs) and stale_count (docs with last_maintained older than archive.toml's staleness_days) and broken_link_count (sum of len(broken_links) across docs) and pending_outputs (count of outputs with status=pending_review).

Constraints:
- All commands are pure reads — no mutation, no QMD calls.
- All output uses absolute paths (resolve_str) when paths appear (e.g. sources field in show).
- --json output is the structured form used by other agents; default output is human-readable.
- Walks are O(n) over docs; acceptable for v1 (cache later if needed).

Done criteria:
- `uv run nexus archive index` prints the index. `--regenerate` rebuilds it.
- `uv run nexus archive recent --days 30` lists recent docs.
- `uv run nexus archive tag paper` returns paper-tagged docs.
- `uv run nexus archive related <slug>` shows forward + backward + mention + sibling neighbours.
- `uv run nexus archive neighborhood <slug> --hops 2` returns a 2-hop subgraph blob.