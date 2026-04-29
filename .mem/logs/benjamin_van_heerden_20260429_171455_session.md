---
created_at: '2026-04-29T17:14:55.966601'
username: benjamin_van_heerden
spec_slug: nexus_archive_command
---
# Work Log - Phases 1-5 of nexus archive

## Overarching Goals

Build out the foundation through the QMD recall layer for `nexus archive`,
the file-first knowledge base / second brain. The session covered the first
five of the nine implementation phases laid out in spec.md: foundations,
topics, wiki docs, traversal, QMD wiring. By end of session the CLI exposes
12 archive subcommands and the data model + graph integrity rules are
solidly in place; what remains is ingestion (`add`), outputs, maintenance
scaffolding, and the onboard/agent-instructions surface.

## What Was Accomplished

### Phase 1 — Foundations

- Six pydantic models under `src/models/archive/`: `ArchiveConfig`/`ArchiveState`
  (with `MaintenanceConfig`, `QmdConfig`, `RenameRecord`), `DocFrontmatter`
  (with `LinkRef`, `Provenance`, status/relation `Literal` enums),
  `TopicConfig`/`TopicMember`, `OutputFrontmatter`, `WorkItem`/`WorkQueue`
  (kind enum), `IndexFile`/`IndexTopicEntry`.
- `src/utils/archive.py` (workhorse module): path getters, atomic TOML/YAML
  writers (temp file + rename), loaders/savers for every artifact,
  `parse_frontmatter` / `serialize_doc` (regex split + `yaml.safe_load` /
  `safe_dump`), `slugify` / `is_valid_slug` / `ensure_unique_slug`,
  `extract_mentions` (regex `[[slug]]`, first-seen ordering), `enqueue_work`,
  `qmd_check` / `qmd_run` subprocess wrappers with `QmdNotInstalledError`.
- `src/commands/archive/setup.py`: pause-check → create dirs → write
  defaults → qmd registration (`collection add` + `context add` + `embed`)
  → absolute PATHS + ACTION REQUIRED footer.
- Wiring: archive Typer app at `src/commands/archive/main.py`; root
  `main.py` registers archive_app.
- Pause integration: `archive: PauseEntry` added to `PauseConfig`; `Literal`
  type extended; `pause archive` and `pause resume archive` subcommands
  added.
- Added `pyyaml` (6.0.3) to project deps.

### Phase 2 — Topics CRUD + member auto-sync

- Utils: `topic_exists`, `list_all_topics`, `sync_topic_membership`
  (reconciles add/remove with hook preservation), `regenerate_index`
  (initial cut: walks topics + wiki, computes topic doc-counts +
  parent/related/children).
- `src/commands/archive/topic.py`: `topic new/update/delete/show`
  + `topics` listing function. `new` validates kebab slug + uniqueness +
  parent/related existence + rejects self-reference. `update` prints
  before/after diff for changed fields, no-op detection, `--parent ""`
  clears parent. `delete` walks wiki, strips topic from each affected
  doc's frontmatter, enqueues `needs_topic_review` per affected doc.
  `show` has `--json`. `topics --match` does case-insensitive substring
  filter on title/summary.

### Phase 3 — Wiki docs lifecycle

- Utils: `doc_exists`, `list_all_doc_slugs`, `list_all_docs_with_frontmatter`
  iterator, `list_all_outputs_with_frontmatter` iterator,
  `mark_pending_qmd_update`.
- `src/commands/archive/write.py`: `nexus archive write <slug> --file <path>`.
  Defaults `created`/`updated` to today; sets `last_maintained` on every
  write. Validates kebab slug + uniqueness, rejects empty topics,
  resolves topics (`--strict-topics` fails on missing; default mode
  auto-creates with placeholder summary + enqueues
  `needs_topic_review`). Resolves links: missing targets go to
  `broken_links` and enqueue `broken_link`. Mentions auto-extracted from
  body, overwrites agent value. Saves → `sync_topic_membership` →
  `regenerate_index` → marks pending qmd. Helpers (`_read_draft`,
  `_validate_doc_frontmatter`, `_resolve_topics`, `_resolve_links`,
  `_ensure_archive_initialized`) are reused by `doc update`.
- `src/commands/archive/doc.py`: `update` (preserves `created`,
  bumps `updated`/`last_maintained`, reports topics added/removed),
  `rename` (in-memory plan, batch commit; rewrites the doc's slug, every
  other doc's links/mentions/body `[[old]]→[[new]]`/broken_links, topic
  `[[docs]]` slugs, output cites; appends `RenameRecord` to state.toml),
  `delete` (strips links/mentions, sets broken_links to include the
  deleted slug, enqueues `broken_link` per affected doc; preserves body
  prose; scrubs topic membership; flags outputs that cite the deleted
  slug without dropping the cite), `show` (frontmatter pretty-print
  with absolute source paths via `resolve_str`; `--body` / `--json`).
- `src/commands/archive/link.py`: `add` (validates relation against
  the `LinkRelation` Literal, both docs exist, no self-link, no exact
  duplicate), `remove` (strips all link entries to the target).

### Phase 4 — Traversal primitives

