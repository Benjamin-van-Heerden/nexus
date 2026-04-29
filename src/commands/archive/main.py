"""Archive app — wires up all archive subapps.

Usage:
  nexus archive setup
  nexus archive topic [new|update|delete|show]
  nexus archive topics [--match <q>]
  nexus archive write <slug> --file <path>
  nexus archive doc [update|rename|delete|show]
  nexus archive link [add|remove]
  (More subcommands added in subsequent phases.)
"""

import typer

from src.commands.archive.doc import app as doc_app
from src.commands.archive.link import app as link_app
from src.commands.archive.setup import setup
from src.commands.archive.topic import app as topic_app
from src.commands.archive.topic import topics
from src.commands.archive.write import write

app = typer.Typer()

app.command(name="setup", help="One-time setup: create archive dirs and register QMD collection")(setup)
app.add_typer(topic_app, name="topic", help="Manage archive topics")
app.command(name="topics", help="List all topics (optionally filtered by --match)")(topics)
app.command(name="write", help="Commit a drafted wiki doc to the archive")(write)
app.add_typer(doc_app, name="doc", help="Manage wiki docs (update, rename, delete, show)")
app.add_typer(link_app, name="link", help="Manage curated links between docs")
