---
title: nexus archive command
status: todo
assigned_to: null
issue_id: 10
issue_url: https://github.com/Benjamin-van-Heerden/nexus/issues/10
branch: null
pr_url: null
created_at: '2026-04-17T13:47:00.069833'
updated_at: '2026-04-17T16:09:16.556202'
completed_at: null
last_synced_at: '2026-04-17T16:09:16.555660'
local_content_hash: ad0b6838af355709b5fafb99899b87d698ecc0896e300c0f3f59de46be5a381c
remote_content_hash: ad0b6838af355709b5fafb99899b87d698ecc0896e300c0f3f59de46be5a381c
---
## Overview

Build `nexus archive` — a personal, file-first knowledge base ("second brain") that an AI agent (the **archivist**) ingests into and queries against. Inspired by Andrej Karpathy's wiki idea, but with rigorous structure: deterministic CLI primitives wherever possible, agent intervention only where judgment is genuinely required.

The archive is not a chat-with-your-notes tool. It is a *deliberately traversed* knowledge graph. Two modes of search complement each other:

- **Recall** (fast, surface-level, brain-like) — backed by [QMD](https://github.com/tobi/qmd), an on-device hybrid search engine (BM25 + vector + reranking). Returns *pointers*, not bodies. Used as the warm-start for ingestion linking and as a query primitive.
- **Traversal** (deliberate, systematic, librarian-like) — walks the structured graph: `index → topic → doc → linked doc`. Every level exposes summaries so the librarian can decide what to open without reading bodies.

Knowledge is a graph, not a tree. Docs live in a flat `wiki/` directory. **Topics** are the organising overlay — multi-valued (a doc can belong to many) and connected to each other via `parent` + `related` relations. There are no subsections; depth comes from topic-to-topic relationships, not nested folders.

The archivist agent is responsible for the few operations that require judgment: composing a wiki entry from raw source, refreshing topic summaries, integrating outputs into the graph, resolving contradictions, finding homes for orphans. Everything else — reading, writing files, validating links, computing graphs, generating indexes, surfacing pending work — is deterministic CLI behaviour.

## Goals

- A flat `wiki/` of markdown docs with rigorous YAML frontmatter (slug, summary, topics, links, mentions, sources, status, provenance, dates).
- A `topics/` directory of TOML files defining the organising overlay, with auto-maintained member lists.
- An `outputs/` directory for agent-produced syntheses, integrated back into the graph during maintenance.
- A `raw/` directory for immutable source material (markdown for v1; pre-processing pipelines for non-markdown handled later via `raw/unprocessed/`).
- An auto-generated `index.toml` exposing the full structural map for the librarian to enter from.
- A `work.toml` queue tracking pending archivist decisions (broken links, orphans, stales, contradictions, outputs awaiting triage).
- QMD integration providing recall-style search. Shelled out via `subprocess`; `nexus archive setup` configures the QMD collection.
- `nexus archive query` returns recall hits as **frontmatter-summary views of relevant topics + docs** — no raw QMD snippets, no doc bodies, no LLM synthesis inside the CLI.
- `nexus archive` agent instructions (`agent_instructions.md`) describe the archivist's role, three invocation modes, decision trees, and command reference — following the established `learn`/`self`/`manage` pattern.
- Graph integrity is preserved on every mutation. Slug renames rewrite all references atomically; deletes flag affected docs but never silently drop data.
- An `onboard` command surfaces full archive state + work queue + paths + agent instructions. Always runs at the start of an archivist session, regardless of invocation mode.

## Technical Approach

### Directory layout (content)

The archive content lives at the project root, mirroring `learn/`, `self/`, `manage/`:

```
archive/
├── archive.toml          # config (interests, defaults, staleness threshold)
├── state.toml            # CLI-mutated (last_reindex, last_qmd_update)
├── work.toml             # archivist work queue
├── index.toml            # auto-generated structural map
├── raw/
│   ├── <hash>.md         # immutable source (markdown only for v1)
│   └── <hash>.toml       # sidecar: origin metadata (url, fetched_at, title, etc.)
├── wiki/
│   └── <slug>.md         # YAML frontmatter + markdown body
├── topics/
│   └── <slug>.toml       # topic definition + auto-maintained member list
└── outputs/
    └── <slug>.md         # YAML frontmatter + markdown body (agent syntheses)
```

`raw/unprocessed/` (PDFs, HTML, websites needing extraction) is **out of scope** for this spec — it'll be a follow-up that produces files into `raw/`.

QMD's index lives wherever QMD wants it (its default cache, `~/.cache/qmd/`). `nexus archive setup` registers `archive/wiki/` as a QMD collection named `nexus-archive`.

### Directory layout (code)

Following `cli-structure-convention` and `no-init-py`:

```
src/commands/archive/
├── main.py                  # wires subcommands into the archive Typer app
├── onboard.py               # context dump
├── add.py                   # ingest raw → trigger agent flow
├── write.py                 # commit a drafted wiki doc (CLI-side of `add`/edit)
├── show.py                  # display a doc (frontmatter only by default)
├── doc.py                   # rename, update, delete
├── topic.py                 # topic CRUD + listing
├── link.py                  # add/remove typed links
├── query.py                 # recall: QMD + frontmatter-summary view
├── search.py                # raw QMD shell-out (no enrichment)
├── related.py               # graph neighbours (links + backlinks + mentions)
├── neighborhood.py          # local subgraph blob
├── index_cmd.py             # `nexus archive index` — print or regenerate
├── recent.py                # temporal entry
├── tag.py                   # tag-based entry
├── output.py                # output sub-app: list, save, integrate, split, archive
├── work.py                  # work-queue listing
├── maintain.py              # archivist maintenance entry point
├── integrity.py             # one-shot integrity scan
├── reindex.py               # rebuild caches (index.toml + qmd update)
├── setup.py                 # one-time setup (create dirs, register qmd collection)
└── agent_instructions.md    # archivist behaviour spec

src/models/archive/
├── archive.py               # ArchiveConfig, ArchiveState
├── doc.py                   # DocFrontmatter, LinkRef
├── topic.py                 # TopicConfig, TopicMember
├── output.py                # OutputFrontmatter
├── work.py                  # WorkItem, WorkQueue (with kind enum)
└── index.py                 # IndexFile (rendered to index.toml)

src/utils/archive.py         # path getters, frontmatter parse/write, qmd wrapper, slug helpers
```

Wired into `main.py` at project root:

```python
from src.commands.archive.main import app as archive_app
app.add_typer(archive_app, name="archive", help="Personal knowledge base / second brain")
```

### Frontmatter schemas

**Wiki doc** (`wiki/<slug>.md`):

```yaml
---
slug: attention-is-all-you-need
title: "Attention Is All You Need"
summary: >
  Introduces the Transformer — a sequence architecture built entirely on
  self-attention. Foundational for modern LLMs. Key contribution: multi-head
  attention replacing recurrence.
created: 2026-04-17
updated: 2026-04-17
status: stable                  # draft | stable | stale | contradicted
topics: [ml-architectures, foundational-papers, nlp]
links:                          # curated, typed edges (the librarian follows these)
  - slug: rnn-limitations
    relation: supersedes
  - slug: positional-encodings
    relation: depends_on
  - slug: sparse-transformers
    relation: spawned
mentions: [attention-mechanism, softmax]   # auto-extracted from [[slug]] in body
sources: ["./archive/raw/a3f4c1.md"]       # ./ convention; CLI resolves for display
provenance:
  ingested_from: add            # add | output_integration | manual
  origin_outputs: []            # output slugs this crystallised from
broken_links: []                # populated by CLI when refs go missing
last_maintained: 2026-04-17
tags: [paper, seminal, 2017]
---

Body of the doc in markdown. Free-form prose. May contain inline references
like [[transformer-implementations]] which the CLI extracts into `mentions`
on save.
```

Validated relations (`relation` field, extensible): `supersedes`, `superseded_by`, `depends_on`, `extends`, `contradicts`, `spawned`, `references`, `part_of_series`. Stored as enum in `LinkRef`.

**Topic** (`topics/<slug>.toml`):

```toml
slug = "ml-architectures"
title = "Machine Learning Architectures"
summary = """
Architectural patterns in ML models — RNNs, CNNs, transformers, MoE.
How design choices affect capability, training cost, and inference latency.
"""
parent = "machine-learning"        # optional; topic → topic hierarchy
related = ["nlp", "computer-vision", "training-dynamics"]
created = 2026-01-10
updated = 2026-04-17
last_maintained = 2026-04-17

# Members are CLI-maintained. Hand-edits will be overwritten on next mutation.
[[docs]]
slug = "attention-is-all-you-need"
hook = "The transformer paper. Foundational."

[[docs]]
slug = "mixture-of-experts"
hook = "Sparse activation for scaling capacity without per-token FLOPs."
```

The `hook` is a one-line per-doc summary, *distinct* from the doc's own `summary`. Hooks are written by the archivist when a doc is added to the topic, and refreshed during `maintain`. They're tuned to be useful *in the context of this topic* — a single doc may have different hooks in different topics.

**Output** (`outputs/<slug>.md`):

```yaml
---
slug: why-transformers-replaced-rnns
query: "Why did transformers replace RNNs in NLP?"
created: 2026-04-15
status: pending_review            # pending_review | integrated | archived
cites: [attention-is-all-you-need, rnn-limitations, lstm-gated-recurrence]
novelty: >
  User-contributed connection: links transformer adoption to hardware
  parallelism trends, not mentioned in any cited doc. Worth promoting.
---

The body of the synthesis as the calling agent wrote it.
```

**Index** (`archive/index.toml`, auto-generated, never hand-edited):

```toml
generated = 2026-04-17T13:47:00
doc_count = 142
topic_count = 23
pending_outputs = 8
orphan_count = 3
stale_count = 12
broken_link_count = 1

[[topics]]
slug = "machine-learning"
summary_line = "Umbrella — algorithms, theory, systems."
doc_count = 34
children = ["ml-architectures", "training-dynamics", "evaluation"]

[[topics]]
slug = "ml-architectures"
summary_line = "Architectural patterns in ML models."
doc_count = 12
parent = "machine-learning"
related = ["nlp", "computer-vision"]
```

The index renders inherently tree-ish (text is linear), but the underlying data is a graph; `parent` + `related` + `children` capture both shapes. Good enough for v1. Graph viewer is a future concern.

### Path conventions

Per `relative-paths-and-resolve` memory:

- All paths *stored* in TOML/YAML use `./` prefix relative to project root (e.g. `./archive/raw/a3f4c1.md`).
- All paths *displayed to agents* (onboard output, command output, error messages) are absolute, via `resolve_str()`.
- Frontmatter `sources:` field uses `./` form; `nexus archive show` displays absolute.

### Three invocation modes — all start with `onboard`

The archivist runs in three modes. All three start with `nexus archive onboard` because the agent is stateless between sessions and must re-acquire context every time.

1. **Direct** — long-lived terminal session (you + Claude/OpenClaw): onboard, then back-and-forth (bulk ingestion, exploration, manual maintenance).
2. **Subagent** — another nexus agent spins up an archivist subagent for a one-shot operation (add a doc, query the archive). Onboards, performs, exits. Onboard overhead is acceptable because sessions are short and the agent is stateless.
3. **Scheduled wake** — an external scheduler (out of scope for this spec, but the design must accommodate it) wakes the archivist with a directive like "run nexus archive onboard --task maintain, then drain the queue." Onboard surfaces the work queue; archivist handles it.

`nexus archive onboard` accepts an optional `--task <add|query|maintain|ingest>` flag. Without it, full context is shown. With it, the **instructions section emphasises the relevant subset of `agent_instructions.md`** and the work queue is filtered. The full PATHS, archive state summary, and ACTION REQUIRED footer always appear.

There is **no `refresh` command**. Sessions are either short (no need) or the user reruns `onboard` (cheap enough).

### Command surface

All commands print human-readable output by default; agent-friendly `--json` flag where structured output is useful (`query`, `search`, `index`, `topic`, `show`, `related`, `neighborhood`, `recent`, `tag`, `work list`, `output list`).

**Setup & onboard**
- `nexus archive setup` — one-time: ensure `archive/` exists, write default `archive.toml` and `state.toml`, register `archive/wiki/` as a QMD collection (`qmd collection add ... --name nexus-archive`), set context (`qmd context add qmd://nexus-archive ...`), warn if `qmd` not on PATH with install instructions.
- `nexus archive onboard [--task <add|query|maintain|ingest>]` — full context dump.

**Ingestion (agent-driven, deterministic CLI scaffolding)**
- `nexus archive add <path-or-url>` — copies/fetches source into `raw/<hash>.md`, writes sidecar `raw/<hash>.toml` with origin metadata, runs QMD recall to surface similar existing docs and candidate topics, prints structured next-step instructions to the agent (with absolute paths and the slug suggestion). The agent then drafts the wiki entry and commits via `write` or `doc update`.
- `nexus archive write <slug> --file <draft.md>` — validates frontmatter (required fields, schema), validates topic refs (warn + auto-create or fail per `--strict-topics`), validates link refs (missing → enqueue `broken_link`), extracts `[[slug]]` mentions from body, writes `wiki/<slug>.md`, updates referenced topics' `[[docs]]` lists, regenerates `index.toml`, queues a QMD update.
- `nexus archive doc update <slug> --file <draft.md>` — same as `write` but enforces the doc already exists; preserves `created`, bumps `updated`.
- `nexus archive doc rename <old> <new>` — atomic: rename file, rewrite all `links:`, `mentions:`, `cites:`, topic members, output references. Logs the rename to `state.toml` for audit.
- `nexus archive doc delete <slug>` — removes the doc, scans all references, strips dangling refs, flags affected docs (sets `broken_links:` and enqueues `broken_link` work items). Never silently drops data.

**Topics (CLI-driven mutation, but content is agent-supplied)**
- `nexus archive topic new <slug> --title <t> --summary <s> [--parent <slug>] [--related <slug>,<slug>]` — create a topic. Summary is required.
- `nexus archive topic update <slug> [--title <t>] [--summary <s>] [--parent <slug>] [--related <slugs>]` — update fields.
- `nexus archive topic delete <slug>` — unassigns from all docs, flags them with `needs_topic_review` work items, removes the topic.
- `nexus archive topic <slug>` — show a topic: title, summary, parent, related, member docs (slug + hook).
- `nexus archive topics [--match <q>]` — list topics (optionally filter by keyword match on title/summary — distinct from QMD-on-bodies).

**Links (curated edges)**
- `nexus archive link add <from> <to> --relation <r>` — add a typed link to `from`'s `links:`.
- `nexus archive link remove <from> <to>` — remove a link.

**Querying (the two-pronged recall + traversal model)**
- `nexus archive query "<q>" [--no-breadcrumbs] [-n N]` — recall mode. Shells out to `qmd query`, then for each hit returns the doc's frontmatter-summary view (slug, title, summary, topics, links). Also lists topics whose member docs appear in hits. **No bodies, no snippets, no LLM synthesis.**
- `nexus archive search "<q>" [-n N]` — raw QMD search (BM25 + vector, no enrichment). Use when you specifically want QMD's view.
- `nexus archive index [--regenerate]` — print the current `index.toml` (or regenerate it from disk). Entry point for systematic traversal.
- `nexus archive show <slug> [--body]` — display frontmatter only by default; `--body` includes the markdown.
- `nexus archive related <slug>` — direct neighbours: `links:` (forward), backlinks (computed), `mentions`, topic-siblings (small set per topic).
- `nexus archive neighborhood <slug> [--hops N]` — single-call subgraph dump: linked docs, mentions, topic-siblings within N hops, all as frontmatter summaries. Saves the agent N×K calls when it wants breadth.
- `nexus archive recent [--days N]` — docs sorted by `updated` desc, last N days.
- `nexus archive tag <tag>` — docs carrying a tag.

**Outputs (persisted syntheses)**
- `nexus archive output save <slug> --file <out.md>` — validate frontmatter (cites must resolve), persist to `outputs/<slug>.md`, enqueue `pending_review` work item.
- `nexus archive output list [--status pending_review|integrated|archived]` — list outputs.
- `nexus archive output show <slug> [--body]` — display.
- `nexus archive output integrate <output-slug> --into <doc-slug>` — fold output into an existing doc (archivist judgment): appends provenance, updates doc, marks output `integrated`.
- `nexus archive output split <output-slug> --create <slug-a>,<slug-b>` — split into multiple new docs (each created via subsequent `write` calls; the split command pre-stages the work items).
- `nexus archive output archive <output-slug>` — mark `archived` (synthesis was redundant, no integration needed).

**Maintenance & integrity**
- `nexus archive work list [--kind ...]` — show the work queue.
- `nexus archive maintain` — entry point for the archivist's maintenance session. Surfaces queue + recommended order (see Maintenance below). Does *not* auto-run agent work — it's a session scaffold; the agent does the actual mutations via the other commands.
- `nexus archive integrity` — one-shot scan: walk every wiki + topic frontmatter, verify all `links`, `topics`, `mentions`, `cites` resolve. Print broken refs and enqueue them.
- `nexus archive reindex` — regenerate `index.toml`; trigger `qmd update --collections nexus-archive`.

### Graph integrity rules

The CLI is the only thing that mutates frontmatter. Every mutation maintains these invariants:

1. **Slug uniqueness** — slug is the primary key. `write` rejects collisions; `doc rename` is the only path to change one.
2. **Bidirectional consistency** — when a doc lists topic `T`, the topic file gets the doc in its `[[docs]]` list. When a doc is deleted, it's removed from all topic member lists.
3. **Reference integrity on rename** — `doc rename <old> <new>` rewrites *every* reference: other docs' `links:`, `mentions:`, topics' `[[docs]]` slugs, outputs' `cites`. Atomic — either all rewrites succeed or none do.
4. **Reference integrity on delete** — affected docs' references are stripped *and* a `broken_link` work item is enqueued so the archivist can decide whether to repoint the link to a different doc.
5. **Mention auto-sync** — on `write`/`doc update`, the CLI extracts `[[slug]]` patterns from the body and replaces the doc's `mentions:` field. Body prose is the source of truth for mentions; `links:` remain agent-curated.
6. **Topic membership auto-sync** — derived from each doc's `topics:` field, written into the topic's `[[docs]]` list. `hook` values are preserved across re-syncs unless the doc is removed.
7. **No silent data loss** — every CLI operation prints what it did. Unresolvable references become work items, not errors that block the operation.

### Maintenance — the five jobs

`nexus archive maintain` surfaces a recommended ordering. The archivist works through them:

1. **Output triage** — walk `pending_review` outputs, read their `novelty` field, decide per-output: `integrate` / `split` / `archive`. Cheap, high-value, do it first because it's where new knowledge enters.
2. **Broken-link resolution** — for each `broken_link` work item, decide: repoint to a different doc, drop the link, or accept (mark resolved without action).
3. **Orphan rescue** — for each `orphan` (doc with no topics OR zero inbound links), use `nexus archive query` to find a candidate home; assign topics or add inbound links from related docs.
4. **Stale doc review** — for the oldest N docs past the staleness threshold (configurable in `archive.toml`, default 90 days), re-validate `links:`, refresh `summary` if sources have changed, bump `last_maintained`.
5. **Topic summary refresh** — for each topic with members added/removed since `last_maintained`, regenerate `summary` and refresh per-doc `hook`s.
6. **Contradiction scan** — use QMD to surface semantically-similar doc pairs; archivist checks for disagreements; flags `status: contradicted` and enqueues if found.

Each job is bounded work per run (oldest-first cursor, configurable batch size). Maintenance never tries to do everything in one pass.

### QMD integration — concrete

QMD is shelled out via `subprocess`. `src/utils/archive.py` wraps the calls. `nexus archive setup` does the one-time configuration:

```sh
qmd collection add <abs-path-to-archive>/wiki --name nexus-archive --mask "**/*.md"
qmd context add qmd://nexus-archive "Personal knowledge base wiki entries."
qmd embed
```

The wrapper checks `qmd --version` on first invocation and prints install instructions (`npm install -g @tobilu/qmd` or `bun install -g @tobilu/qmd`) if missing.

`nexus archive search` calls `qmd search "<q>" -c nexus-archive --json -n N`.
`nexus archive query` calls `qmd query "<q>" -c nexus-archive --json -n N`, then enriches each hit with the doc's frontmatter summary (parsed from disk).

After `write`/`doc update`/`doc delete`/`doc rename`, queue a QMD update. For v1, the simplest approach: invoke `qmd update --collections nexus-archive` synchronously at the end of the command. If this proves too slow, defer to a `--no-qmd-update` flag and rely on `nexus archive reindex` for batched updates. Decide during implementation based on observed latency.

### `agent_instructions.md` — what the archivist reads

Following the `learn`/`self`/`manage` pattern, structured as:

1. **Identity and role** — "You are the archivist of Benjamin's second brain. You maintain a knowledge graph of structured wiki entries, topics, and outputs."
2. **The model** — flat wiki, multi-valued topics, three search modes (recall, structural entry, traversal), the librarian metaphor.
3. **State management rules** — NON-NEGOTIABLE: every mutation goes through a CLI command; never hand-edit frontmatter or topic files; always validate slugs before referencing.
4. **Three invocation modes** — direct, subagent, scheduled. Wake-up checklist for each.
5. **The wake-up checklist** — onboard, scan work queue, ask user (direct mode) or proceed to assigned task (subagent/scheduled).
6. **Composing a wiki entry** — workflow for `add`: read raw, scan QMD recall hits, decide (new doc vs. augment existing), draft frontmatter, write, verify.
7. **Maintenance workflow** — the five jobs in order; what to look for in each.
8. **Output triage decision tree** — when to integrate, split, archive.
9. **Topic management** — when to create a new topic vs. reuse; how to write good summaries and hooks.
10. **Rules** — paths (absolute), file creation locations (only inside `archive/`), no silent assumptions.
11. **Available commands** — full reference.

### Onboard output structure

Mirrors `learn`/`self`/`manage` onboard:

1. Pause check (skip if `nexus pause archive` active — pause integration is in `src/commands/pause/`; check existing pattern).
2. Intro: "You are the archivist…" with task-specific framing if `--task` provided.
3. Archive state: doc count, topic count, pending outputs, orphans, stales, broken links, last reindex, last QMD update.
4. Top-level index summary (top 5–10 topics by doc count, with summary lines).
5. Recent activity (last N docs added or updated).
6. Work queue summary (top items per kind, filtered by `--task` if relevant).
7. **PATHS** section — absolute paths for: `archive/`, `wiki/`, `topics/`, `raw/`, `outputs/`, `index.toml`, `work.toml`. Stern reminder to never create files outside these.
8. Agent instructions (full or task-filtered subset of `agent_instructions.md`).
9. **ACTION REQUIRED** footer — "Read the above and respond to the user/parent agent NOW."

### Configuration files

**`archive/archive.toml`** — user-edited:

```toml
# Topics the user is most interested in (used by archivist when choosing
# whether to create a new topic for a borderline doc).
interests = ["machine learning", "elixir", "rust", "philosophy of mind"]

[maintenance]
staleness_days = 90        # doc considered stale after this many days
batch_size = 10            # max items per maintenance job per run

[qmd]
collection_name = "nexus-archive"
default_recall_n = 10      # default -n for `query`/`search`
```

**`archive/state.toml`** — CLI-mutated:

```toml
last_reindex = 2026-04-17T13:47:00
last_qmd_update = 2026-04-17T13:47:00
schema_version = 1

[[renames]]
old = "old-slug"
new = "new-slug"
at = 2026-04-17T13:47:00
```

**`archive/work.toml`** — CLI-mutated, archivist-drained:

```toml
[[items]]
kind = "broken_link"           # broken_link | pending_output | orphan | stale | contradiction | needs_topic_review
slug = "attention-is-all-you-need"
detail = "links to deleted slug 'foo-bar'"
created = 2026-04-17T13:47:00

[[items]]
kind = "pending_output"
slug = "why-transformers-replaced-rnns"
created = 2026-04-15T10:00:00
```

`orphan` and `stale` items are *computed on the fly* from disk (cheap walk over frontmatter). They appear in `work list` output but aren't persisted. `broken_link`, `pending_output`, `contradiction`, `needs_topic_review` are persisted because they record specific decisions or moments.

### Pause integration

Add `archive` to `src/models/pause.py` PauseConfig. Update `src/commands/pause/main.py` to recognise `archive`. Onboard checks pause status and exits early if active (mirroring `learn`/`self`/`manage`).

### Implementation phases (for breaking into tasks)

Suggested order — each phase is independently testable:

1. **Foundations**: models (`DocFrontmatter`, `TopicConfig`, `OutputFrontmatter`, `WorkItem`, `ArchiveConfig`, `ArchiveState`), `src/utils/archive.py` helpers (paths, slug generation, frontmatter parse/write, `[[slug]]` extraction), `setup` command, `archive.toml`/`state.toml` defaults, pause integration.
2. **Topics**: `topic new/update/delete/show`, `topics list`, member auto-sync.
3. **Wiki docs**: `write`, `doc update/rename/delete`, `show`, frontmatter validation, `links` add/remove, mention auto-sync, broken-link enqueueing.
4. **Index & traversal primitives**: `index` (read + regenerate), `recent`, `tag`, `related`, `neighborhood`.
5. **QMD wiring**: `setup` registers collection + context, `search`, `query` (with frontmatter enrichment), QMD update on mutation.
6. **Ingestion**: `add` (hash, store raw, sidecar metadata, recall + topic candidates, structured next-step output for the agent).
7. **Outputs**: `output save/list/show/integrate/split/archive`, work queue integration.
8. **Maintenance & integrity**: `work list`, `maintain` (scaffold + ordering), `integrity` scan, `reindex`.
9. **Onboard & agent instructions**: `onboard` with `--task`, full `agent_instructions.md`.

### Out of scope

- `raw/unprocessed/` and pre-processing pipelines (PDFs, HTML, web crawling). Future spec.
- Cron / scheduled wake-up integration. The CLI is designed to *accommodate* it; actual scheduling is external.
- Subagent invocation protocol from other agents (e.g. how OpenClaw's `learn` agent calls into archive). Out-of-band; the archive doesn't care how it's invoked.
- MCP server for the archive. Future.
- Graph viewer / visualisation. Future.
- Multi-user concurrency. Single-user, single-machine for v1.

## Success Criteria

- `nexus archive setup` produces a working archive directory and a registered QMD collection.
- `nexus archive add path/to/source.md` results in a `raw/<hash>.md` file, sidecar metadata, and structured agent instructions printed to stdout — including absolute paths, the QMD recall shortlist, candidate topics, and the next command to run.
- A drafted wiki doc committed via `nexus archive write` is validated, persisted, integrated into its topics' member lists, has its mentions auto-extracted, and triggers a QMD update.
- `nexus archive query "<q>"` returns a list of relevant topics (with summary lines) and relevant docs (frontmatter-summary view) — never raw QMD snippets, never doc bodies, never LLM-synthesised prose.
- `nexus archive doc rename <old> <new>` rewrites every reference across the archive atomically.
- `nexus archive doc delete <slug>` flags affected docs and enqueues `broken_link` work items rather than silently dropping references.
- `nexus archive maintain` surfaces an ordered list of pending work and instructs the archivist what to do next.
- `nexus archive onboard` provides everything a fresh archivist session needs: state summary, work queue, paths, agent instructions, ACTION REQUIRED footer. With `--task <…>` it filters appropriately.
- Agent instructions are loaded from `src/commands/archive/agent_instructions.md` (per `agent-instructions-file` memory pattern) and surfaced in onboard output.
- All paths displayed to the agent are absolute. All paths stored in TOML/YAML use the `./` prefix.
- The `archive` directory is registered with QMD as collection `nexus-archive`, and search/query commands return results.
- `nexus pause archive` correctly suspends archivist activity and onboard reflects the pause.

## Notes

- This is intended as the foundation for ~all of the user's agentic memory going forward. Prioritise **structural rigour over ergonomics** wherever they conflict — it should be hard to corrupt the archive, easy to traverse it, and clear what to do next at every step.
- The librarian metaphor is the design north star: the archive should *feel* like a well-organised library, where every shelf has a label, every book has a card, and the catalogue points you to the right neighbourhood. The archivist agent is the librarian; the CLI is the card catalogue and shelving rules.
- QMD is a *recall primitive*, not a query engine. It surfaces candidates; the structured graph is what the librarian actually traverses. If a future, better recall engine appears, swapping it in should mean changing only `src/utils/archive.py` (the QMD wrapper).
- `wiki/` is flat by design. Resist the temptation to add subfolders. Topics handle the organising; depth comes from topic-to-topic relations.
- No subsections. A topic can have a `parent` topic and `related` topics; that's it. If a future need arises for tighter hierarchy, revisit — but don't pre-build for it.
- Frontmatter is the source of truth. Bodies are prose. The CLI keeps frontmatter consistent; the agent writes bodies.
- The work queue is the contract between the CLI (which surfaces problems) and the archivist (which solves them). Keep it simple, well-typed, and human-readable.
