---
title: Agent instructions and default sources config
status: completed
created_at: '2026-04-07T15:21:26.242654'
updated_at: '2026-05-05T10:36:44.931571'
completed_at: '2026-05-05T10:36:44.931562'
---
Create the agent instructions file and seed the default sources configuration.

FILE: src/commands/news/agent_instructions.md
Write agent instructions covering:
- Purpose: relay the newspaper output to Benjamin via Telegram
- Onboard flow: run 'nexus news onboard', read output, format for Telegram, send
- Refresh flow: run 'nexus news refresh', relay any breaking/new stories
- Story tracking: when Benjamin says 'keep tabs on X' or 'follow this story', run 'nexus news track "description"'
- Untracking: when Benjamin says 'stop following X', run 'nexus news untrack <slug>'
- Source management: when Benjamin wants to add/remove sources, use the source commands
- Response pattern: present the newspaper, then STOP. No back-and-forth. If Benjamin responds with story tracking requests, execute and confirm.
- The agent should present stories in order of significance, lead with breaking/tracked stories

FILE: news/config.toml (default seed config)
Create a default config.toml with a curated initial source list. Include at minimum:
- Wire/Neutral: Reuters, AP
- US Left/Center-Left: NPR, The Guardian  
- US Right/Center-Right: Fox News, The Hill
- International: BBC, Al Jazeera, DW
- Tech: Ars Technica, TechCrunch, Hacker News
- Science: Nature, Science Daily
- South Africa: News24, Daily Maverick, EWN, TimesLive
- Entertainment: at least 1-2 entertainment feeds

Use real, working RSS feed URLs. Research correct URLs for each source. Some known good ones:
- BBC: http://feeds.bbci.co.uk/news/rss.xml (and category variants)
- NPR: https://feeds.npr.org/1001/rss.xml
- The Guardian: https://www.theguardian.com/world/rss
- Al Jazeera: https://www.aljazeera.com/xml/rss/all.xml
- Ars Technica: https://feeds.arstechnica.com/arstechnica/index
- Hacker News: https://news.ycombinator.com/rss
- Fox News: check for their RSS feeds (they have them at moxie.foxnews.com or similar)

Set xai_model = 'grok-3' as default. The user will configure XAI_API_KEY separately.

Also create empty directories: news/records/ and news/stories/ (with .gitkeep files if needed).

## Completion Notes

Added src/commands/news/agent_instructions.md covering daily onboard, refresh, story tracking/untracking, direct news/config.toml source management, editorial calibration, and the present-then-stop response pattern. Seeded news/config.toml with live-tested RSS sources across US left/right politics, international, economics, technology, science, entertainment, and South Africa; configured grok-4.3, RSS entry caps, freshness filtering, and the user's editorial profile. Verified with uvx ty check across the touched news/root/pause files, plus a focused uv run python check that loads config, performs a capped RSS fetch, confirms agent instructions exist, and validates news/pause CLI help.