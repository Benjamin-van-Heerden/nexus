"""Google Calendar sync and auth commands."""

import tomllib
from datetime import date, datetime, timedelta
from pathlib import Path

import tomli_w
import typer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.models.management.index import IndexEntry
from src.models.management.task import TaskConfig
from src.utils.management import (
    add_to_index,
    get_sync_dir,
    get_tasks_dir,
    load_index,
    load_task,
    save_task,
    slugify,
    update_index_entry,
)
from src.utils.path_resolution import resolve, to_stored_path
from src.utils.paths import get_project_root

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CLIENT_SECRET_PATH = "auth/client_secret_221009037075-mscrrhc8b32ad40ang5ha8rd82ivtmuq.apps.googleusercontent.com.json"
TOKEN_PATH = "auth/token.json"


def _get_abs_path(relative: str) -> Path:
    return get_project_root() / relative


def _load_credentials() -> Credentials | None:
    token_path = _get_abs_path(TOKEN_PATH)
    if not token_path.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds


def _load_sync_state() -> dict:
    sync_dir = get_sync_dir()
    sync_dir.mkdir(parents=True, exist_ok=True)
    state_path = sync_dir / "sync_state.toml"
    if not state_path.exists():
        return {"last_sync": "", "calendar_id": "primary"}
    with open(state_path, "rb") as f:
        return tomllib.load(f)


def _save_sync_state(state: dict) -> None:
    state_path = get_sync_dir() / "sync_state.toml"
    with open(state_path, "wb") as f:
        tomli_w.dump(state, f)


def auth_google():
    """Set up Google Calendar OAuth credentials."""
    client_secret = _get_abs_path(CLIENT_SECRET_PATH)
    if not client_secret.exists():
        typer.echo(f"Client secret not found: {client_secret}")
        typer.echo("Place your Google OAuth client credentials JSON in the auth/ directory.")
        raise typer.Exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
    creds = flow.run_local_server(port=0)

    token_path = _get_abs_path(TOKEN_PATH)
    with open(token_path, "w") as f:
        f.write(creds.to_json())

    typer.echo("Google Calendar auth complete. Token saved to auth/token.json")


def sync():
    """Bidirectional Google Calendar sync."""
    creds = _load_credentials()
    if not creds or not creds.valid:
        typer.echo("Not authenticated. Run 'nexus manage auth google' first.")
        raise typer.Exit(1)

    service = build("calendar", "v3", credentials=creds)

    state = _load_sync_state()
    calendar_id = state.get("calendar_id", "primary")
    last_sync_str = state.get("last_sync", "")

    pulled = 0
    pushed = 0
    conflicts = 0

    # -- PULL (gcal -> nexus) --
    list_kwargs = {
        "calendarId": calendar_id,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if last_sync_str:
        list_kwargs["updatedMin"] = last_sync_str
        list_kwargs["timeMin"] = last_sync_str

    events_result = service.events().list(**list_kwargs).execute()
    events = events_result.get("items", [])

    index = load_index()
    gcal_id_map = {}
    for entry in index.tasks:
        task = load_task(resolve(entry.path))
        if task.gcal_event_id:
            gcal_id_map[task.gcal_event_id] = entry

    for event in events:
        event_id = event["id"]
        event_summary = event.get("summary", "Untitled Event")
        event_updated = event.get("updated", "")

        start = event.get("start", {})
        event_start = start.get("dateTime", start.get("date", ""))
        due_value = _parse_gcal_datetime(event_start)

        if event_id in gcal_id_map:
            entry = gcal_id_map[event_id]
            task_path = resolve(entry.path)
            task = load_task(task_path)

            gcal_modified = datetime.fromisoformat(event_updated.replace("Z", "+00:00"))
            nexus_modified = task.last_modified.replace(tzinfo=gcal_modified.tzinfo) if task.last_modified.tzinfo is None else task.last_modified

            if gcal_modified > nexus_modified:
                task.name = event_summary
                task.due = due_value
                task.last_modified = datetime.now()
                save_task(task_path, task)
                update_index_entry(entry.slug, name=event_summary, due=due_value)
                pulled += 1
            else:
                conflicts += 1
        else:
            slug = slugify(event_summary)
            existing_slugs = {e.slug for e in index.tasks}
            if slug in existing_slugs:
                slug = f"{slug}_gcal"

            tasks_dir = get_tasks_dir()
            tasks_dir.mkdir(parents=True, exist_ok=True)
            task_path = tasks_dir / f"{slug}.toml"

            task = TaskConfig(
                name=event_summary,
                slug=slug,
                status="todo",
                created=date.today(),
                due=due_value,
                tags=["gcal"],
                gcal_event_id=event_id,
                last_modified=datetime.now(),
            )
            save_task(task_path, task)

            entry = IndexEntry(
                slug=slug,
                name=event_summary,
                path=to_stored_path(task_path),
                due=due_value,
            )
            add_to_index(entry)
            index = load_index()
            pulled += 1

    # -- PUSH (nexus -> gcal) --
    index = load_index()
    now = datetime.now()

    for entry in index.tasks:
        if entry.due is None:
            continue

        task_path = resolve(entry.path)
        task = load_task(task_path)

        should_push = False
        if not task.gcal_event_id:
            should_push = True
        elif last_sync_str:
            last_sync_dt = datetime.fromisoformat(last_sync_str.replace("Z", "+00:00"))
            nexus_modified = task.last_modified
            if nexus_modified.tzinfo is None and last_sync_dt.tzinfo is not None:
                nexus_modified = nexus_modified.replace(tzinfo=last_sync_dt.tzinfo)
            if nexus_modified > last_sync_dt:
                should_push = True

        if not should_push:
            continue

        event_body = _build_gcal_event(task)

        if task.gcal_event_id:
            service.events().update(
                calendarId=calendar_id,
                eventId=task.gcal_event_id,
                body=event_body,
            ).execute()
        else:
            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event_body,
            ).execute()
            task.gcal_event_id = created_event["id"]
            task.last_modified = now
            save_task(task_path, task)

        pushed += 1

    # -- Update sync state --
    state["last_sync"] = now.isoformat()
    state["calendar_id"] = calendar_id
    _save_sync_state(state)

    typer.echo(f"Sync complete: {pulled} pulled, {pushed} pushed, {conflicts} conflicts (latest wins)")


def _parse_gcal_datetime(dt_str: str) -> datetime | date | None:
    if not dt_str:
        return None
    if "T" in dt_str:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return date.fromisoformat(dt_str)


def _build_gcal_event(task: TaskConfig) -> dict:
    event = {"summary": task.name}
    if task.description:
        event["description"] = task.description

    if task.due:
        if isinstance(task.due, datetime):
            start_dt = task.due
            end_dt = start_dt + timedelta(hours=1)
            event["start"] = {"dateTime": start_dt.isoformat(), "timeZone": "UTC"}
            event["end"] = {"dateTime": end_dt.isoformat(), "timeZone": "UTC"}
        else:
            event["start"] = {"date": task.due.isoformat()}
            next_day = task.due + timedelta(days=1)
            event["end"] = {"date": next_day.isoformat()}

    return event
