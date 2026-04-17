---
title: 'QMD wiring: search, query, update on mutation'
status: todo
created_at: '2026-04-17T14:03:21.411415'
updated_at: '2026-04-17T14:03:21.411415'
completed_at: null
---
Phase 5 of the implementation plan in spec.md. Wires QMD into the archive — recall-style search and the two-pronged `query` command. Resolves the deferred TODO from phase 3 (qmd update on mutation).

Files to create:

src/commands/archive/search.py — `nexus archive search "<q>" [-n N] [--json]`:
- Raw QMD shell-out, no enrichment. Use when you specifically want QMD's view (for debugging or a deliberate fast brain-style probe).
- Calls `qmd search "<q>" -c nexus-archive --json -n N` (default N from archive.toml's qmd.default_recall_n, default 10).
- Output: hits with score, title, snippet, path. With --json: pass through QMD's JSON output verbatim.

src/commands/archive/query.py — `nexus archive query "<q>" [--no-breadcrumbs] [-n N] [--json]`:
- The recall-mode primitive. Two-pronged enrichment over QMD output.
- Calls `qmd query "<q>" -c nexus-archive --json -n N`.
- For each hit, parse the doc's frontmatter (using load_doc) and surface the frontmatter-summary view: slug, title, summary, topics, links (just the slugs + relations), tags, status.
- Compute the union of topics across all hits; for each such topic, also include its summary line (from topics/<slug>.toml).
- Output structure:
  ```
  Relevant topics (M):
    <topic-slug> — <summary_line>
    ...
  Relevant docs (N):
    <slug>
      Title: <title>
      Summary: <summary>
      Topics: [<list>]
      Links: <relation> <slug>, ...
      Tags: [<list>]
    ...
  ```
- --no-breadcrumbs: omit the "Relevant topics" section, just show docs.
- --json: structured output for agents.
- IMPORTANT: never include doc bodies. Never include QMD snippets. Never synthesise prose. The CLI is a data primitive; the calling agent does any synthesis.

src/utils/archive.py additions:

- qmd_search(q, n) -> list[dict] — wraps `qmd search ... --json`.
- qmd_query(q, n) -> list[dict] — wraps `qmd query ... --json`.
- qmd_update_collection() -> None — wraps `qmd update --collections nexus-archive`. Logs to state.toml's last_qmd_update.
- qmd_check() -> bool — wraps `qmd --version`; raises clear error with install instructions if missing.

Mutation hook integration (resolves the phase-3 TODO):
- Update src/commands/archive/write.py, doc.py (update/rename/delete), and link.py to call qmd_update_collection() at the end of the operation.
- For v1 we run it synchronously. If observed latency is problematic, add a `--no-qmd-update` flag that skips it; users can then run `nexus archive reindex` (phase 8) to batch-update. Make this a runtime decision based on actual measurement, not premature optimisation.

Mapping QMD paths to archive slugs:
- QMD returns paths relative to its collection root (which we registered as archive/wiki/). The path for a doc is just `<slug>.md`. Strip the .md to recover the slug for frontmatter lookup. Be defensive — if a path doesn't end in .md or doesn't correspond to an existing doc, log a warning and skip.

Constraints:
- All QMD calls go through src/utils/archive.py wrappers. No direct subprocess calls in command files.
- Errors from qmd are surfaced clearly with the exact command that failed and stderr.
- If qmd is not installed, `search` and `query` exit 1 with install instructions; mutation commands warn but still complete (the mutation must succeed even if the qmd update fails).

Done criteria:
- `uv run nexus archive search "transformer"` returns QMD hits.
- `uv run nexus archive query "transformer"` returns the enriched two-pronged view (topics + docs as frontmatter summaries).
- After `uv run nexus archive write` of a new doc, the doc is searchable via `qmd search` directly (verified via `qmd search "<term-from-doc>" -c nexus-archive`).
- `uv run nexus archive doc rename` updates QMD's index so the new slug is searchable and the old isn't.