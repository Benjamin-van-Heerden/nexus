---
created_at: '2026-05-05T11:04:01.565313'
username: benjamin_van_heerden
spec_slug: nexus_archive_command
---
# Work Log - Completed nexus archive command

## Overarching Goals

Complete the remaining phases of the `nexus_archive_command` spec and make the
archive agent deployable as a file-first, ephemeral archivist. This session
covered ingestion, outputs, maintenance/integrity, onboard/agent instructions,
QMD runtime installation/testing, and run-cycle documentation.

## What Was Accomplished

### Ingestion (`nexus archive add`)

- Added `nexus archive add <path-or-url>` for staging markdown sources into
  `archive/raw/`.
- Implemented deterministic SHA256-based raw filenames, TOML sidecar metadata,
  duplicate hash warnings, first-H1 title guesses, suggested slugs, QMD recall
  hits, and keyword candidate topics.
- Added URL fetching via `httpx`, with v1 markdown-only validation.
- Patched QMD hit parsing to support QMD 2.1.0's `file` field as well as the
  older/assumed `path` field.
- Tightened excerpt generation so QMD recall receives clean plain-text queries
  while preserving hyphenated terms such as `self-attention`.

### QMD Runtime Bootstrap

- Installed and tested QMD locally at version 2.1.0.
- Registered the `nexus-archive` collection and completed first-run model cache
  warmup.
- Added `scripts/install-qmd.sh`, with `QMD_VERSION="2.1.0"` pinned at the top.
  The script supports `--check-only`, `--setup-archive`, and `--warmup`.
- Documented that deployments must persist `~/.cache/qmd` because QMD stores
  indexes and downloaded models there.

### Outputs Sub-App

- Added `nexus archive output` commands:
  - `save`
  - `list`
  - `show`
  - `integrate`
  - `split`
  - `archive`
- `output save` validates frontmatter, slug match, non-empty cites and novelty,
  cite resolution against wiki docs, persists to `archive/outputs/`, enqueues
  `pending_output`, and regenerates `index.toml`.
- `output integrate` updates target doc provenance via
  `provenance.origin_outputs`, marks output integrated, resolves the work item,
  and does not modify doc body.
- `output split` stages multi-doc split instructions and marks integrated for
  v1.
- `output archive` marks redundant outputs archived and resolves work items.

### Maintenance, Integrity, and Reindex

- Added `nexus archive work list`, combining persisted work queue items with
  computed orphan and stale items.
- Added `nexus archive maintain`, a read-only maintenance scaffold with ordered
  jobs and concrete next-step commands.
- Added `nexus archive integrity`, which detects missing links, missing topics,
  missing mentions, orphan topic members, and broken output cites; it enqueues
  work items, updates `broken_links`, strips invalid topic members, and
  regenerates the index.
- Added `nexus archive reindex`, which regenerates `index.toml`, updates
  `state.last_reindex`, refreshes QMD, and prints timing/status.
- Added reusable maintenance utilities: `compute_orphans`, `compute_stales`,
  minimal `compute_contradictions`, and `get_topic_member_freshness`.

### Onboard and Agent Instructions

- Added `nexus archive onboard [--task add|ingest|query|maintain]`.
- Onboard now includes pause handling, task-specific framing, archive state,
  top-level index summary, recent activity, scoped work queue summary, absolute
  paths, references to run-cycle and QMD install docs, full agent instructions,
  and an ACTION REQUIRED footer.
- Added `src/commands/archive/agent_instructions.md` covering archive identity,
  graph model, mutation rules, ephemeral session model, invocation modes,
  add/query/maintenance workflows, output triage, topic management, command
  reference, and deployment notes.

### Run-Cycle Documentation

- Added `archive_run_cycle.md` at repo root documenting the archive operating
  model: ephemeral sessions by default, no refresh command, add/query/maintain
  wake modes, daily/weekly scheduling suggestions, and cross-agent usage.

### Verification

- Ran Python compile checks across changed Python files.
- Exercised archive commands via Typer `CliRunner`.
- Verified QMD registration, search/query behavior, and recall integration.
- Tested output workflows and maintenance/integrity workflows with temporary
  fixtures, then cleaned all test archive content and stale work items.
- Verified archive pause/resume behavior for onboard.

## Key Files Affected

- `src/commands/archive/add.py` — new ingestion command.
- `src/commands/archive/output.py` — new outputs sub-app.
- `src/commands/archive/work.py` — work queue listing.
- `src/commands/archive/maintain.py` — maintenance scaffold.
- `src/commands/archive/integrity.py` — integrity scanner/repair pass.
- `src/commands/archive/reindex.py` — index/QMD rebuild command.
- `src/commands/archive/onboard.py` — archivist session context dump.
- `src/commands/archive/agent_instructions.md` — source of truth for archive
  agent behavior.
- `src/commands/archive/main.py` — wired all new archive commands.
- `src/utils/archive.py` — raw ingestion helpers, output/work helpers,
  maintenance computations, QMD compatibility tweaks, cleaned excerpt
  generation.
- `scripts/install-qmd.sh` — pinned QMD install/check/warmup script.
- `archive_run_cycle.md` — operational model for the archive agent.

## Errors and Barriers

- `uv run ruff` and `uv run ty` could not run because those tools are not
  installed in the project environment. Syntax checks were performed with
  `uv run python -m py_compile` instead.
- The installed `nexus` console command in this environment did not expose the
  current worktree's archive app, so command verification used Typer
  `CliRunner` against `src.commands.archive.main`.
- QMD direct commands failed inside sandboxed execution because QMD needs access
  to its user cache (`~/.cache/qmd`). Running QMD with approved access worked.
- QMD 2.1.0 returns hit paths under `file`; the code initially expected `path`.
  This was fixed in `archive add` and `archive query`.
- QMD first-run query required a large reranker model download into
  `~/.cache/qmd/models`. This informed the deployment script and cache
  persistence documentation.

## What Comes Next

All tasks in the `nexus_archive_command` spec are complete. The next action is
to run `mem spec complete nexus_archive_command "detailed commit message"` to
let mem create the PR and mark the spec merge-ready.
