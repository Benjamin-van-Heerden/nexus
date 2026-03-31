---
title: End-to-end testing
status: todo
created_at: '2026-03-31T09:27:34.357214'
updated_at: '2026-03-31T09:27:34.357214'
completed_at: null
---
Test the full management system end-to-end using the nexus CLI:

1. Task lifecycle:
   - Create a top-level task with due date and tags
   - Create subtasks with --parent flag (2 levels deep)
   - Verify index.toml is correct after each operation
   - List tasks (tree view, flat view, filtered by tag, filtered by due window)
   - Show a task with subtasks
   - Complete leaf subtask, then parent (verify guard on incomplete subtasks)
   - Verify completed tasks moved to completed/ with correct structure
   - Delete a task with subtasks (verify cleanup)

2. Recurring tasks:
   - Create recurring task (weekly meeting: '* * 1')
   - Complete it — verify it stays active with updated next due
   - Create birthday-style recurrence ('15 3 *')

3. Contacts:
   - Create contact with all fields including birthday
   - List contacts, show details
   - Edit contact (add info key)
   - Verify birthday shows up in upcoming command

4. Onboard:
   - Run nexus manage onboard with mix of overdue, due today, upcoming, recurring, and open tasks
   - Verify all sections render correctly

5. Google Calendar (if auth is set up):
   - Run auth flow
   - Run sync, verify events pull through
   - Create task with due date, sync, verify it appears in gcal

Fix any bugs found during testing.