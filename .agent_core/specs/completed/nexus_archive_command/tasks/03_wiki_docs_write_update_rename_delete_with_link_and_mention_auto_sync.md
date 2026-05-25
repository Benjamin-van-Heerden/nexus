---
title: 'Wiki docs: write, update, rename, delete with link and mention auto-sync'
status: completed
created_at: '2026-04-17T14:02:25.391935'
updated_at: '2026-04-29T16:06:02.023744'
completed_at: '2026-04-29T16:06:02.023738'
---
Phase 3 of the implementation plan in spec.md. Implements the wiki doc lifecycle — the heart of the archive.

Files to create:

src/commands/archive/write.py — `nexus archive write <slug> --file <path>` command. The agent drafts a wiki doc (frontmatter + body) to a file; this command commits it.
1. Read the draft file via parse_frontmatter.
2. Validate frontmatter against DocFrontmatter model (required: slug, title, summary, status, topics non-empty list).
3. Verify the slug arg matches the frontmatter slug (sanity check).
4. Verify slug is unique (not already in wiki/) — fail with clear error if collision.
5. Verify each topic in `topics:` exists. With --strict-topics flag (default false), fail if any missing. Without it, warn and auto-create the missing topic with a placeholder summary ("Auto-created during write of <slug>. Please refine via `nexus archive topic update`.") and enqueue a `needs_topic_review` work item for the new topic.
6. Verify each `links[].slug` exists. For any missing, add to the doc's `broken_links:` field and enqueue a `broken_link` work item.
7. Extract mentions from body via extract_mentions(); replace doc's `mentions:` field with the result.
8. Set `created` and `updated` to now if not present; set `last_maintained` to now.
9. Write to wiki/<slug>.md atomically (temp file + rename).
10. Call sync_topic_membership() to update topic [[docs]] lists.
11. Call regenerate_index() (cheap).
12. Queue a QMD update marker (the actual qmd update command runs in phase 5; for now, just record it in state.toml as `pending_qmd_update: true` or similar — leave the actual subprocess call as a TODO for phase 5).
13. Print summary: slug, topics assigned, links validated, broken_links count, mentions extracted, ACTION REQUIRED next-step hint (e.g. "Doc written. To inspect: `nexus archive show <slug>`. To update topic hooks: TODO once topic.py supports it.").

src/commands/archive/doc.py — doc sub-app with these commands:

- `nexus archive doc update <slug> --file <path>` — same as `write` but enforces the doc already exists. Preserves `created`. Bumps `updated` and `last_maintained`. Re-runs all validation + auto-sync steps. Diffs old vs new topics, calls sync_topic_membership.

- `nexus archive doc rename <old-slug> <new-slug>` — atomic rename with full reference rewrite:
  1. Verify old exists, new doesn't.
  2. Move wiki/<old>.md to wiki/<new>.md.
  3. Update frontmatter slug field.
  4. Walk every wiki doc: in `links[]` entries with slug == old, update to new; in `mentions[]`, replace old with new; in body, replace `[[old]]` with `[[new]]`.
  5. Walk every topic: in [[docs]] entries with slug == old, update to new.
  6. Walk every output: in `cites[]` with slug == old, update to new.
  7. Append rename record to state.toml's `[[renames]]` list.
  8. Regenerate index.toml.
  9. Print summary of every file touched.
  Atomicity: do all the rewrites in memory first; only commit to disk at the end. If any step fails, abort with no changes.

- `nexus archive doc delete <slug>` — destructive but never silently drops data:
  1. Verify exists.
  2. Walk wiki: for every doc with `links[].slug == slug` or `mentions: contains slug` or body contains `[[slug]]`, strip the references AND set `broken_links:` on the affected doc to include the deleted slug AND enqueue a `broken_link` work item with detail "<deleted-slug> was deleted; <affected-doc-slug> referenced it".
  3. Walk topics: remove this slug from every topic's [[docs]] list.
  4. Walk outputs: outputs with `cites: contains slug` get a work item enqueued (kind=broken_link, slug=output-slug). Don't strip from cites — preserve historical record.
  5. Delete wiki/<slug>.md.
  6. Regenerate index.toml.
  7. Print summary: docs affected, work items enqueued.

- `nexus archive show <slug> [--body] [--json]` — display the doc. Default: frontmatter pretty-printed. With --body: include the markdown body. With --json: structured output. Sources field rendered as absolute paths.

src/commands/archive/link.py — link sub-app:

- `nexus archive link add <from-slug> <to-slug> --relation <r>` — append a LinkRef to from's `links:` (validate to exists; relation must be a valid enum value). Bump from's `updated`.

- `nexus archive link remove <from-slug> <to-slug>` — remove all matching link entries.

src/utils/archive.py additions:

- doc_exists(slug) -> bool
- list_all_doc_slugs() -> set[str]
- list_all_docs_with_frontmatter() -> Iterator[(slug, DocFrontmatter)] — used by walks.
- regenerate_index() -> None — walk wiki + topics, build IndexFile, write to archive/index.toml. Cheap enough to call after every mutation.
- enqueue_work(WorkItem) — append to work.toml.

