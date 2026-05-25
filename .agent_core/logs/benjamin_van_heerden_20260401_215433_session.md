---
created_at: '2026-04-01T21:54:33.232466'
username: benjamin_van_heerden
---
# Work Log - Manage system improvements: birthday model, tone, weather

## Overarching Goals

Address issues identified in `problems_manage.md` and add weather integration to the manage onboard/refresh commands using the Open-Meteo API.

## What Was Accomplished

### Birthday Model Change
Changed contact birthday from a full `date` (YYYY-MM-DD) to a month-day string (`MM-DD`) with an optional `birth_year` field. This separates the recurring birthday concept from age tracking.

- `ContactConfig.birthday`: `date | None` → `str` (MM-DD format)
- `ContactConfig.birth_year`: `int | None` (new field)
- Updated all CLI commands (new, edit, list, show) to accept `--birthday MM-DD` and `--birth-year YEAR`
- Updated `_get_birthday_reminders()` in onboard.py to parse MM-DD strings and compute age only when birth_year is present
- Updated Steyn van Niekerk's contact TOML to new format

### Tone Changes
Shifted agent instructions from conversational to informational/administrative, per `problems_manage.md`.

- Updated `agent_instructions.md`: removed "Be direct and conversational", added rules about presenting facts not prompts, explicit "Never say things like 'What would you like to tackle first?'"
- Updated refresh condensed instructions to match

### Weather Integration
Added weather display to manage onboard and refresh using Open-Meteo API (free, no API key).

- Created `src/utils/weather.py`: httpx-based weather fetching, WMO code mapping, weather config TOML I/O
- Created `src/commands/manage/weather.py`: `nexus manage weather --latlon "lat,lon" --name "City"` to configure location, `nexus manage weather` to show current conditions
- Added `_print_weather()` helper to onboard.py, called in both `onboard()` and `refresh()`
- Wired weather command into `src/commands/manage/main.py`
- Updated agent instructions with weather command docs

### Memory Created
- `always_use_httpx`: Always use httpx instead of requests for HTTP calls

## Key Files Affected

- `src/models/manage/contact.py` — birthday field changed to str, added birth_year
- `src/commands/manage/contact.py` — CLI updated for MM-DD birthday format and --birth-year option
- `src/commands/manage/onboard.py` — birthday reminders updated, weather display added, tone changes to refresh instructions
- `src/commands/manage/agent_instructions.md` — tone shift, weather command docs
- `src/commands/manage/weather.py` (new) — weather command
- `src/utils/weather.py` (new) — weather utilities (httpx + open-meteo)
- `src/commands/manage/main.py` — registered weather command
- `manage/contacts/steyn_van_niekerk.toml` — updated to MM-DD birthday format
- `manage/weather.toml` (created by CLI) — weather location config

## What Comes Next

- Suppress `VIRTUAL_ENV` warning from uv — add `unset VIRTUAL_ENV` to `~/.zshrc` (stale venv path, no tool in the setup is setting it)
- OpenClaw skill definitions so the Telegram agent can invoke onboard/refresh via cron
- Consider the `nexus pause` todo — it appears implemented but the GitHub issue is still open and should be claimed
