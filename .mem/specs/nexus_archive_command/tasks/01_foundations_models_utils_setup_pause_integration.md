---
title: 'Foundations: models, utils, setup, pause integration'
status: completed
created_at: '2026-04-17T14:01:20.082970'
updated_at: '2026-04-29T15:38:37.876841'
completed_at: '2026-04-29T15:38:37.876831'
---
Phase 1 of the implementation plan in spec.md. Implements the foundational layer that everything else builds on.

Files to create:

src/models/archive/archive.py — ArchiveConfig (interests, maintenance.staleness_days default 90, maintenance.batch_size default 10, qmd.collection_name default "nexus-archive", qmd.default_recall_n default 10) and ArchiveState (last_reindex, last_qmd_update, schema_version starting at 1, renames list of {old, new, at}).

src/models/archive/doc.py — DocFrontmatter (slug, title, summary, created, updated, status enum [draft|stable|stale|contradicted], topics list[str], links list[LinkRef], mentions list[str], sources list[str], provenance {ingested_from, origin_outputs}, broken_links list[str], last_maintained, tags list[str]). LinkRef = {slug, relation} where relation enum is [supersedes, superseded_by, depends_on, extends, contradicts, spawned, references, part_of_series].

src/models/archive/topic.py — TopicConfig (slug, title, summary, parent optional, related list[str], created, updated, last_maintained, docs list[TopicMember]). TopicMember = {slug, hook}.

src/models/archive/output.py — OutputFrontmatter (slug, query, created, status enum [pending_review|integrated|archived], cites list[str], novelty).

src/models/archive/work.py — WorkItem (kind enum [broken_link|pending_output|orphan|stale|contradiction|needs_topic_review], slug, detail optional, created), WorkQueue (items list[WorkItem]).

src/models/archive/index.py — IndexFile (generated, doc_count, topic_count, pending_outputs, orphan_count, stale_count, broken_link_count, topics list of {slug, summary_line, doc_count, parent optional, related list, children list}).

src/utils/archive.py — implement:
- Path getters: get_archive_dir, get_wiki_dir, get_topics_dir, get_raw_dir, get_outputs_dir, get_archive_config_path, get_archive_state_path, get_work_path, get_index_path, get_agent_instructions_path. All return Path. All resolve to project root (use existing path_resolution utilities).
- Config loaders/savers: load_archive_config, save_archive_config, load_archive_state, save_archive_state, load_work_queue, save_work_queue, load_topic(slug), save_topic, load_doc(slug) -> (frontmatter, body), save_doc(slug, frontmatter, body), load_output, save_output, load_index, save_index. All use tomllib + tomli_w for TOML, PyYAML for the YAML frontmatter blocks.
- Frontmatter helpers: parse_frontmatter(text) -> (dict, body_str) splitting on "---" delimiters, serialize_doc(frontmatter_dict, body_str) -> str producing valid frontmatter+body markdown.
- Slug helpers: slugify(title), is_valid_slug(s), ensure_unique_slug(candidate, existing_set).
- Mention extraction: extract_mentions(body) -> list[str] using regex r"\[\[([a-z0-9-]+)\]\]".
- QMD wrapper: qmd_run(args: list[str], json: bool = False) — shells to `qmd` via subprocess.run, captures stdout, parses JSON if requested, raises clear error if qmd is not on PATH (with install instructions).

src/commands/archive/setup.py — setup() command:
1. Pause check (skip if archive paused; mirror learn/self/manage pattern).
2. Create archive/, archive/raw/, archive/wiki/, archive/topics/, archive/outputs/ if missing.
3. Write default archive.toml and state.toml if missing.
4. Check qmd is on PATH (`qmd --version`); if not, print install instructions (`npm install -g @tobilu/qmd` or `bun install -g @tobilu/qmd`) and exit 1.
5. Register wiki dir with QMD: `qmd collection add <abs-wiki-dir> --name nexus-archive --mask "**/*.md"`.
6. Add context: `qmd context add qmd://nexus-archive "Personal knowledge base wiki entries."`.
7. Run `qmd embed`.
8. Print summary with absolute paths to all archive subdirs + ACTION REQUIRED footer.

src/commands/archive/main.py — wire the archive Typer app. For this phase only `setup` is wired; later tasks add more subcommands.

main.py at project root — register the archive app: `from src.commands.archive.main import app as archive_app` and `app.add_typer(archive_app, name="archive", help="Personal knowledge base / second brain")`.

