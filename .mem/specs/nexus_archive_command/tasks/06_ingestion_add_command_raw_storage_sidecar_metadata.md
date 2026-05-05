---
title: 'Ingestion: add command, raw storage, sidecar metadata'
status: completed
created_at: '2026-04-17T14:03:52.866297'
updated_at: '2026-05-05T10:22:22.829158'
completed_at: '2026-05-05T10:22:22.829148'
---
Phase 6 of the implementation plan in spec.md. Implements `nexus archive add` — the entry point for new source material.

Files to create:

src/commands/archive/add.py — `nexus archive add <path-or-url>` command:

1. Determine input type:
   - If <path-or-url> starts with http:// or https://: fetch via httpx, save to a temp .md file (assume markdown for v1 per the out-of-scope note in spec; non-markdown URLs go to the future raw/unprocessed/ pipeline). If the response is not text/markdown, error out with "Only markdown sources supported for v1; PDFs/HTML belong in raw/unprocessed/ (future spec)."
   - If <path-or-url> is a local path: verify it exists and ends in .md (error otherwise with the same v1 limitation message).
2. Hash the file contents (SHA256, take first 12 chars for the filename).
3. Copy to archive/raw/<hash>.md (use copyfile + atomic rename via temp).
4. If the hash already exists in raw/, surface a duplicate warning with the existing sidecar's metadata; ask the agent to confirm whether to proceed (in the printed instructions; this command itself doesn't prompt — it just informs and proceeds, since CLI is non-interactive).
5. Write archive/raw/<hash>.toml sidecar with origin metadata:
   ```toml
   hash = "<hash>"
   filename = "<hash>.md"
   original_path = "<input-path-or-url>"
   fetched_at = <iso-datetime>
   title_guess = "<extracted from first H1 if present>"
   byte_size = <int>
   line_count = <int>
   ```
6. Run `nexus archive query` internally on the doc's content (extract first 500 words as a heuristic query) to surface candidate similar docs. Use qmd_query() under the hood; collect top 5 hits.
7. Walk topics/, find candidate topics whose summary or title contains words from the doc's title or first paragraph (simple keyword match — this is a hint, not a recommendation).
8. Print structured next-step instructions for the agent:
   ```
   Source ingested.
     hash: <hash>
     raw file: <abs-path-to-raw>
     sidecar: <abs-path-to-sidecar>
     title guess: <title>

   QMD recall — similar existing docs:
     <slug> — <summary first line> (score: <s>)
     ... (top 5)

   Candidate topics (keyword match):
     <slug> — <summary line>
     ... (top 5)

   ACTION REQUIRED:
     1. Read the raw file: <abs-path>
     2. Decide:
        a) New doc → draft frontmatter + body to a temp file, then run:
           nexus archive write <new-slug> --file <temp-file>
        b) Augment existing doc → run:
           nexus archive doc update <existing-slug> --file <temp-file>
        c) Already-known content (duplicate or trivially redundant) → no action; the raw stays as a record.
     3. Suggested slug: <slugified title guess>
     4. Use the QMD recall and candidate topics above to inform link and topic assignments.
   ```
9. Exit cleanly. The CLI never writes to wiki/ from `add` — it just stages raw and informs the agent.

src/utils/archive.py additions:

- hash_file(path) -> str — SHA256, first 12 chars hex.
- fetch_url_to_temp(url) -> Path — httpx GET, save body to a temp .md, return path. Validate Content-Type startswith text/.
- save_raw(source_path, hash) -> (raw_path, sidecar_path) — copy source to raw/<hash>.md, write sidecar.
- read_first_h1(markdown_text) -> str | None — for title guess.
- extract_excerpt(markdown_text, word_count=500) -> str — for the QMD recall query.
- find_candidate_topics_by_keywords(text) -> list[TopicConfig] — simple word-match against topic title + summary, ranked by match count.

Constraints:
- Never write to wiki/ from this command. The agent does that explicitly via `write` or `doc update`.
- Hashing is deterministic; duplicates are detected and surfaced, never silently re-added.
- httpx is already in the project (per always-use-httpx memory); use it for URL fetching.
- For v1, only markdown is accepted. Non-markdown errors out with a clear pointer to the future raw/unprocessed/ workflow.
- All paths in printed output are absolute.

Done criteria:
- `uv run nexus archive add path/to/source.md` produces archive/raw/<hash>.md + sidecar.
- `uv run nexus archive add https://example.com/article.md` fetches and stores.
- The printed instructions include QMD recall hits, candidate topics, suggested slug, and the exact follow-up command.
- Re-adding the same source surfaces a duplicate warning with the existing sidecar's origin info.

## Completion Notes

Implemented nexus archive add for local markdown paths and markdown URLs. Added raw ingestion helpers in src/utils/archive.py for SHA256 hashing, URL fetch to temp markdown via httpx, raw/sidecar atomic persistence, H1 title extraction, cleaned excerpt generation for QMD recall, and keyword-based candidate topic matching. Added src/commands/archive/add.py to stage sources in archive/raw, detect duplicate hashes with previous sidecar metadata, run best-effort QMD recall, surface candidate topics, suggest a slug, and print exact archivist next steps without writing to wiki/. Wired add into src/commands/archive/main.py. Installed and tested QMD 2.1.0 locally, registered the nexus-archive collection, completed first-run model warmup, and verified archive add surfaces a QMD recall hit from an indexed temporary wiki doc. Patched QMD hit handling to accept both path and file fields for QMD 2.1.0 compatibility. Verified syntax with uv run python -m py_compile and cleaned up temporary test fixtures.