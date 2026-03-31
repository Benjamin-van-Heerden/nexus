---
title: End-to-end testing
status: completed
created_at: '2026-03-31T09:27:34.357214'
updated_at: '2026-03-31T15:35:07.734461'
completed_at: '2026-03-31T15:35:07.734454'
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

## Completion Notes

Full e2e testing completed with bugs found and fixed: (1) move_to_completed now preserves directory structure relative to tasks/, (2) subtask completion stays in place — only top-level parent moves the whole subtree, (3) date-only tasks no longer show 'at 00:00', (4) gcal sync: added 30-day lookahead window, birthday event filtering, auto-completion of past events, event metadata extraction (description/location/meeting links), fixed updatedMin RFC3339 format, hardcoded calendar to benjaminvh1997@gmail.com, (5) onboard/refresh: added THIS WEEK section (2-7 days out), strict birthday windows (7,2,1,0), user context, last sync info, condensed refresh instructions, clean date formatting, (6) renamed src/commands/management to src/commands/manage, (7) added refresh command for follow-up sessions.