---
title: 'Wiki docs: write, update, rename, delete with link and mention auto-sync'
status: todo
created_at: '2026-04-17T14:02:25.391935'
updated_at: '2026-04-17T14:02:25.391935'
completed_at: null
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