---
title: cli-structure-convention
created_at: '2026-03-27T12:55:14.298486'
updated_at: '2026-03-27T12:55:14.298486'
---
The nexus CLI follows a strict directory-mirrors-commands convention. Each app (e.g. learn) gets its own directory under src/commands/. The app wiring file is always called main.py. Each subcommand gets its own file in that directory. Example: src/commands/learn/main.py wires up topic.py, onboard.py, phase.py, task.py, record.py. Models follow the same pattern under src/models/learn/. When adding a new app (e.g. self-improvement), create src/commands/self_improvement/main.py and scope all subcommands there.