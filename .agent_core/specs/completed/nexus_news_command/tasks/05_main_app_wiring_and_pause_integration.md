---
title: Main app wiring and pause integration
status: completed
created_at: '2026-04-07T15:21:04.410034'
updated_at: '2026-05-05T10:35:06.490331'
completed_at: '2026-05-05T10:35:06.490322'
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

## Completion Notes

Added src/commands/news/main.py and wired the news Typer app with onboard, refresh, track, untrack, and stories commands. Registered the news app in the root main.py as nexus news. Added nexus pause news --until YYYY-MM-DD with optional reason, included news in pause status output and resume validation, and replaced the previous plain-string/type-ignore resume path with an explicit FeatureName Literal cast. Verified with uvx ty check on main.py, src/commands/news/main.py, and src/commands/pause/main.py, plus Typer CliRunner help checks for news, news track, news refresh, and pause news.