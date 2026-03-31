---
title: Onboard and upcoming commands
status: todo
created_at: '2026-03-31T09:20:55.549090'
updated_at: '2026-03-31T09:20:55.549090'
completed_at: null
---
Create src/commands/management/onboard.py and add 'upcoming' to main.py:

onboard command — full context dump for agents. Output sections in order:
1. Overdue tasks: due date passed, not completed, not recurring. Show name, due date, how many days overdue
2. Due today: tasks due today
3. Due this week: tasks due in next 7 days
4. Upcoming birthdays: scan contacts/ for birthdays in next 30 days. Show name, date, age if birth year known
5. Upcoming recurring: calculate next occurrence for all recurring tasks, show those within 14 days
6. Open todos: tasks with no due date (not recurring, not completed)
7. Task tree: hierarchical view of ALL active tasks with indented subtasks, status markers
8. Agent instructions: read and print src/commands/management/agent_instructions.md

upcoming command — lighter version, just sections 1-5 from onboard. Useful for quick daily check. Add --days option to control the lookahead window (default 14).

Also create src/commands/management/agent_instructions.md with instructions for the OpenClaw agent on how to use the management commands, following the pattern of src/commands/learn/agent_instructions.md.