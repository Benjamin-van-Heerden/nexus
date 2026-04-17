---
title: 'Topics: CRUD commands and member auto-sync'
status: todo
created_at: '2026-04-17T14:01:44.779769'
updated_at: '2026-04-17T14:01:44.779769'
completed_at: null
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