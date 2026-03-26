---
created_at: '2026-03-26T15:46:55.052347'
username: benjamin_van_heerden
---
# Work Log - Nexus CLI foundation and architecture design

## Overarching Goals

Design and begin implementing the `nexus` CLI — a typer-based Python tool that powers a personal learning and self-improvement system. The CLI will be used by an OpenClaw agent (via Telegram) to manage daily learning exercises, topic rotation, and self-improvement tracking. The key architectural constraint is that the file system must be self-documenting so that agents waking up cold (via cron) can read directory state and understand what to do.

## What Was Accomplished

### Architecture decisions
- Settled on a sliding-window approach for topic selection (instead of cumulative counts) so that weight changes take effect naturally without needing complex migration logic. A `nexus topic reset` command handles the simple case.
- Learning is a daily agent-driven feed (not session-counted). Small 10-20 min exercises daily, 2x/week larger tasks (up to 2 hours). Incomplete tasks carry over. Exercise and reading remain session-counted under self-improvement.
- Each learn subdirectory gets its own `records/` directory for session logs. `doc.md` files hold stateful/significant context; records are brief notes with frontmatter metadata.
- CLI is named `nexus` (not `learn`) since it covers both learning and self-improvement.

### Files created/modified
- **`pyproject.toml`** — renamed project to `nexus`, added `tomli-w` dependency
- **`scripts/nexus`** — fixed shebang typo, updated to use `uv run --project` pattern pointing to project root
- **`config.toml`** — created with learn weights (c:1, elixir:2, python:4, js-ts:1, rust:4), window_size=8, and self-improvement goals (exercise: 4/week, reading: 5/week)
- **`src/__init__.py`**, **`src/commands/__init__.py`**, **`src/utils/__init__.py`** — package init files
- **`src/utils/paths.py`** — project root and path resolution
- **`src/utils/config.py`** — config.toml loading into dataclasses
- **`src/utils/state.py`** — state.toml read/write with topic history tracking
- **`src/commands/topic.py`** — topic command group with `topic` (show/pick), `topic reset`, `topic history`, `topic weights` subcommands. Implements proportional weighted selection with sliding window.

## Key Files Affected

- `pyproject.toml` — updated name and deps
- `scripts/nexus` — rewritten
- `config.toml` — new
- `src/utils/paths.py` — new
- `src/utils/config.py` — new
- `src/utils/state.py` — new
- `src/commands/topic.py` — new
- `src/__init__.py`, `src/commands/__init__.py`, `src/utils/__init__.py` — new (empty)

## What Comes Next

- **`main.py`** — rewrite as typer app wiring up the topic command group
- **`src/commands/record.py`** — record command for logging learning sessions to `learn/<topic>/records/`
- **Self-improvement commands** — `nexus self log`, `nexus self status`
- **`state.toml`** — not yet created on disk (gets created on first `nexus topic` run)
- **`doc.md` schema** — define what each learn topic's doc.md should contain so agents can orient themselves
- **End-to-end testing** — verify `nexus topic`, `nexus topic weights`, `nexus topic reset` work via the scripts/nexus entrypoint
- **`data/weights.json`** — can be removed now that weights live in config.toml
- **OpenClaw skill definition** — once CLI is stable, define a SKILL.md for the OpenClaw agent
