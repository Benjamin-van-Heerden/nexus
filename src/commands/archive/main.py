"""Archive app — wires up all archive subapps.

Usage:
  nexus archive setup
  (More subcommands added in subsequent phases.)
"""

import typer

from src.commands.archive.setup import setup

app = typer.Typer()

app.command(name="setup", help="One-time setup: create archive dirs and register QMD collection")(setup)
