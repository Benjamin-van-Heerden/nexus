"""News app — wires up all news commands.

Usage:
  nexus news onboard
  nexus news refresh
  nexus news track "story description"
  nexus news untrack <slug>
  nexus news stories
"""

import typer

from src.commands.news.onboard import onboard, refresh
from src.commands.news.track import stories, track, untrack

app = typer.Typer()

app.command(name="onboard", help="Generate the full daily newspaper")(onboard)
app.command(name="refresh", help="Check for breaking news since onboard")(refresh)
app.command(name="track", help="Start following a story over time")(track)
app.command(name="untrack", help="Stop following a tracked story")(untrack)
app.command(name="stories", help="List tracked stories")(stories)
