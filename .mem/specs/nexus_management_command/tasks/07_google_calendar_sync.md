---
title: Google Calendar sync
status: todo
created_at: '2026-03-31T09:27:19.290527'
updated_at: '2026-03-31T09:27:19.290527'
completed_at: null
---
Create src/commands/management/sync.py with two commands:

auth_google command (wired as 'nexus manage auth google'):
- Read OAuth client credentials from auth/client_secret_221009037075-mscrrhc8b32ad40ang5ha8rd82ivtmuq.apps.googleusercontent.com.json
- Use google-auth-oauthlib InstalledAppFlow.from_client_secrets_file() with scopes=['https://www.googleapis.com/auth/calendar']
- Run flow.run_local_server() to open browser for consent
- Save resulting credentials (with refresh token) to auth/token.json
- Print success message

sync command (wired as 'nexus manage sync'):
1. Load token from auth/token.json. If missing, error with hint to run 'nexus manage auth google'
2. Build Google Calendar service using googleapiclient.discovery.build('calendar', 'v3', credentials=creds)
3. Load sync_state.toml from management/sync/ (last_sync timestamp, calendar_id default 'primary')
4. PULL (gcal -> nexus):
   - Fetch events modified since last_sync using events().list(timeMin=last_sync, updatedMin=last_sync)
   - For events matching existing tasks (by gcal_event_id): compare last_modified timestamps, latest wins
   - For new events: create task with gcal_event_id set, tags=['gcal'], due from event start time
5. PUSH (nexus -> gcal):
   - Find tasks in index with due date set and (no gcal_event_id OR last_modified > last_sync)
   - For tasks without gcal_event_id: create gcal event, store gcal_event_id back on task
   - For tasks with gcal_event_id and last_modified > last_sync: update gcal event
6. Update sync_state.toml with new last_sync timestamp
7. Print summary: N pulled, N pushed, N conflicts resolved

Dependencies needed (advise user, do not install): google-auth-oauthlib, google-api-python-client, google-auth-httplib2

Wire both commands into src/commands/management/main.py.