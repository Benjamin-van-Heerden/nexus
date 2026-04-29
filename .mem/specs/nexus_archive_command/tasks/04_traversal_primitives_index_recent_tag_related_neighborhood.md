---
title: 'Traversal primitives: index, recent, tag, related, neighborhood'
status: completed
created_at: '2026-04-17T14:02:51.963349'
updated_at: '2026-04-29T16:18:08.265360'
completed_at: '2026-04-29T16:18:08.265351'
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

## Completion Notes

Implemented Phase 4: structural-entry and traversal primitives.

Utils additions (src/utils/archive.py):
- compute_backlinks(target_slug) -> list[(source_slug, relation)]: walks docs, finds inbound links.
- compute_mentioned_by(target_slug) -> list[str]: walks docs, finds [[target]] in body or in mentions list.
- compute_topic_siblings(slug, limit_per_topic=5) -> dict[topic_slug, list[doc_slug]]: per-topic neighbour list excluding self.
- Enhanced regenerate_index(): now computes orphan_count (no topics OR zero inbound refs), stale_count (last_maintained older than archive.toml's staleness_days), broken_link_count (sum across docs), pending_outputs. Builds inbound-ref index in O(n).

Commands (src/commands/archive/):

index_cmd.py — `index [--regenerate] [--json]`:
- Default reads archive/index.toml; --regenerate rebuilds first.
- Human form prints counts + topics sorted by doc-count desc, with summary line, parent, children, related.

recent.py — `recent [--days N=7] [-n M=20] [--json]`:
- Walks wiki, filters updated >= today - days, sorts desc, caps at M. Per-doc: slug, title, first-line summary, topics, status, updated date.

tag.py — `tag <tag> [--json]`:
- Exact-match filter on tags[]. Output: slug, title, first-line summary, topics, all tags, status.

related.py — `related <slug> [--siblings-per-topic N=5] [--json]`:
- Five sections: forward links (with relation), backlinks (with inverse relation), mentions, mentioned-by, topic siblings (per topic, capped).
- Each item enriched with title + summary first line.
- Missing link/mention targets flagged with `(missing)` marker.

neighborhood.py — `neighborhood <slug> [--hops N=1, 0..3] [--siblings-per-topic N=3] [--json]`:
- BFS-style expansion through links, backlinks, mentions, mentioned-by, topic siblings.
- Returns {center, hops, node_count, edge_count, nodes: [{slug, title, summary, topics, hop, via}], edges: [{from, to, kind, relation/topic}]}.
- kind in {"link", "mention", "topic-sibling"}.
- Edges may include nodes already in the graph; node deduplication is by slug.

Wiring (src/commands/archive/main.py): added index, recent, tag, related, neighborhood as top-level archive commands.

Smoke tests verified end-to-end:
- Built a 3-topic / 3-doc graph (ml parent of nlp, cv; transformer/bert/vit with cross-doc links and mentions).
- `index` correctly reports 3 docs, 3 topics, 2 orphans (bert + vit have zero inbound refs); --regenerate rebuilds; --json emits structured form.
- `recent --days 1` returns all docs sorted by updated desc.
- `tag paper` returns 3 docs; `tag seminal` returns 1.
- `related transformer` correctly surfaces 2 backlinks (bert depends_on, vit extends), 2 mentioned-by, 2 topic siblings under nlp; --json includes full enrichment.
- `neighborhood --hops 0/1/2/3` work; --hops 5 rejected; missing slug rejected.
- Stale detection: aging a doc's last_maintained by 100 days bumps stale_count to 1.

Conventions:
- All commands are pure reads — no mutation, no QMD calls (deferred to phase 5).
- All paths displayed are absolute via existing path helpers.
- --json structured form available across all five commands.
- O(n) walks acceptable for v1; can cache later if needed.