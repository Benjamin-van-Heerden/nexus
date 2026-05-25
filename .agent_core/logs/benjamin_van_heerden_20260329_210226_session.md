---
created_at: '2026-03-29T21:02:26.160966'
username: benjamin_van_heerden
---
# Work Log - Git sync, CLI polish, and JAX learning track setup

## Overarching Goals

Harden the nexus learn CLI for real-world use: add git sync so the system works across machines (agent on Ubuntu, user on Mac), fix sharp edges in command outputs and structure, and stress-test the full topic creation flow by building out a JAX learning track.

## What Was Accomplished

### Git sync (pre/post command hooks)
- Created `src/utils/git_sync.py` with `pre_sync()` (git pull) and `post_sync()` (git add -A, commit with datetime, push — only if changes exist)
- Wrapped `app()` call in `main.py` with pre/post sync
- Fixed `scripts/nexus` shebang from `#!/usr/bin/bash` to `#!/usr/bin/env bash` for macOS/Linux portability

### Topic rotation on onboard
- Extracted `ensure_topic_for_week()` from `topic update` command
- Called it at the start of `onboard` so the topic auto-rotates when a new week starts

### Records moved to subtopic level
- `get_records_dir()` now takes `(topic, subtopic)` instead of `(topic, subtopic, phase)`
- Record files now include YAML frontmatter linking to phase, goal, type, duration, status
- Record description explicitly documents what the USER did, not agent actions — this distinction is critical for the cold-start agent

### Task model overhaul
- Added `created: date`, `completed: date | None`, and `relevant_files: list[str]` to Task model
- `task new` is blocked if there are incomplete tasks from a previous day (dangling task guard)
- `task new` accepts `--file`/`-f` flags for relevant file paths (relative to subtopic dir)
- `task complete` shows remaining tasks and reminds about logging a record

### Goal references made required
- `Goal.reference` is now a required field (non-optional)
- `goal new` takes reference as a positional argument and validates the file exists before creating
- References live at topic level (`learn/<topic>/reference/`) not subtopic level
- `topic new` now creates a `reference/` directory automatically
- `onboard` prints the full content of the current goal's reference document

### --topic and --subtopic overrides on all commands
- `get_active_context()` accepts optional `topic_override` and `subtopic_override`
- Added `--topic` and `--subtopic` flags to: `phase new/complete/delete/status`, `goal new/complete/delete/set/list/status`, `task new/complete/list`, `record`
- Extracted `_resolve_topic_subtopic()` helper in phase.py
- This was needed because you can't set up a new topic's phases without switching `current_topic`

### Setup commands for practical exercises
- Added `setup_commands: list[str]` to `ExerciseTypeConfig` in subtopic model
- `phase new` runs setup commands with `cwd=phase_dir` and injects `$TOPIC`, `$SUBTOPIC`, `$PHASE` as env vars
- Falls back to `mkdir` if no setup commands defined
- Removed spurious practical/theoretical/quiz dirs from `subtopic new` (they belong under phases)

### Practical project naming convention
- For Rust: `cargo new practical` + sed to rename to `practical-rust-python-book-track-{phase}` in Cargo.toml
- For Python/JAX: `uv init practical` + sed to rename to `practical-{TOPIC}-{SUBTOPIC}-{PHASE}` in pyproject.toml
- Uses `$TOPIC`, `$SUBTOPIC`, `$PHASE` env vars injected by phase.py — pure shell, no custom templating
- Fixed existing rust practical dirs (foundations had `name = "practical"`, others had empty dirs — all now have properly named cargo projects with examples/)

### tomli_w multiline strings
- Enabled `multiline_strings=True` on all `tomli_w.dump()` calls (both in `_save_toml` helper and direct calls)
- Prevents description fields from collapsing into single-line `\n` strings

### Command output improvements
- `topic new`: now creates reference/ dir, prints numbered next steps with paths, tells agent to discuss with user
- `subtopic new`: explains setup_commands, env vars, and exercise type configuration
- `phase new`: explains that reference docs must exist before creating goals, shows reference path
- `task complete`: reminds about logging a record
- `goal new`: validates reference exists, shows absolute path

### Agent instructions rewrite
- Complete rewrite of `src/commands/learn/agent_instructions.md`
- Added decision tree for what to do on onboard
- Added full "Setting up a new learning track" section (topic → subtopic → phase → goal flow)
- Clarified that records describe USER actions, not agent actions
- Documented dangling task behavior and `--file` flag
- Updated all command signatures

