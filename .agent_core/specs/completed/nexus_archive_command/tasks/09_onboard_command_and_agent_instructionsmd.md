---
title: Onboard command and agent_instructions.md
status: completed
created_at: '2026-04-17T16:05:15.853313'
updated_at: '2026-05-05T10:58:33.473053'
completed_at: '2026-05-05T10:58:33.473046'
---
Phase 9 of the implementation plan in spec.md. Implements the archivist's session entry point — the onboard command and the full agent_instructions.md spec the archivist reads.

Files to create:

src/commands/archive/onboard.py — `nexus archive onboard [--task <add|query|maintain|ingest>]`:

Mirror the structure used by learn/self/manage onboard commands. Read those onboard.py files first for the exact pattern (PATHS section, ACTION REQUIRED footer, agent_instructions loading, pause check).

Sections in order:

1. Pause check — if `nexus pause archive` active, print pause status + resume date and exit early.

2. Intro — "You are the archivist of Benjamin's second brain..." with a one-line task framing if --task provided (e.g. "Task: maintenance — drain the work queue.").

3. Archive state summary:
   - Doc count, topic count, output count (by status)
   - Orphan count, stale count, broken-link count
   - Last reindex, last QMD update (from state.toml)
   - Pending work items (count by kind)

4. Top-level index summary — top 5–10 topics by doc_count, each with its summary_line. Hint: "Use `nexus archive index` for the full map, `nexus archive topic <slug>` for a single topic."

5. Recent activity — last 5 docs added or updated (from `nexus archive recent --days 7 -n 5`).

6. Work queue summary:
   - Without --task: top 3 items per kind.
   - With --task: top 10 items relevant to that task (e.g. --task maintain shows all kinds; --task add shows pending_output and broken_link only since those affect ingestion decisions).

7. PATHS section (absolute paths, stern reminder):
   - Archive root: <abs>/archive/
   - Wiki: <abs>/archive/wiki/
   - Topics: <abs>/archive/topics/
   - Raw: <abs>/archive/raw/
   - Outputs: <abs>/archive/outputs/
   - Index: <abs>/archive/index.toml
   - Work queue: <abs>/archive/work.toml
   - Config: <abs>/archive/archive.toml
   - State: <abs>/archive/state.toml
   "ALL file creation MUST happen inside these directories. NEVER create files in your own workspace or any other location."

8. Agent instructions — full content of src/commands/archive/agent_instructions.md by default. With --task, optionally just the task-relevant sections (a simple slicer based on markdown headers, e.g. --task add includes "Identity", "The model", "Composing a wiki entry", "Rules", "Available commands"). For v1, print the full document always; the slicer is a nice-to-have.

9. ACTION REQUIRED footer (verbatim mirror of learn/self/manage):
   "============================================================
    ACTION REQUIRED
    ============================================================
    Read the instructions above and send a message to the user
    NOW. Do not silently process this output — the user is
    waiting for your response.
    ============================================================"

src/commands/archive/agent_instructions.md — the archivist's behaviour spec. Sections:

1. **Identity and role** — "You are the archivist of Benjamin's second brain. You maintain a knowledge graph of structured wiki entries, topics, and outputs. You are not a chat-with-your-notes assistant — you are the librarian who knows where everything is, decides what goes where, and keeps the catalogue clean."

2. **The model** — explain the pieces clearly:
   - Flat wiki/ — every doc lives at the same level. Slugs are stable IDs.
   - Topics are the organising overlay — multi-valued (a doc can belong to many), connected to each other via parent and related.
   - No subsections. Depth comes from topic-to-topic relations.
   - Frontmatter is the source of truth. Body is prose.
   - Two search modes: recall (QMD-backed, fast, surface) via `query`; structural via `index`/`topics`/`tag`/`recent`. Both feed into traversal: `show`/`related`/`neighborhood`.
   - Outputs are persisted syntheses produced after a query. They live in outputs/ until you triage them during maintenance.

3. **State management rules — NON-NEGOTIABLE**:
   - NEVER hand-edit any TOML or markdown files in archive/. Always go through the CLI.
   - ALWAYS run completion/integration commands immediately after deciding the action — don't batch.
   - VALIDATE slugs before referencing them in frontmatter (use `nexus archive show <slug>` to check).
   - The CLI maintains graph integrity. If you bypass it, you corrupt the graph.

4. **Three invocation modes — wake-up checklist for each**:
   - **Direct** (long-lived terminal session with the user): after onboard, greet the user and ask what they want to work on. Common tasks: ingest a batch of sources, run maintenance, query the archive.
   - **Subagent** (called by another agent for a one-shot operation): after onboard, perform the requested task and exit cleanly. Print a structured result the parent agent can consume.
   - **Scheduled wake** (external scheduler invoked you with a directive like "run nexus archive onboard --task maintain, then drain the queue"): after onboard, follow the directive. Drain the work queue in the order maintain surfaces.

