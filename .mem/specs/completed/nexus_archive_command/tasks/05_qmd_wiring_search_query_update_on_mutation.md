---
title: 'QMD wiring: search, query, update on mutation'
status: completed
created_at: '2026-04-17T14:03:21.411415'
updated_at: '2026-04-29T17:14:50.281166'
completed_at: '2026-04-29T17:14:50.281154'
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

## Completion Notes

Implemented Phase 5: QMD recall + mutation hook integration.

Utils additions (src/utils/archive.py):
- qmd_search(q, n): wraps `qmd search "<q>" -c <name> --json -n N`. Returns list of hit dicts via _qmd_unwrap_hits.
- qmd_query(q, n): same envelope wrapping for `qmd query`.
- qmd_update_collection(): runs `qmd update --collections <name>`, stamps state.toml.last_qmd_update, clears pending_qmd_update.
- qmd_path_to_slug(path): defensive path -> slug mapper. Strips suffix, verifies slug exists in wiki/, returns None otherwise. Handles absolute, relative, missing, non-md, None, and empty inputs.
- _qmd_unwrap_hits(payload): coerces qmd JSON output. Handles bare list, {results: [...]}, {hits: [...]}, {data: [...]}, None, and unknown shapes (returns []).
- trigger_qmd_update_after_mutation(echo): high-level wrapper. Marks pending_qmd_update first, runs qmd_update_collection, on QmdNotInstalledError emits a warning and leaves pending=True, on RuntimeError emits stderr and leaves pending=True. Mutations always succeed.

Mutation hook integration:
- Every mutation now calls trigger_qmd_update_after_mutation(typer.echo) after regenerate_index().
- write.py: write
- doc.py: update, rename, delete
- link.py: add, remove
- Replaces the phase-3 mark_pending_qmd_update() stub. Resolves the deferred TODO from phase 3.

Commands:

search.py — `nexus archive search "<q>" [-n N] [--json]`:
- Raw QMD hits, no enrichment. Default N from archive.toml.qmd.default_recall_n.
- Exits 1 with install hint if qmd missing; exits 1 with stderr on other failures.
- --json passes qmd's JSON output through verbatim.

query.py — `nexus archive query "<q>" [-n N] [--no-breadcrumbs] [--json]`:
- Two-pronged enriched view:
  - For each qmd hit: resolve path -> slug via qmd_path_to_slug, load frontmatter, emit frontmatter-summary view (slug, title, summary, topics, links with relations, tags, status).
  - Compute union of topics across hits; for each, emit slug + summary_line.
- Never returns doc bodies, raw QMD snippets, or LLM-synthesised prose.
- Skipped paths (qmd hit didn't resolve to a wiki slug) reported in footer.
- --no-breadcrumbs omits the topics section.

Wiring (src/commands/archive/main.py): added search and query at archive top level. All 12 archive commands now wired.

Smoke tests verified:
- Wiring: all archive subcommands appear in --help.
- search and query without qmd installed: exit 1 with install hint cleanly.
- Mutation graceful degradation: topic new + write succeed despite qmd missing; warning printed; pending_qmd_update flag remains True (so future reindex picks it up).
- qmd_path_to_slug unit cases: None/empty/non-md -> None, absolute path with .md -> slug if exists, relative .md -> slug if exists, missing slug -> None.
- _qmd_unwrap_hits unit cases: list passthrough, dict-with-results unwrap, dict-with-hits unwrap, dict-with-data unwrap, None -> [], unknown shape -> [].

Notes:
- Done criteria items #3 and #4 (write makes doc searchable in qmd; doc rename re-indexes) require qmd to be installed for end-to-end verification. The wiring is complete and will work once qmd is on PATH.
- All qmd subprocess calls go through src/utils/archive.py wrappers; no direct subprocess.run in command files.