---
title: 'Topics: CRUD commands and member auto-sync'
status: completed
created_at: '2026-04-17T14:01:44.779769'
updated_at: '2026-04-29T15:52:26.958594'
completed_at: '2026-04-29T15:52:26.958588'
---
Phase 2 of the implementation plan in spec.md. Implements topic management — the organising overlay for the wiki.

Files to create:

src/commands/archive/topic.py — topic sub-app with these commands:

- `nexus archive topic new <slug> --title <t> --summary <s> [--parent <slug>] [--related <slug>,<slug>...]` — create topic. Validate slug uniqueness, validate parent exists if provided, validate each related topic exists. Write topics/<slug>.toml with empty docs list. Set created/updated/last_maintained to now. Print confirmation + ACTION REQUIRED next-step hint (e.g. "Topic created. Add docs by setting `topics: [<slug>, ...]` in their frontmatter when you write or update them.").

- `nexus archive topic update <slug> [--title <t>] [--summary <s>] [--parent <slug>] [--related <slugs>]` — update fields. Validate parent/related exist. Bump updated. Print before/after diff for changed fields.

- `nexus archive topic delete <slug>` — destructive. Walk all wiki docs, remove this topic from their `topics:` lists; for each affected doc, enqueue a `needs_topic_review` work item. Remove the topic file. Regenerate index.toml. Print summary: docs affected count, work items enqueued.

- `nexus archive topic <slug>` — show a topic: title, summary, parent, related, member docs (slug + hook). JSON via --json. This is a read primitive used during traversal.

- `nexus archive topics [--match <q>]` — list all topics. With --match, filter by case-insensitive substring match against title or summary (NOT QMD; this is structural keyword entry, distinct from query/search).

src/utils/archive.py additions — implement:

- topic_exists(slug) -> bool
- list_all_topics() -> list[TopicConfig]
- sync_topic_membership(doc_slug, new_topics: list[str], old_topics: list[str]) — call this after a doc write/update/delete. For each topic in (new - old), add the doc to the topic's [[docs]] list (with empty hook unless the agent provides one separately). For each topic in (old - new), remove the doc from the topic's [[docs]] list. Preserve existing hook values on no-op topics.
- get_or_create_topic_member_hook(topic_slug, doc_slug) — helper for membership sync; returns existing hook or empty string.

Hook handling:
- Hooks are *per-membership*, not per-doc. They live in the topic's [[docs]] entries.
- This task does NOT add a CLI command for setting hooks — that's part of the wiki doc write flow (next task) where the agent can pass `--hook "<text>"` per-topic or via frontmatter extension. For this task, hooks default to empty string when topics auto-add docs.

Constraints:
- Topic delete never silently drops references — always enqueue `needs_topic_review` for affected docs.
- Atomic writes: when updating a topic file, write to a temp file and rename (avoid partial-write corruption).
- No QMD calls in this task (topics are purely structural; QMD comes in the wiki/query phases).

Done criteria:
- `uv run nexus archive topic new ml-architectures --title "ML Architectures" --summary "..."` creates topics/ml-architectures.toml.
- `uv run nexus archive topic update ml-architectures --parent machine-learning` updates the parent field.
- `uv run nexus archive topic delete ml-architectures` (with no member docs yet) removes the file cleanly.
- `uv run nexus archive topics --match arch` returns matching topics.
- Membership sync helper is unit-tested independently (or at least exercised via a manual smoke test — write a stub doc, add a topic, observe the topic's [[docs]] list updates).

## Completion Notes

Implemented Phase 2: topic CRUD + membership auto-sync.

Utils additions (src/utils/archive.py):
- topic_exists(slug), list_all_topics() (sorted, swallows malformed files)
- sync_topic_membership(doc_slug, new_topics, old_topics, hook_overrides=None): reconciles a doc's claimed topics against each topic file's [[docs]] list. Adds with empty hook (or override) for (new - old); removes for (old - new); preserves existing hooks on no-op topics; silently skips missing topic files (caller validates).
- get_or_create_topic_member_hook(topic_slug, doc_slug): returns existing hook or empty string.
- regenerate_index(): minimal phase-2 implementation walking topics/ + wiki/, computing topic doc-count, parent/related/children, summary_line. Orphan/stale/broken_link counts default 0 (phase 4 fills them in).
- Hoisted datetime/timezone, IndexTopicEntry, TopicMember to top-of-module imports per no-function-imports rule.

Commands (src/commands/archive/topic.py):
- `topic new <slug> --title <t> --summary <s> [--parent <slug>] [--related <slug>,<slug>]`: validates kebab-case slug format + uniqueness, parent existence, related existence, rejects self-reference and duplicates in related. Sets created/updated/last_maintained=today, empty docs. Saves + regenerate_index. Prints ACTION REQUIRED hint.
- `topic update <slug> [--title --summary --parent --related]`: validates parent/related, prints before/after diff for changed fields only, no-op message if nothing changed, --parent "" clears parent.
- `topic delete <slug>`: walks wiki/, strips topic from each doc's frontmatter `topics:` list, enqueues a `needs_topic_review` work item per affected doc, deletes the topic file atomically, regenerates index. Reports affected-doc list.
- `topic show <slug> [--json]`: human-readable or JSON view.
- `topics [--match <q>] [--json]`: lists topics; --match does case-insensitive substring filter against title or summary (NOT QMD).

Slight CLI deviation from spec text: spec lists `nexus archive topic <slug>` for show, which conflicts with Typer subcommand dispatch. Used `nexus archive topic show <slug>` instead — matches the learn/manage pattern. User-confirmed during planning.

Wiring (src/commands/archive/main.py):
- Added topic sub-app: `app.add_typer(topic_app, name="topic", ...)`.
- Added topics top-level: `app.command(name="topics", ...)(topics)`.

Smoke tests verified end-to-end:
- Validation paths: reject missing parent, reject self-as-related, reject self-as-parent, reject duplicate slug, reject malformed slug.
- CRUD: topic new (with and without parent/related); topics list (full and filtered via --match); topic show (human and --json); topic update with field diff; topic update no-op message; topic update --parent "" to clear.
- Membership sync (Python REPL): create stub doc with topics=[a,b], sync from [] -> [a,b], verify both topic files contain the doc; sync from [a,b] -> [c,b], verify a removed, c added, b preserved.
- Topic delete with attached doc: deleted topic removed from doc's frontmatter, work item enqueued in archive/work.toml with needs_topic_review kind + descriptive detail, topic file removed.
- index.toml regenerated correctly after each mutation (counts and topic entries match disk state).

Conventions:
- Atomic writes via existing _atomic_write_text/_atomic_write_bytes helpers.
- All paths displayed are absolute.
- No QMD calls (per phase 2 constraint).
- All imports at module top.