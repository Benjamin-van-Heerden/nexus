"""Archive app — wires up all archive subapps.

Usage:
  nexus archive setup
  nexus archive topic [new|update|delete|show]
  nexus archive topics [--match <q>]
  nexus archive write <slug> --file <path>
  nexus archive doc [update|rename|delete|show]
  nexus archive link [add|remove]
  nexus archive index [--regenerate]
  nexus archive recent [--days N] [-n M]
  nexus archive tag <tag>
  nexus archive related <slug>
  nexus archive neighborhood <slug> [--hops N]
  (More subcommands added in subsequent phases.)
"""

import typer

from src.commands.archive.doc import app as doc_app
from src.commands.archive.index_cmd import index_cmd
from src.commands.archive.link import app as link_app
from src.commands.archive.neighborhood import neighborhood
from src.commands.archive.query import query
from src.commands.archive.recent import recent
from src.commands.archive.related import related
from src.commands.archive.search import search
from src.commands.archive.setup import setup
from src.commands.archive.tag import tag
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
app.command(name="index", help="Print or regenerate archive/index.toml")(index_cmd)
app.command(name="recent", help="List recently updated docs")(recent)
app.command(name="tag", help="List docs by tag")(tag)
app.command(name="related", help="Show direct neighbours for a doc")(related)
app.command(name="neighborhood", help="Multi-hop subgraph dump")(neighborhood)
app.command(name="search", help="Raw QMD search hits (no enrichment)")(search)
app.command(name="query", help="Recall mode: QMD hits with frontmatter-summary enrichment")(query)
