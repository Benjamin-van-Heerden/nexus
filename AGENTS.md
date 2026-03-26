<MEMCONTENT>
# Working with mem

This project uses **mem** for context management and version control in AI-assisted development.

## First Action

The first action in every session is typically to get up to date with the project context:

```bash
mem onboard
```

Be on the lookout for trigger phrases like "Let's get to work", "Let's go" or "Get onboarded". If you see one, run `mem onboard` to get started.

`mem onboard` gives you everything you need: project info, coding guidelines, active specs, tasks, and recent work logs. The onboard output includes all available commands and project state.

## About mem

mem is a CLI tool for managing project context in AI-assisted development.
It uses a file-first, git-native architecture where all data is stored as
markdown files with YAML frontmatter in the .mem/ directory.

**Core concepts:**
- **Specs**: High-level feature specifications (linked to GitHub issues)
- **Tasks**: Concrete work items within a spec
- **Todos**: Standalone work items not tied to a spec (synced with GitHub issues)
- **Memories**: Short, atomic notes about patterns, conventions, or preferences in the codebase
- **Work Logs**: Session records of what was done and what's next

**Key commands:**
- `mem spec new "title"` - Create a new spec
- `mem sync` - Sync the project context with the remote repository. This is a very important command. It runs automatically on onboarding. It is also an essential command that must be ran before a spec can be assigned (this will create an issue on github and make sure the remote knows about the spec).
- `mem spec assign <slug>` - Assign spec to and create worktree. DO NOT ASSIGN SPECS WITHOUT EXPLICIT CONSENT.
- `mem task new "title" "detailed description with implementation notes if necessary"` - Create a task for active spec. Can also be ran with `--spec <slug>` to create a task under a specific spec.
- `mem task complete "title" "detailed notes about what was done"` - Mark task done
- `mem spec complete <slug> "detailed commit message"` - Create PR, mark spec merge_ready
- `mem log` - Create work log for the session. This is an extremely important command that should be ran towards the end of every session. If you feel at any point your context window is becoming too large, suggest creating a log and continuing in a new session.

**Todos (standalone work items):**
- `mem todo new "title" "description"` - Create a todo (also creates GitHub issue with mem-todo label)
- `mem todo list` - List all open todos
- `mem todo claim "title"` - Claim a todo (closes the linked GitHub issue)

**Memories (project-specific notes):**
- `mem memory new "title" "content"` - Create a memory (a short note about a pattern, convention, or preference)
- `mem memory list` - List all memories
- `mem memory show <slug>` - Show memory details
- `mem memory update <slug> "new content"` - Update a memory
- `mem memory delete <slug>` - Delete a memory

**Document search:**
- `mem docs search "query"` - Semantic search across indexed documentation
- `mem docs search "query" -d <slug>` - Search within a specific document
- `mem docs list` - List all documents and their index status
- `mem docs index` - Index new or changed documents

## Memories

Memories are short, atomic notes about patterns, conventions, or preferences in the codebase.
They are shown during onboard so every session has access to accumulated project knowledge.

- **When the user asks you to remember something** — create a memory with `mem memory new "title" "content"`
- **When you notice a useful pattern** — suggest creating a memory, but only create it if the user agrees
- Do not use external memory tools (e.g. Claude Code's auto-memory) — use `mem memory` instead

## Notes

- Do not `cd` into the project directory - your shell is already at the project root
- Do not enter plan mode - `mem` handles planning through specs and tasks
- Do not use external task management tools - use `mem task` instead
- Do not create specs unless prompted - often times we will do work out of spec
- When running any mem command **ALWAYS** allow for at least 60 seconds of execution time (the github api can hang)
- `mem log` is not an interactive command and takes no arguments. When prompted to "Create a log" or "Let's log" you should simply run `mem log` and follow the instructions
- When working in the context of a spec (inside a worktree directory), you are ABSOLUTELY NEVER allowed to perform mutating action on the main repo directory in any way shape or form. No git operations. If any merge or rebase fails inside a spec, you must resolve the issues inside that spec!
- Do not add your name or the fact that you co-authored something to any commit messages. Commit messages should be clean and descriptive, no extra information.
- Do not run `mem onboard` arbitrarily - it's output can be very large and typically within the scope of a session it won't provide any additional information. The purpose of the onboard command is just to sync version control and build *initial* context. No other time is it necessary.
- The outputs produced by the mem commands are to be strictly adhered to. Especially in the cases where mem instructs you to stop and give feedback. This is important to keep a human in the loop.
- When working within a spec, DO NOT CREATE TASKS unless explicitly prompted to do so.
- When you are interrupted by the user with "Stop" or "No" or similar, you must **IMMEDIATELY** stop what you are doing, give a brief explanation of what you were busy with, and wait for further instructions. DO NOT continue working.
</MEMCONTENT>
