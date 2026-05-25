---
title: 'Maintenance and integrity: work, maintain, integrity, reindex'
status: completed
created_at: '2026-04-17T14:05:00.778441'
updated_at: '2026-05-05T10:42:25.772384'
completed_at: '2026-05-05T10:42:25.772377'
---
Phase 8 of the implementation plan in spec.md. Implements the maintenance scaffolding — surfacing pending work, scanning integrity, and rebuilding caches.

Files to create:

src/commands/archive/work.py — `nexus archive work list [--kind <kind>] [--json]`:
- Shows the current work queue. Combines:
  - Persisted items from work.toml (broken_link, pending_output, contradiction, needs_topic_review).
  - Computed items (orphan, stale) — derived on the fly from disk:
    - orphan: doc with empty `topics:` OR zero inbound refs (no other doc has it in `links` or `mentions`).
    - stale: doc whose `last_maintained` is older than archive.toml's maintenance.staleness_days.
- --kind filters to one kind.
- Output: grouped by kind, each item: kind, slug, detail (if persisted), created (if persisted) or computed-now.

src/commands/archive/integrity.py — `nexus archive integrity [--json]`:
- One-shot integrity scan. Walks every wiki doc, every topic, every output frontmatter:
  - For each `links[].slug`, verify the target wiki doc exists. If not, enqueue `broken_link` (if not already present) and add to the source doc's `broken_links:` field.
  - For each `topics[]` in a doc, verify the topic exists. If not, enqueue `needs_topic_review` for the doc.
  - For each `mentions[]`, verify the target exists. If not, log a warning (don't enqueue — mentions are softer than links).
  - For each topic's [[docs]] entry, verify the doc exists; if not, remove the orphan member entry and rewrite the topic file.
  - For each output's `cites[]`, verify the cited doc exists; if not, enqueue `broken_link` for the output.
- Output: summary report (counts per kind), and a list of the new work items enqueued by this run.
- This is the catch-up command — run it periodically or after manual file edits to make sure the queue reflects reality.

src/commands/archive/reindex.py — `nexus archive reindex`:
- Calls regenerate_index() (rebuild archive/index.toml from disk).
- Calls qmd_update_collection() (force a QMD update of the nexus-archive collection).
- Updates state.toml's last_reindex and last_qmd_update.
- Prints summary: docs walked, topics walked, QMD update status, durations.

src/commands/archive/maintain.py — `nexus archive maintain [--task <output_triage|broken_links|orphans|stale|topic_summaries|contradictions>] [--limit N]`:
- This is the archivist's session entry point. It does NOT do any work itself — it surfaces the queue in recommended order and prints next-step instructions for each item.
- Default order (per spec's "five jobs" — actually six with broken-link resolution):
  1. Output triage (pending_review outputs)
  2. Broken-link resolution
  3. Orphan rescue
  4. Stale doc review (oldest first; up to maintenance.batch_size from archive.toml, overridable via --limit)
  5. Topic summary refresh (topics whose member list changed since their last_maintained)
  6. Contradiction scan (run a QMD-based pass: for each recently-updated doc, qmd_query its summary; if a top hit's content seems contradictory by topic overlap, enqueue contradiction — for v1, this is best-effort and may just suggest the agent run a manual scan).
- --task filters to a single job.
- --limit caps the items shown per job.
- For each surfaced item, print:
  - The kind, slug, and any detail.
  - The recommended action (e.g. for broken_link: "Decide: repoint to a different doc with `nexus archive link add`/remove, or accept by removing from broken_links via `nexus archive doc update`").
  - The exact CLI commands the agent would run.
- ACTION REQUIRED footer: "Work through these in order. After each resolution, re-run `nexus archive work list` to see what's left."

src/utils/archive.py additions:

- compute_orphans() -> list[str] — slugs of docs with no topics or zero inbound refs.
- compute_stales(staleness_days) -> list[str] — slugs whose last_maintained is older than the threshold.
- compute_contradictions() -> list[(slug_a, slug_b)] — best-effort: for each recently-updated doc (last 30 days), qmd_query its summary; for each top hit with overlapping topics, flag as a candidate pair. v1 may just return an empty list and surface "manual scan recommended" — implement minimally.
- get_topic_member_freshness(topic_slug) -> bool — returns True if topic's [[docs]] list has changed since its last_maintained.

Constraints:
- maintain never mutates state — it only surfaces and instructs. The agent does the actual mutations via the targeted commands.
- integrity is the only command that mutates as a side effect of scanning (it strips orphan topic members and adds broken_link flags). This is OK because integrity restores invariants the CLI is supposed to maintain anyway — drift is a bug, integrity is the corrective sweep.
- All printed paths absolute.

Done criteria:
- `uv run nexus archive work list` shows persisted + computed items, grouped by kind.
- `uv run nexus archive integrity` runs cleanly on a healthy archive (no new items); on a manually-corrupted archive (e.g. delete a topic file by hand), it detects the orphan members and enqueues fixes.
- `uv run nexus archive reindex` rebuilds index.toml and triggers qmd update.
- `uv run nexus archive maintain` surfaces the work queue in the documented order with actionable next-step instructions.

## Completion Notes

Implemented archive maintenance and integrity commands. Added work list command combining persisted work.toml items with computed orphan and stale items, with kind filtering and JSON output. Added maintain command as read-only archivist scaffold in recommended order: output triage, broken links, orphans, stale docs, topic summaries, contradictions, with concrete next-step commands per item. Added integrity scan that detects missing link targets, missing topics, missing mentions, orphan topic members, and broken output cites; it enqueues persisted work items, adds broken_links to docs, strips invalid topic members, and regenerates the index. Added reindex command that regenerates index.toml, updates state.last_reindex, refreshes QMD, and reports timings/status. Added reusable utilities compute_orphans, compute_stales, compute_contradictions minimal v1, and get_topic_member_freshness. Wired all commands into archive main. Verified healthy archive behavior and a controlled corrupted fixture, including work queue surfacing, integrity repair/enqueueing, maintain recommendations, reindex, and cleanup. Final py_compile passed.