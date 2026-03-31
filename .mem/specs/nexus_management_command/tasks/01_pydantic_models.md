---
title: Pydantic models
status: completed
created_at: '2026-03-31T09:11:50.521270'
updated_at: '2026-03-31T09:53:43.543174'
completed_at: '2026-03-31T09:53:43.543165'
---
Create src/models/management/ with three model files:

- task.py: TaskConfig model with fields: name (str), slug (str), description (str, default ''), status (Literal['todo', 'in_progress', 'completed']), created (date), due (datetime | date | None), completed_at (date | None), tags (list[str], default []), recurrence (str, default ''), gcal_event_id (str, default ''), last_modified (datetime), has_subtasks (bool, default False), parent (str, default '')

- contact.py: ContactConfig model with fields: name (str), slug (str), phone (str, default ''), email (str, default ''), birthday (date | None), relationship (str, default ''), info (dict[str, Any], default {})

- index.py: IndexEntry model with fields: slug (str), name (str), path (str), due (datetime | date | None), parent (str, default ''). ManageIndex model with tasks (list[IndexEntry], default [])

No __init__.py files. Follow existing Pydantic patterns from src/models/learn/.

## Completion Notes

Created src/models/management/ with three model files: task.py (TaskConfig with all fields including recurrence, gcal, subtask support), contact.py (ContactConfig with info dict), index.py (IndexEntry + ManageIndex). Follows existing patterns from src/models/learn/ — no __init__.py, Pydantic BaseModel, Union types with | syntax.