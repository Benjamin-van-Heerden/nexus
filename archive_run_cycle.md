# Nexus Archive Run Cycle

`archive` is a file-state driven agent. Its source of truth is the archive
directory, generated indexes, the work queue, QMD, and the `nexus archive` CLI.
It should not rely on long-lived conversational memory.

## Session Model

The main archive agent should be ephemeral by default.

Every archive session starts with:

```bash
nexus archive onboard --task <add|query|maintain>
```

Then the agent performs bounded work and exits.

There is no need for a `refresh` command. Unlike `manage`, `self`, and `learn`,
archive does not need conversational continuity. It can reacquire all relevant
state from disk each time it wakes.

Long-lived archive sessions are only useful for direct interactive curation,
for example ingesting a batch of sources with the user present. Even then, the
session should start with `onboard`; if the state gets stale, rerun `onboard`
manually.

## Wake Modes

### 1. Add / Ingestion

Trigger examples:

- User says: "Archive this: <url>"
- User uploads or references a markdown file
- Another agent has a source that should become archive material
- A Telegram note should be preserved

Run:

```bash
nexus archive onboard --task add
nexus archive add <path-or-url>
```

The agent then reads the staged raw file and decides:

- New doc: draft and run `nexus archive write <slug> --file <draft.md>`
- Existing doc update: run `nexus archive doc update <slug> --file <draft.md>`
- Duplicate/redundant: take no wiki action; raw remains as a record

`archive add` never writes to `wiki/` directly.

### 2. Query / Retrieval

Trigger examples:

- User asks: "What do I know about X?"
- Another agent asks archive for relevant context
- `learn`, `self`, or `manage` needs prior knowledge before acting

Run:

```bash
nexus archive onboard --task query
nexus archive query "<question or topic>"
```

Then traverse deliberately as needed:

```bash
nexus archive index
nexus archive topic <slug>
nexus archive show <slug>
nexus archive related <slug>
nexus archive neighborhood <slug>
```

If the query produces a useful synthesis that should be preserved, save it as
an output:

```bash
nexus archive output save <slug> --file <output.md>
```

The output is later triaged during maintenance.

### 3. Scheduled Maintenance

Trigger examples:

- Daily cron wake
- Weekly integrity/reindex wake
- Pending `work.toml` items

Run:

```bash
nexus archive onboard --task maintain
nexus archive maintain --limit 5
```

The agent should work through surfaced items in order:

1. Output triage
2. Broken-link resolution
3. Orphan rescue
4. Stale doc review
5. Topic summary refresh
6. Contradiction scan

Maintenance should be bounded. The archive agent should not try to clean the
entire archive in one wake unless explicitly asked.

## Suggested Scheduling

Daily lightweight wake:

```text
Wake archive.
Run nexus archive onboard --task maintain.
Run nexus archive maintain --limit 5.
Process pending_output and broken_link items first.
If there is no work, report that there is no archive work and exit.
```

Weekly deeper wake:

```text
Wake archive.
Run nexus archive onboard --task maintain.
Run nexus archive integrity.
Run nexus archive reindex.
Run nexus archive maintain --limit 10.
Resolve output triage first, then broken links, then orphans/stales.
Exit when the bounded batch is done.
```

On-demand ingestion:

```text
When the user says "archive this", wake archive immediately.
Run onboard --task add, then archive add.
Classify the source and either write, update, or leave as duplicate raw.
Exit.
```

On-demand retrieval:

```text
When the user or another agent asks an archive-memory question, wake archive.
Run onboard --task query, then query/traversal commands.
Return the result to the caller.
Optionally save an output if there is a novel synthesis.
Exit.
```

## Operating Principles

- Archive is passive by default.
- Archive acts when new information arrives, another agent asks a question, or
  scheduled maintenance finds queued work.
- Archive should not generate daily reports like `manage`, `self`, or `learn`.
- All mutations go through `nexus archive` commands.
- All archive sessions start with `onboard`; no `refresh` command is needed.
- QMD is a runtime dependency. Deployment should install the pinned QMD version
  with `scripts/install-qmd.sh` and persist `~/.cache/qmd`.
