---
title: App wiring
status: completed
created_at: '2026-03-31T12:00:38.929226'
updated_at: '2026-03-31T15:52:34.858929'
completed_at: '2026-03-31T15:52:34.858924'
---
Wire up the self-improvement app into the nexus CLI.

IMPORTANT CONTEXT: The nexus CLI uses typer. The root main.py adds sub-apps via app.add_typer(). Look at how the learn app is wired in main.py and src/commands/learn/main.py for the exact pattern. Pre/post git sync is already handled in root main.py — no changes needed for that.

**1. Create src/commands/self_improvement/main.py:**
- Create a typer.Typer() instance: app = typer.Typer(help='Self-improvement and habit tracking')
- Add sub-typers for each habit:
  - from src.commands.self_improvement.read import app as read_app -> app.add_typer(read_app, name='read', help='Reading habit tracking')
  - from src.commands.self_improvement.exercise import app as exercise_app -> app.add_typer(exercise_app, name='exercise', help='Exercise habit tracking')
  - from src.commands.self_improvement.math import app as math_app -> app.add_typer(math_app, name='math', help='Mental math practice')
  - from src.commands.self_improvement.learn import app as learn_app -> app.add_typer(learn_app, name='learn', help='Daily learning check-in')
- Add onboard as a direct command: from src.commands.self_improvement.onboard import onboard -> app.command(name='onboard')(onboard)

**2. Update root main.py:**
- Add import: from src.commands.self_improvement.main import app as self_app
- Add typer: app.add_typer(self_app, name='self', help='Self-improvement and habit tracking')
- Place the import and add_typer near the existing learn_app lines

The resulting CLI structure will be:
nexus self onboard
nexus self read [new|list|show|log|complete|history]
nexus self exercise [log|status|history]
nexus self math [generate|log|status|config]
nexus self learn [log|status]

## Completion Notes

Created self_improvement/main.py wiring all sub-apps. Updated root main.py with self_app import and add_typer.