import typer

from src.commands.self.exercise import app as exercise_app
from src.commands.self.learn import app as learn_app
from src.commands.self.math import app as math_app
from src.commands.self.onboard import onboard, refresh
from src.commands.self.read import app as read_app

app = typer.Typer(help="Self-improvement and habit tracking")

app.add_typer(read_app, name="read", help="Reading habit tracking")
app.add_typer(exercise_app, name="exercise", help="Exercise habit tracking")
app.add_typer(math_app, name="math", help="Mental math practice")
app.add_typer(learn_app, name="learn", help="Learning habit tracking")
app.command(name="onboard", help="Daily context dump for agents")(onboard)
app.command(name="refresh", help="Lightweight context refresh for follow-up sessions")(refresh)