### Pydantic model field ordering fix
- `Goal.reference` (required) moved before `status` (has default)
- `LearnConfig.weights` (required) moved before `window_size` (has default)

### JAX learning track created
- `learn/jax/topic_info.md` — background, end goal (transformer + DeepSeek from scratch + Flax rebuild), approach
- `learn/jax/from-scratch/subtopic_info.md` — learning plan, phases, resources
- `learn/jax/from-scratch/subtopic.toml` — exercise type descriptions and setup_commands for all three types
- 5 phases created: foundations, neural-net-primitives, attention-and-transformers, deepseek-moe, flax-rebuild
- 6 reference documents for foundations goals in `learn/jax/reference/`
- 6 goals created for foundations phase, each with validated reference

### Rust track updated
- `learn/rust/topic_info.md` — rewritten with async Rust end goal and two-track approach
- `learn/rust/python-book-track/subtopic_info.md` — expanded with learning context
- `learn/rust/python-book-track/subtopic.toml` — added setup_commands for cargo, improved descriptions with examples
- Fixed all phase.toml reference paths from `../../reference/` to `reference/` (now relative to topic dir)
- Fixed all practical Cargo.toml names to `practical-rust-python-book-track-{phase}`

## Key Files Affected

- `main.py` — pre/post git sync wrapping
- `src/utils/git_sync.py` — new file, git pull/commit/push
- `src/utils/learn.py` — `get_active_context` overrides, `get_records_dir` at subtopic level, `multiline_strings=True`
- `src/utils/paths.py` — unchanged but referenced
- `src/models/learn/phase.py` — Task model (created, completed, relevant_files), Goal.reference required, field ordering
- `src/models/learn/subtopic.py` — ExerciseTypeConfig.setup_commands
- `src/models/learn/learn.py` — field ordering fix
- `src/commands/learn/phase.py` — setup_commands execution, env vars, --topic/--subtopic flags, improved output
- `src/commands/learn/goal.py` — required reference arg, topic dir resolution, --topic/--subtopic flags
- `src/commands/learn/task.py` — dangling task guard, relevant_files, --topic/--subtopic flags, record reminder
- `src/commands/learn/record.py` — frontmatter, --type flag, --topic/--subtopic flags, docstring clarity
- `src/commands/learn/topic.py` — ensure_topic_for_week extracted, reference/ dir creation, improved output
- `src/commands/learn/subtopic.py` — removed exercise dirs from new, improved output, multiline_strings
- `src/commands/learn/onboard.py` — topic-level references, subtopic-level records, reference content printing
- `src/commands/learn/agent_instructions.md` — complete rewrite
- `scripts/nexus` — shebang fix
- `learn/jax/**` — full topic/subtopic/phase/goal structure
- `learn/rust/**` — updated topic_info, subtopic_info, subtopic.toml, all phase.toml references, all Cargo.toml names

## Errors and Barriers

### uv workspace conflicts
When `uv init practical` is called in multiple phases, all pyproject.toml files get `name = "practical"` which causes a uv workspace member name collision. Fixed by using sed + env vars to rename to `practical-{TOPIC}-{SUBTOPIC}-{PHASE}` after init.

### cargo new vs cargo init
`cargo new` fails if the directory already exists. For fixing existing empty practical dirs, had to use `cargo init --name ...` instead. For new phases, `cargo new` is correct since `phase new` creates a fresh directory.

### sed portability
Using `sed -i ''` (macOS syntax). This will need attention for the Ubuntu agent — GNU sed uses `sed -i` without the empty string argument. Not yet resolved.

## What Comes Next

- **Test task workflow end-to-end**: create tasks with --file flags, complete them, verify dangling task guard works, verify records are created correctly. This is untested.
- **Create async-book track for Rust**: `learn/rust/reference/async-book/` already has all reference material. Create a new subtopic, phases, and goals. This will be a smoother test of the full flow since reference docs already exist.
- **sed portability**: the setup_commands use macOS `sed -i ''` syntax. Need to handle GNU sed on Ubuntu (the agent's machine). Could use a portable pattern or detect OS.
- **SKILL.md for OpenClaw**: once the CLI is stable, define the skill so the agent can be wired up via Telegram.
- **Self-improvement system**: similar architecture for exercise/reading tracking under `src/commands/self_improvement/`.
- **Stale file cleanup**: old config.toml may still have outdated sections.
