"""Archive app — wires up all archive subapps.

Usage:
  nexus archive setup
  nexus archive topic [new|update|delete|show]
  nexus archive topics [--match <q>]
  (More subcommands added in subsequent phases.)
"""

import typer

from src.commands.archive.setup import setup
from src.commands.archive.topic import app as topic_app
from src.commands.archive.topic import topics

app = typer.Typer()

app.command(name="setup", help="One-time setup: create archive dirs and register QMD collection")(setup)
app.add_typer(topic_app, name="topic", help="Manage archive topics")
app.command(name="topics", help="List all topics (optionally filtered by --match)")(topics)
