---
title: Onboard and refresh commands
status: todo
created_at: '2026-04-07T15:20:54.666984'
updated_at: '2026-04-07T15:20:54.666984'
completed_at: null
---
Create the core onboard and refresh commands that generate the newspaper.

FILE: src/commands/news/onboard.py

onboard() function:
1. Check pause status (check_pause('news'))
2. Load news config
3. Validate xAI API key is configured (exit with helpful message if not)
4. Load last N daily records for continuity (load_recent_records)
5. Load all active tracked stories
6. Fetch RSS feeds (fetch_all_feeds)
7. Call x_search_global()
8. Call x_search_local()
9. Call web_search_gaps()
10. Call synthesize_newspaper() with all collected data
11. Save digest to news/records/YYYY-MM-DD.toml
12. Update tracked stories that were matched (append developments, update last_updated)
13. Print the newspaper in structured format:
    - Header with date
    - For each category section: category name, then each story cluster with headline, summary, perspectives
    - TRENDING ON X (GLOBAL) section
    - TRENDING ON X (SOUTH AFRICA) section  
    - TRACKED STORIES section — each tracked story with latest development
    - Source count summary
14. Print agent instructions from agent_instructions.md

refresh() function:
1. Check pause
2. Load today's record if it exists
3. xAI x_search calls only (global + SA) — 'what breaking news in the last few hours?'
4. Quick LLM pass to identify genuinely new stories not already in today's record
5. Print only new/breaking content
6. Do NOT overwrite today's record
7. Print condensed agent instructions

The output formatting should use the same style as manage onboard (print('=' * 60), print('-' * 60) for sections, 2-space indentation).

The xAI calls (steps 7-10 in onboard) should be done with appropriate timeouts since they involve network calls. Use httpx timeouts of 30-60 seconds.