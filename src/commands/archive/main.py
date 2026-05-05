"""Archive app — wires up all archive subapps.

Usage:
  nexus archive setup
  nexus archive onboard [--task <add|query|maintain|ingest>]
  nexus archive add <path-or-url>
  nexus archive topic [new|update|delete|show]
  nexus archive topics [--match <q>]
  nexus archive write <slug> --file <path>
  nexus archive doc [update|rename|delete|show]
  nexus archive link [add|remove]
  nexus archive index [--regenerate]
  nexus archive work list [--kind <kind>]
  nexus archive maintain [--task <task>]
  nexus archive integrity
  nexus archive reindex
  nexus archive recent [--days N] [-n M]
  nexus archive tag <tag>
  nexus archive related <slug>
  nexus archive neighborhood <slug> [--hops N]
  nexus archive output [save|list|show|integrate|split|archive]
  (More subcommands added in subsequent phases.)
"""

import typer

from src.commands.archive.add import add
from src.commands.archive.doc import app as doc_app
from src.commands.archive.index_cmd import index_cmd
from src.commands.archive.integrity import integrity
from src.commands.archive.link import app as link_app
from src.commands.archive.maintain import maintain
from src.commands.archive.neighborhood import neighborhood
from src.commands.archive.onboard import onboard
from src.commands.archive.output import app as output_app
from src.commands.archive.query import query
from src.commands.archive.recent import recent
from src.commands.archive.reindex import reindex
from src.commands.archive.related import related
from src.commands.archive.search import search
from src.commands.archive.setup import setup
from src.commands.archive.tag import tag
from src.commands.archive.topic import app as topic_app
from src.commands.archive.topic import topics
from src.commands.archive.work import app as work_app
from src.commands.archive.write import write

app = typer.Typer()

app.command(name="setup", help="One-time setup: create archive dirs and register QMD collection")(
    setup
)
app.command(name="onboard", help="Full archivist context dump")(onboard)
app.command(name="add", help="Stage raw source material for archivist ingestion")(add)
app.add_typer(topic_app, name="topic", help="Manage archive topics")
app.command(name="topics", help="List all topics (optionally filtered by --match)")(topics)
app.command(name="write", help="Commit a drafted wiki doc to the archive")(write)
app.add_typer(doc_app, name="doc", help="Manage wiki docs (update, rename, delete, show)")
app.add_typer(link_app, name="link", help="Manage curated links between docs")
app.command(name="index", help="Print or regenerate archive/index.toml")(index_cmd)
app.add_typer(work_app, name="work", help="Show archive work queue")
app.command(name="maintain", help="Surface archivist maintenance work")(maintain)
app.command(name="integrity", help="Scan and repair archive graph drift")(integrity)
app.command(name="reindex", help="Regenerate index.toml and refresh QMD")(reindex)
app.command(name="recent", help="List recently updated docs")(recent)
app.command(name="tag", help="List docs by tag")(tag)
app.command(name="related", help="Show direct neighbours for a doc")(related)
app.command(name="neighborhood", help="Multi-hop subgraph dump")(neighborhood)
app.command(name="search", help="Raw QMD search hits (no enrichment)")(search)
app.command(name="query", help="Recall mode: QMD hits with frontmatter-summary enrichment")(query)
app.add_typer(output_app, name="output", help="Manage persisted archive outputs")
