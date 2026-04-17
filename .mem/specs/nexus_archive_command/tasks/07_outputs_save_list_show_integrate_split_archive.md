---
title: 'Outputs: save, list, show, integrate, split, archive'
status: todo
created_at: '2026-04-17T14:04:24.225292'
updated_at: '2026-04-17T14:04:24.225292'
completed_at: null
---
Phase 7 of the implementation plan in spec.md. Implements the outputs sub-app — persisted syntheses produced by agents and integrated back into the wiki during maintenance.

Files to create:

src/commands/archive/output.py — output sub-app with these commands:

- `nexus archive output save <slug> --file <path>` — persist a synthesis:
  1. Read the file via parse_frontmatter.
  2. Validate against OutputFrontmatter (required: slug, query, status, cites non-empty, novelty).
  3. Verify slug arg matches frontmatter slug; verify slug uniqueness in outputs/.
  4. Verify each `cites:` slug exists in wiki/. If any missing, error out (cites must be valid — outputs are syntheses *of* the wiki, not aspirational).
  5. Set `created` to now if not present; set `status` to "pending_review" by default if not specified.
  6. Write to outputs/<slug>.md atomically.
  7. Enqueue a `pending_output` work item with slug = output slug.
  8. Print summary + ACTION REQUIRED hint: "Output saved. It's on the work queue for archivist triage. Run `nexus archive maintain` to triage now, or it'll be processed in the next maintenance pass."

- `nexus archive output list [--status pending_review|integrated|archived] [--json]` — list outputs. Default: all. Output: slug, query (truncated), status, created, cites count.

- `nexus archive output show <slug> [--body] [--json]` — display an output (mirror `archive show`).

- `nexus archive output integrate <output-slug> --into <doc-slug>` — fold output into existing doc:
  1. Verify output exists with status pending_review.
  2. Verify target doc exists.
  3. Append a provenance note to the doc's `provenance.origin_outputs` list (add the output slug).
  4. Bump doc's `updated` and `last_maintained`.
  5. Set output status to "integrated".
  6. Mark the work item resolved (remove from work.toml).
  7. Print summary. Note: this command does NOT modify the doc's body — that's the agent's job (run `nexus archive doc update` separately with the augmented body if body changes are needed). This command tracks the link and the status.

- `nexus archive output split <output-slug> --create <slug-a>,<slug-b>,...` — pre-stage a multi-doc split:
  1. Verify output exists with status pending_review.
  2. Validate the target slugs don't already exist in wiki/ (these are NEW docs to be created).
  3. Add provenance notes: when the agent later writes wiki/<slug-a>.md etc., they should set `provenance.origin_outputs: [<output-slug>]`. The command itself only emits the next-step instructions:
     "Output split staged. Now create each new doc:
        nexus archive write <slug-a> --file <draft-a.md>
        nexus archive write <slug-b> --file <draft-b.md>
      Each draft should set provenance.origin_outputs: [<output-slug>]."
  4. Mark output status to "integrated" once ALL the listed slugs exist in wiki/. Until then, status remains pending_review and the work item stays. Use a check on subsequent `output show` calls (cheap walk of wiki/).
     Simpler v1 approach: just mark status "integrated" immediately when split is invoked, on faith. The agent is responsible for following through. Document this in the printed instructions.
  5. Remove the work item.

- `nexus archive output archive <output-slug>` — mark archived (synthesis was redundant or didn't warrant integration). Sets status to "archived"; removes work item.

src/utils/archive.py additions:

- output_exists(slug) -> bool
- list_all_outputs(status_filter=None) -> list[OutputFrontmatter]
- mark_work_item_resolved(kind, slug) -> None — remove a matching item from work.toml.

Constraints:
- Outputs reference wiki docs (cites); the dependency goes one way. Don't introduce circular references.
- All status transitions are explicit via the CLI; no automatic state machines.
- The CLI never modifies wiki doc bodies during integrate — body changes are the agent's responsibility via `doc update`.

Done criteria:
- `uv run nexus archive output save my-synthesis --file out.md` validates and persists.
- `uv run nexus archive output list --status pending_review` shows the queue.
- `uv run nexus archive output integrate my-synthesis --into some-doc` updates provenance, status, and removes the work item.
- `uv run nexus archive output split my-synthesis --create new-a,new-b` prints the next-step guidance.
- `uv run nexus archive output archive my-synthesis` cleanly marks archived.