src/models/pause.py — add `archive: PauseEntry = PauseEntry()` to PauseConfig.

src/commands/pause/main.py — add "archive" to the recognised app names (read existing learn/self/manage handling and mirror it).

Constraints:
- No __init__.py files (per no-init-py memory).
- All paths stored in TOML/YAML use ./ prefix; all paths displayed to user/agent are absolute via resolve_str() (per relative-paths-and-resolve memory).
- All Python operations via uv (per project conventions).

Done criteria:
- `uv run nexus archive setup` creates all dirs, writes defaults, registers QMD collection (if installed), and prints absolute paths.
- `uv run nexus pause archive --until <date> --reason <r>` followed by `uv run nexus archive setup` shows the pause and exits early.
- All models round-trip cleanly via tomllib + tomli_w (and PyYAML for frontmatter).

## Completion Notes

Implemented Phase 1 foundations for nexus archive.

Models created (src/models/archive/):
- archive.py: ArchiveConfig (interests, MaintenanceConfig {staleness_days=90, batch_size=10}, QmdConfig {collection_name=nexus-archive, default_recall_n=10}) and ArchiveState (last_reindex, last_qmd_update, schema_version=1, pending_qmd_update, renames list).
- doc.py: DocFrontmatter with all spec fields, LinkRef, Provenance, status/relation enums via Literal types.
- topic.py: TopicConfig with TopicMember.
- output.py: OutputFrontmatter with status enum.
- work.py: WorkItem (kind enum: broken_link, pending_output, orphan, stale, contradiction, needs_topic_review), WorkQueue.
- index.py: IndexFile with IndexTopicEntry.

Utils (src/utils/archive.py):
- Path getters: get_wiki_dir, get_topics_dir, get_raw_dir, get_outputs_dir, get_archive_config_path, get_archive_state_path, get_work_path, get_index_path, get_agent_instructions_path.
- TOML I/O via tomllib + tomli_w with atomic writes (temp file + rename).
- Loaders/savers for archive config/state, work queue, topics, docs, outputs, index.
- enqueue_work helper.
- Frontmatter helpers: parse_frontmatter (regex split + yaml.safe_load), serialize_doc (yaml.safe_dump).
- Slug helpers: slugify (kebab-case), is_valid_slug, ensure_unique_slug.
- extract_mentions: regex-based [[slug]] extraction with first-seen ordering.
- QMD wrapper: qmd_check, qmd_run with QmdNotInstalledError surfaced with install hints.

Setup command (src/commands/archive/setup.py):
1. Pause check (mirrors learn/self/manage pattern via check_pause("archive")).
2. Creates archive/, raw/, wiki/, topics/, outputs/.
3. Writes default archive.toml, state.toml, empty work.toml.
4. Runs qmd --version; on failure prints install instructions and exits 1.
5. Registers wiki dir as QMD collection 'nexus-archive', adds context, runs qmd embed.
6. Prints absolute PATHS section + ACTION REQUIRED footer.

Plumbing:
- src/commands/archive/main.py wires the archive Typer app (currently exposing only `setup`).
- main.py at project root now registers the archive_app: `app.add_typer(archive_app, name='archive', ...)`.
- src/models/pause.py: added archive: PauseEntry to PauseConfig.
- src/utils/pause.py: extended Literal type to include 'archive'.
- src/commands/pause/main.py: added `pause archive` subcommand and updated `resume` to accept 'archive'.
- src/utils/paths.py: added get_archive_dir().

Dependencies:
- Added pyyaml (6.0.3) to project deps for YAML frontmatter parsing/serialization.

Smoke tests verified:
- `uv run python main.py archive --help` shows the archive subapp with `setup`.
- `uv run python main.py archive setup` creates all directories and config files; cleanly exits 1 with install instructions when qmd is missing.
- `uv run python main.py pause archive --until 2026-05-01 --reason "smoke test"` pauses; subsequent `archive setup` detects pause and exits early; `pause resume archive` clears the pause.
- Helpers exercised in a Python REPL: slugify, is_valid_slug, ensure_unique_slug, extract_mentions (skips invalid slug forms, dedupes), parse_frontmatter + DocFrontmatter round-trip across nested links/provenance.

Conventions followed:
- No __init__.py files (per no-init-py memory).
- Pause integration mirrors learn/self/manage exactly.
- All path display in setup output is absolute.
- Atomic writes throughout to avoid partial-write corruption.
- All TOML/YAML I/O routed through helpers; no direct subprocess.run outside the qmd_run wrapper.