---
created_at: '2026-03-30T19:22:44.620830'
username: benjamin_van_heerden
---
# Work Log - Task workflow testing, path convention overhaul, and Elixir/Rust track setup

## Overarching Goals

Test the nexus learn CLI end-to-end (task creation, completion flow), fix bugs discovered during testing, establish a consistent path convention for the entire project, and scaffold new learning tracks (Elixir OTP, Rust async-book).

## What Was Accomplished

### Bug fixes
- **TOML serialization crash**: `Task.completed = None` caused `tomli_w` to fail because TOML has no null type. Fixed by adding `exclude_none=True` to all `model_dump()` calls in `src/utils/learn.py`.
- **Git sync data corruption**: `pre_sync()` pulled a stale remote version of `learn.toml` that had old weights (c, elixir, python, js-ts), which caused topic rotation to pick `python` (no directory). The `post_sync()` then committed and pushed the corrupted state. Recovered manually.

### Path convention overhaul
Replaced the inconsistent path storage (goal references relative to topic dir, task files relative to subtopic dir) with a single universal convention: **all stored paths use `./` prefix, relative to repo root**.

- `src/utils/path_resolution.py` — updated `resolve()` to handle `./` prefix, added `to_stored_path()` for converting any path to the storage convention
- `src/commands/learn/goal.py` — stores references as `./learn/<topic>/reference/...`, uses `resolve_str()` for display
- `src/commands/learn/task.py` — stores relevant_files as `./learn/...`, uses `resolve_str()` for display
- `src/commands/learn/onboard.py` — uses `resolve_str(goal.reference)` directly instead of manual topic_dir joins
- `src/commands/learn/phase.py` — updated output messages to show `./` convention
- Updated all TOML data: JAX foundations phase.toml (6 references + 1 relevant_file), all 4 Rust python-book-track phase.toml files (also fixed stale `src/` in paths from book unnesting)
- `src/commands/learn/agent_instructions.md` — updated all path examples and conventions
- Updated `mem` memory `relative-paths-and-resolve`

### Removed stale subtopic `reference` field
Removed unused `reference: str = ""` from `SubtopicConfig` model and all 3 subtopic.toml files. References belong on goals, not subtopics.

### Rust async-book track
Created full async-book subtopic under rust with 4 phases and 15 goals:
- **how-async-works** (5 goals): Future trait, Poll, Pin/Unpin, state machines (ch01-ch05)
- **ecosystem** (5 goals): building futures, executors, Tokio, async traits (ch06-ch10)
- **production** (4 goals): streams, pitfalls, production patterns, exercises (ch11-ch14)
- **capstone** (1 goal): async chat server (ch16)

Exercise type descriptions include tokio dependency notes, async test patterns, and Send/Sync reasoning for quizzes. Updated `topic_info.md` with future bitcoin and sqlite CodeCrafters tracks.

### Elixir OTP track
Created elixir topic (weight 2) with full OTP subtopic:
- **otp-foundations** (3 goals): behaviours, functional cores/CRC, GenServer callbacks
- **abstractions-and-supervision** (2 goals): links/monitors, supervisors/child specs/restart strategies
- **advanced-patterns** (3 goals): dynamic supervisors/registries, design concepts/backpressure, tasks/agents
- **capstone** (3 goals): word ladder project (functional core → GenServer → dynamic supervisor)

11 reference documents written covering all OTP concepts. Each phase has a mix project (`mix new practical`) for exercises. Setup commands handle Elixir's underscore-only app naming by converting hyphens with `tr`.

### JAX exercise file
Created `learn/jax/from-scratch/foundations/practical/examples/2026-03-30.py` — JAX mental model exercises (array creation, slicing, `.at[].set()` updates) with stub functions and assertions.

## Key Files Affected

- `src/utils/learn.py` — `exclude_none=True` on all `model_dump()` calls
- `src/utils/path_resolution.py` — `resolve()` handles `./`, added `to_stored_path()`
- `src/models/learn/subtopic.py` — removed `reference` field
- `src/commands/learn/goal.py` — `./` path convention for references
- `src/commands/learn/task.py` — `./` path convention for relevant_files
- `src/commands/learn/onboard.py` — simplified path resolution
- `src/commands/learn/phase.py` — updated output messages
- `src/commands/learn/agent_instructions.md` — updated path convention docs
- `learn/jax/from-scratch/foundations/phase.toml` — `./` prefixed paths
- `learn/rust/python-book-track/{foundations,core-concepts,advanced-topics,capstone}/phase.toml` — `./` prefixed paths, fixed stale `src/`
- `learn/rust/topic_info.md` — added bitcoin/sqlite future tracks
- `learn/rust/async-book-track/**` — new subtopic, 4 phases, all phase.toml files
- `learn/elixir/**` — new topic, OTP subtopic, 4 phases, 11 reference docs
- `learn/jax/from-scratch/foundations/practical/examples/2026-03-30.py` — new exercise file

## Errors and Barriers

### Git sync corrupted learn.toml
The `pre_sync()` git pull overwrote local `learn.toml` with a stale remote version containing old weights. Topic rotation then picked a non-existent topic (`python`), and `post_sync()` committed the corrupted state. This was fixed manually but the underlying issue (git sync overwriting local state) is not resolved. The git sync mechanism needs guardrails — possibly checking that selected topics have directories before committing.

### Phase creation leaves partial state on setup_command failure
When `mix new practical --app practical_${PHASE}` failed (hyphen in Elixir app name), the phase directory was created but empty, and not added to subtopic.toml phases. However, retrying `phase new` failed with "already exists". Had to manually `rmdir` before retrying. Phase creation should clean up on failure.

## What Comes Next

- **`nexus management` command** — create a spec for personal calendar, events, todos, birthdays, task management
- **`nexus self-improvement` command** — create a spec for habit tracking (exercise, reading, mental math)
- **C learning track** — flesh out the topic structure (out of spec)
- **OpenClaw integration** — think about how to hook up the nexus CLI on the agent side (SKILL.md, cron triggers)
