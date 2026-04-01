"""Manage app — wires up all manage subapps.

Usage:
  nexus manage task [new|list|show|complete|edit|delete]
  nexus manage contact [new|list|show|edit|delete]
  nexus manage onboard
  nexus manage upcoming
  nexus manage sync
  nexus manage auth google
"""

import typer

from src.commands.manage.contact import app as contact_app
from src.commands.manage.onboard import onboard, refresh, upcoming
from src.commands.manage.sync import auth_google, sync
from src.commands.manage.task import app as task_app

auth_app = typer.Typer()
auth_app.command(name="google", help="Set up Google Calendar OAuth")(auth_google)

app = typer.Typer()

app.add_typer(task_app, name="task", help="Manage tasks")
app.add_typer(contact_app, name="contact", help="Manage contacts")
app.add_typer(auth_app, name="auth", help="Authentication commands")
app.command(name="onboard", help="Full manage context dump for agents")(onboard)
app.command(name="refresh", help="Lightweight context refresh for follow-up sessions")(
    refresh
)
app.command(
    name="upcoming", help="Show upcoming tasks, birthdays, and recurring events"
)(upcoming)
app.command(name="sync", help="Bidirectional Google Calendar sync")(sync)
