---
title: Task CRUD commands
status: todo
created_at: '2026-03-31T09:14:21.428232'
updated_at: '2026-03-31T09:14:21.428232'
completed_at: null
---
Create src/commands/management/task.py with typer app:

Commands:
- task new 'title' — create task TOML in management/tasks/<slug>.toml, add to index. Options: --due (date or datetime string), --recur (3-field cron string), --parent (slug or name — resolve via index, create slug/ dir if needed, set has_subtasks=true on parent), --tag (repeatable), --description
- task list — list active tasks in tree view (show hierarchy via indentation). Options: --tag (filter), --due today|week|month (filter by due window), --flat (no tree, just flat list)
- task show <slug> — show full task details + subtask tree if has_subtasks
- task complete <slug> — if has_subtasks, check all subtasks completed (or --force). For recurring tasks: record completion, calculate and update next due date, do NOT move to completed. For non-recurring: move to completed/ (task + subtask dir), remove from index recursively
- task edit <slug> — update task fields. Options: --due, --description, --tag (add), --remove-tag, --status. Update last_modified on any change
- task delete <slug> — confirm, then delete task + subtask dir, remove from index recursively

Patterns: use typer.echo() for output, typer.confirm() for destructive ops, raise typer.Exit(1) on errors. Use resolve_slug() from utils for slug arguments.