Constraints:
- Atomic writes throughout (temp file + rename).
- All slug references are validated; no silent data loss.
- The actual `qmd update` subprocess invocation is deferred to phase 5 — for this phase, just mark state that an update is pending.
- The agent provides the frontmatter; the CLI validates and persists. Don't let the CLI write summaries or hooks itself.

Done criteria:
- A draft markdown file with valid frontmatter writes cleanly via `nexus archive write`.
- `nexus archive doc rename` rewrites all references atomically (verified by inspecting files after).
- `nexus archive doc delete` flags affected docs with `broken_links:` and enqueues work items.
- `nexus archive show <slug>` displays frontmatter; `--body` adds the body.
- `nexus archive link add A B --relation supersedes` updates A's frontmatter.

## Completion Notes

Implemented Phase 3: full wiki doc lifecycle with reference integrity.

Utils additions (src/utils/archive.py):
- doc_exists(slug), list_all_doc_slugs() -> set[str]
- list_all_docs_with_frontmatter() -> Iterator[(slug, DocFrontmatter, body)]
- list_all_outputs_with_frontmatter() -> Iterator[(slug, OutputFrontmatter, body)]
- mark_pending_qmd_update(): sets state.toml's pending_qmd_update flag (phase 5 turns it into an actual qmd update)

Commands (src/commands/archive/):

write.py — `nexus archive write <slug> --file <path> [--strict-topics]`:
- parse frontmatter; validate slug arg matches frontmatter slug and is kebab-case; reject duplicate
- inject defaults: created/updated default to today; last_maintained always set to today
- validate via DocFrontmatter pydantic model; reject empty topics
- topic resolution: missing topics fail with --strict-topics, otherwise auto-create with placeholder summary + enqueue needs_topic_review
- link resolution: each links[].slug verified; missing slugs added to broken_links + enqueue broken_link work item
- mentions auto-extracted from body, overwrites agent-supplied value
- save_doc -> sync_topic_membership -> regenerate_index -> mark_pending_qmd_update
- helpers (_read_draft, _validate_doc_frontmatter, _resolve_topics, _resolve_links, _ensure_archive_initialized) exported for reuse by doc update

doc.py — sub-app (update/rename/delete/show):
- update: enforces existence; preserves created from existing on disk; bumps updated/last_maintained; reuses write helpers; reports topics added/removed
- rename: in-memory plan, then batch commit. Rewrites the renamed doc's slug; every other doc's links[].slug, mentions[], body [[old]]->[[new]], broken_links; topic [[docs]] entries; output cites. Old file removed last. RenameRecord appended to state.toml.
- delete: walks wiki and strips links[], removes from mentions[], sets broken_links to include the deleted slug, enqueues broken_link work item per affected doc. Body prose preserved (historical record). Walks topics and removes from [[docs]]. Walks outputs — those that cite the deleted slug get broken_link enqueued; cites preserved per spec.
- show: human-readable frontmatter with absolute source paths via resolve_str; --body appends body; --json emits structured form

link.py — sub-app (add/remove):
- add: validates relation against LinkRelation Literal enum, both docs exist, no self-link, no exact (slug+relation) duplicate. Bumps from-doc's updated.
- remove: removes all matching link entries to the target (any relation).

Wiring (src/commands/archive/main.py): added write, doc sub-app, link sub-app.

Smoke tests verified end-to-end:
- Write with curated + broken link: doc persisted, broken_link work item enqueued, mentions auto-extracted from body, topic [[docs]] lists updated.
- Auto-create topic flow: write with brand-new topic in frontmatter, auto-creates topic with placeholder summary + enqueues needs_topic_review; --strict-topics correctly fails.
- Link add/remove: add new relation; duplicate (same slug+relation) is no-op; invalid relation rejected; self-link rejected; remove strips all relations to target.
- Doc update with topic shift: foundational-papers gained transformer-impl, ml-architectures lost it (sync_topic_membership reconciles correctly); broken_links cleared once link is valid.
- Rename attention-is-all-you-need -> attention-paper: file moved, transformer-impl's links[].slug, mentions[], body [[...]] all rewritten; both topic [[docs]] entries updated; RenameRecord appended to state.toml. Error paths: missing source, target already exists.
- Delete attention-paper while transformer-impl references it: links stripped, mentions cleared, broken_links updated to include the deleted slug, work item enqueued with descriptive detail, both topics' [[docs]] scrubbed, file removed; idempotent error on second delete.

Conventions:
- Atomic per-file writes (existing _atomic_write_text/_atomic_write_bytes).
- All paths displayed are absolute via resolve_str or get_doc_path.
- No QMD subprocess calls (deferred to phase 5; mark_pending_qmd_update flag instead).
- All imports at module top. Cross-module helpers imported with their underscore-prefixed names from write.py for now (acceptable internal reuse; could be promoted to a shared private module later).