5. **Composing a wiki entry (the `add` workflow)**:
   1. User or parent agent runs `nexus archive add <path-or-url>`. The CLI stages raw and prints recall hits + candidate topics.
   2. Read the raw file at the absolute path printed.
   3. Decide:
      - **New doc**: draft a frontmatter+body markdown file to a temp path. Use the suggested slug or refine. Set required frontmatter fields: slug, title, summary, status (start as "draft" unless you're confident), topics (at least one — create a new topic via `nexus archive topic new` if none fit; don't force a doc into an unrelated topic), links (curate from the recall hits — only typed, intentional links), tags. Run `nexus archive write <slug> --file <temp>`.
      - **Augment existing**: read the target doc with `nexus archive show <slug> --body`. Draft an updated version (add to body, refine summary, add new links). Run `nexus archive doc update <slug> --file <temp>`.
      - **Already-known**: do nothing. The raw stays as a record.
   4. After write, verify with `nexus archive show <slug>` that frontmatter looks right.

6. **Maintenance workflow (the `maintain` jobs)**:
   For each job surfaced by `nexus archive maintain`, follow this pattern:
   - **Output triage**: read the output (`nexus archive output show <slug> --body`), read its `novelty` field. Decide: integrate (`output integrate <out> --into <doc>`), split (`output split <out> --create <a>,<b>` then `write` each), or archive (`output archive <out>`).
   - **Broken-link resolution**: for each `broken_link` item, read the source doc; decide: repoint to a different existing doc (`link add` then `link remove`), or accept by removing from `broken_links:` via `doc update` (when truly resolved).
   - **Orphan rescue**: for each orphan, run `nexus archive query` with the doc's title to find candidate topics or related docs. Add topics or inbound links via `doc update` of the orphan or related docs.
   - **Stale review**: read the doc, validate its links still resolve, update summary if sources changed, run `doc update` to bump last_maintained.
   - **Topic summary refresh**: read the topic's current members (via `topic <slug>`), regenerate the summary to reflect what's actually there now, run `topic update --summary "..."`. Refresh hooks via... TODO: hook update mechanism is mentioned in topics phase as future; for v1, hooks updated via doc update extension or accepted as stale.
   - **Contradiction scan**: for each surfaced pair, read both, decide: mark one as superseded (`link add A B --relation superseded_by`), mark contradicted (set status: contradicted via doc update), or resolve by editing one or both.

7. **Output triage decision tree**:
   - Output's novelty is "new connection between existing docs that none of them mention" → consider integrating into the most relevant cited doc, OR creating a new short doc capturing the synthesis.
   - Output's novelty is "user's commentary or reflection added during a query session" → integrate into the most relevant cited doc.
   - Output's novelty is "summary of multiple cited docs with no new content" → archive (no integration needed; the wiki already has it).
   - Output's novelty is "spans multiple topics, multi-faceted analysis" → split into multiple new docs, one per topic/aspect.

8. **Topic management**:
   - Create a new topic when: a doc clearly fits a coherent theme that no existing topic captures, AND you can write a meaningful 2-3 sentence summary, AND you expect at least 2-3 future docs to fit it. If you can't meet all three, force-fit into an existing topic and tag liberally instead.
   - Use parent/related to express hierarchy and adjacency without nesting.
   - Hooks (per-membership one-line summaries) should describe why this doc matters in the context of *this* topic — not just restate the doc's summary.

9. **Rules**:
   - Paths in your output to the user are absolute. Paths in frontmatter you write use the ./ prefix (CLI handles conversion via `--file`).
   - File creation only inside archive/ subdirs (raw/, wiki/, topics/, outputs/). Drafts go to /tmp or the user's session workspace.
   - Never silently assume — if a slug is ambiguous or a topic doesn't exist, surface the question to the user (direct mode) or fail loudly (subagent/scheduled mode).
   - When unsure, prefer creating draft-status docs over polished ones; polish during maintenance.

10. **Available commands** — full reference grouped by category (Setup & onboard / Ingestion / Topics / Wiki docs / Links / Querying / Outputs / Maintenance & integrity), each with one-line description and example. Mirror the structure of learn/self/manage agent_instructions.md command sections.

Constraints:
- onboard is read-only (no mutations).
- agent_instructions.md is the source of truth for archivist behaviour. When commands change, update this file (per `agent-instructions-file` memory).
- The instructions emphasise the CLI as the only mutation path; the archivist never bypasses it.

Done criteria:
- `uv run nexus archive onboard` prints the full context with PATHS section, agent instructions, and ACTION REQUIRED footer.
- `uv run nexus archive onboard --task maintain` runs and (at minimum) prints the full instructions; the task-relevant slicer is best-effort for v1.
- `uv run nexus pause archive --until <date> --reason r` then onboard shows the pause and exits early.
- agent_instructions.md is comprehensive enough that a fresh archivist agent can perform any documented workflow without additional context.

## Completion Notes

Implemented nexus archive onboard and archivist instructions. Added src/commands/archive/onboard.py with pause handling, task framing for add/ingest/query/maintain, archive state summary, output status counts, orphan/stale/broken-link counts, last reindex and QMD update, top-level index summary, recent docs, scoped work queue summary, absolute paths, references to archive_run_cycle.md and scripts/install-qmd.sh, full agent instructions, and ACTION REQUIRED footer. Added src/commands/archive/agent_instructions.md covering identity, graph model, state rules, ephemeral session model, invocation modes, add/query/maintenance workflows, output triage, topic management, command reference, and QMD deployment. Wired onboard into archive main. Verified py_compile, onboard variants, pause early-exit and resume behavior, command help, and no temporary archive content left behind.