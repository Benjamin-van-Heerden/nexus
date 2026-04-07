---
title: Main app wiring and pause integration
status: todo
created_at: '2026-04-07T15:21:04.410034'
updated_at: '2026-04-07T15:21:04.410034'
completed_at: null
---
Wire up the news app into the nexus CLI and integrate with the pause system.

FILE: src/commands/news/main.py
- Create typer app
- Register: onboard, refresh commands from onboard.py
- Register: source subapp from source.py
- Register: track, untrack, stories commands from track.py
- Follow exact pattern from src/commands/manage/main.py

MODIFY: main.py (project root)
- Import: from src.commands.news.main import app as news_app
- Register: app.add_typer(news_app, name='news', help='Daily news aggregation')

MODIFY: src/commands/pause/main.py
- Add 'nexus pause news --until YYYY-MM-DD [--reason ...]' command
- Follow exact same pattern as existing pause learn/self/manage commands

Note: PauseConfig model change (adding news field) is handled in task 1.