- Utils: `compute_backlinks`, `compute_mentioned_by`,
  `compute_topic_siblings`. Enhanced `regenerate_index` to compute
  `orphan_count` (no topics OR zero inbound refs), `stale_count`
  (`last_maintained` older than `staleness_days`), `broken_link_count`
  (sum across docs), `pending_outputs` (count of `pending_review`
  outputs). Uses a single O(n) inbound-ref index pass.
- `index_cmd.py`: `index [--regenerate] [--json]`. Default reads
  index.toml; `--regenerate` rebuilds first. Pretty-prints counts +
  topics sorted by doc-count desc.
- `recent.py`: `recent [--days N=7] [-n M=20] [--json]`. Walks wiki,
  filters `updated >= today - days`, sorts desc.
- `tag.py`: `tag <tag> [--json]`. Exact match on `tags[]`.
- `related.py`: forward links + backlinks (with relations) + mentions
  + mentioned-by + topic siblings (per topic, capped). Each item enriched
  with title + summary first line; missing targets flagged.
- `neighborhood.py`: BFS subgraph dump. `--hops N=1, max 3`. Returns
  `{center, hops, node_count, edge_count, nodes, edges}` where edges
  carry `kind in {link, mention, topic-sibling}`.

### Phase 5 — QMD wiring + mutation hooks

- Utils: `qmd_search(q, n)` and `qmd_query(q, n)` (BM25 + vector +
  reranker, both wrap qmd subprocess + use `_qmd_unwrap_hits` to
  defensively coerce different qmd response envelopes — bare list,
  `{results}`, `{hits}`, `{data}`, None, unknown).
  `qmd_update_collection()` runs `qmd update --collections <name>`,
  stamps `state.toml.last_qmd_update`, clears `pending_qmd_update`.
  `qmd_path_to_slug(path)` defensively maps qmd hit paths to wiki slugs.
  `trigger_qmd_update_after_mutation(echo)` is the high-level wrapper:
  marks pending → runs update → on `QmdNotInstalledError` warns and
  leaves pending; on `RuntimeError` warns with stderr; mutation always
  succeeds.
- All mutation commands (write, doc update/rename/delete, link
  add/remove) now call `trigger_qmd_update_after_mutation(typer.echo)`
  after `regenerate_index()`. The phase-3 `mark_pending_qmd_update()`
  stub is replaced.
- `search.py`: raw qmd hits, no enrichment. Default N from
  `archive.toml.qmd.default_recall_n`. Exits 1 with install hint if
  qmd missing; `--json` passes qmd's output verbatim.
- `query.py`: two-pronged enriched view. For each hit, resolves path →
  slug, loads frontmatter, emits frontmatter-summary (slug/title/summary
  /topics/links with relations/tags/status). Computes union of topics
  across hits and emits topic breadcrumbs. Never returns doc bodies,
  raw qmd snippets, or LLM-synthesised prose. `--no-breadcrumbs`
  omits the topics section.

## Key Files Affected

Models (new directory):
- src/models/archive/archive.py
- src/models/archive/doc.py
- src/models/archive/topic.py
- src/models/archive/output.py
- src/models/archive/work.py
- src/models/archive/index.py

Commands (new directory):
- src/commands/archive/main.py (Typer wiring; updated multiple times)
- src/commands/archive/setup.py
- src/commands/archive/topic.py
- src/commands/archive/write.py
- src/commands/archive/doc.py
- src/commands/archive/link.py
- src/commands/archive/index_cmd.py
- src/commands/archive/recent.py
- src/commands/archive/tag.py
- src/commands/archive/related.py
- src/commands/archive/neighborhood.py
- src/commands/archive/search.py
- src/commands/archive/query.py

Utils + plumbing:
- src/utils/archive.py (new — extensive: I/O, frontmatter parsing,
  slug/mention helpers, qmd wrappers, graph computation primitives,
  `regenerate_index`).
- src/utils/paths.py (added `get_archive_dir`).
- src/utils/pause.py (extended Literal to include 'archive').
- src/models/pause.py (added `archive: PauseEntry`).
- src/commands/pause/main.py (added `pause archive` and resume support).
- main.py (registers archive_app).

Deps:
- pyproject.toml + uv.lock: added `pyyaml`.

## What Comes Next

Spec status: 5 of 9 phases complete. Remaining tasks (in suggested order):

1. **Ingestion: add command, raw storage, sidecar metadata** — implements
   `nexus archive add <path-or-url>`, hashes source, writes raw + sidecar,
   emits structured agent next-step instructions.
2. **Outputs: save, list, show, integrate, split, archive** — output
   sub-app with provenance tracking and work-queue integration.
3. **Maintenance & integrity: work, maintain, integrity, reindex** —
   surfaces the work queue in recommended order; integrity scan;
   reindex command.
4. **Onboard & agent_instructions.md** — `nexus archive onboard
   [--task ...]` and the full archivist behaviour spec.

End-to-end qmd integration verification (search returns hits, rename
re-indexes correctly, etc.) requires `qmd` to be installed. The wiring
is in place; once qmd is available those Done Criteria items can be
checked.

A small cosmetic item: doc.py imports underscore-prefixed helpers from
write.py (`_ensure_archive_initialized`, `_read_draft`, `_resolve_topics`,
`_resolve_links`, `_validate_doc_frontmatter`). Functional and idiomatic
internally, but could be promoted to a proper shared module
(`src/commands/archive/_helpers.py`) if the underscore-cross-module
import becomes a readability concern.
