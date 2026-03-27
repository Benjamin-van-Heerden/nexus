"""Learn app — wires up all learn subapps.

Usage:
  nexus learn onboard
  nexus learn topic [new|list|delete|update|reset|history|weights]
  nexus learn subtopic [new|set|list|delete]
  nexus learn phase [new|complete|delete|status]
  nexus learn goal [new|set|complete|delete|list|status]
  nexus learn task [new|complete|list]
  nexus learn record "description"
"""

import typer

from src.commands.learn.topic import app as topic_app
from src.commands.learn.subtopic import app as subtopic_app
from src.commands.learn.phase import app as phase_app
from src.commands.learn.goal import app as goal_app
from src.commands.learn.task import app as task_app
from src.commands.learn.onboard import onboard
from src.commands.learn.record import record

app = typer.Typer()

app.add_typer(topic_app, name="topic", help="Manage learning topics")
app.add_typer(subtopic_app, name="subtopic", help="Manage subtopics within a topic")
app.add_typer(phase_app, name="phase", help="Manage learning phases")
app.add_typer(goal_app, name="goal", help="Manage goals in active phase")
app.add_typer(task_app, name="task", help="Manage tasks in current goal")
app.command(name="onboard", help="Print full learning context for agents")(onboard)
app.command(name="record", help="Log a learning session record")(record)
