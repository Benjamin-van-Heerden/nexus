---
created_at: '2026-03-27T16:33:50.695138'
username: benjamin_van_heerden
---
# Work Log - Nexus learn CLI: full hierarchy, CRUD, and agent onboarding

## Overarching Goals

Build out the `nexus learn` CLI as a structured, agent-friendly learning management system. The CLI manages a hierarchy of topic → subtopic → phase → goal → task, with all state stored in TOML files. An OpenClaw agent (via Telegram) will use `nexus learn onboard` to get full context and interact with the system through CLI commands.

## What Was Accomplished

### Distributed TOML hierarchy
Replaced the single-file approach with a distributed structure where each level owns its config:
- `learn/learn.toml` — weights, window_size, current_topic, selection history
- `learn/<topic>/topic.toml` — name, current_subtopic
- `learn/<topic>/<subtopic>/subtopic.toml` — name, current_phase, exercise type descriptions, [[phases]]
- `learn/<topic>/<subtopic>/<phase>/phase.toml` — name, current_goal, [[goals]] with nested tasks

### Pydantic models
Created strongly-typed models in `src/models/learn/`:
- `learn.py` — LearnConfig, TopicEntry
- `topic.py` — TopicConfig
- `subtopic.py` — SubtopicConfig, PhaseEntry, ExerciseTypeConfig
- `phase.py` — PhaseConfig, Goal, Task (with type: practical/theoretical/quiz)

### CLI commands (full CRUD at every level)
All commands scoped under `src/commands/learn/` mirroring the CLI structure:
- `topic.py` — new, list, delete, update, reset, history, weights
- `subtopic.py` — new (with deliberation template in subtopic_info.md), set, list, delete
- `phase.py` — new (creates practical/theoretical/quiz dirs), complete (guards on incomplete goals), delete, status
- `goal.py` — new, set, complete (guards on open tasks), delete, list, status
- `task.py` — new (with --type flag), complete, list
- `record.py` — log session records
- `onboard.py` — full context dump for agents

### Agent instructions pattern
Created `src/commands/learn/agent_instructions.md` as central source of truth for agent-facing instructions. The onboard command reads and appends this file. No hardcoded instructions in Python code.

### Path resolution
Created `src/utils/path_resolution.py` with `resolve()` and `resolve_str()`. All paths printed by the CLI are absolute. `nexus resolve-path` command for agent use.

### Rust learning content
- Cloned Microsoft RustTraining python-book and async-book into `learn/rust/reference/`
- Created full phase structure (foundations, core-concepts, advanced-topics, capstone) with goals mapped to book chapters
- Exercise type descriptions in subtopic.toml for practical/theoretical/quiz

### Other
- `setup.sh` — installs uv and rust (non-interactive)
- `scripts/nexus` — entrypoint script using uv run

## Key Files Affected

- `main.py` — typer app entrypoint
- `src/commands/learn/main.py` — learn app wiring
- `src/commands/learn/topic.py` — topic CRUD + rotation
- `src/commands/learn/subtopic.py` — subtopic CRUD with deliberation template
- `src/commands/learn/phase.py` — phase CRUD with guards
- `src/commands/learn/goal.py` — goal CRUD with guards
- `src/commands/learn/task.py` — task management with types
- `src/commands/learn/onboard.py` — agent context dump
- `src/commands/learn/record.py` — session logging
- `src/commands/learn/agent_instructions.md` — agent instructions (central source of truth)
- `src/models/learn/{learn,topic,subtopic,phase}.py` — pydantic models
- `src/utils/learn.py` — TOML traversal and load/save
- `src/utils/paths.py` — path resolution base
- `src/utils/path_resolution.py` — resolve relative to absolute
- `learn/learn.toml` — top-level learn config with weights
- `learn/rust/topic.toml`, `topic_info.md` — rust topic config
- `learn/rust/python-book-track/subtopic.toml`, `subtopic_info.md` — subtopic config
- `learn/rust/python-book-track/{foundations,core-concepts,advanced-topics,capstone}/phase.toml` — phase configs
- `learn/rust/reference/python-book/`, `learn/rust/reference/async-book/` — cloned reference material
- `setup.sh` — environment bootstrap
- `config.toml` — retains self-improvement goals only

## What Comes Next

- **SKILL.md for OpenClaw** — define the skill so the agent can be wired up via Telegram
- **Self-improvement system** — similar architecture (src/commands/self_improvement/) for exercise/reading tracking
- **Stale file cleanup** — config.toml still has old [learn] section, old data/ dir references
- **Async book track** — reference material is cloned but no subtopic structure created yet
- **Testing the full agent loop** — have the OpenClaw agent actually run onboard, create exercises, and interact
- **Weekly balance tracking** — currently counts from phase.toml tasks, could also derive from records for time-based tracking
