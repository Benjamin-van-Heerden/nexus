import typer

from src.commands.learn.main import app as learn_app
from src.commands.manage.main import app as manage_app
from src.commands.pause.main import app as pause_app
from src.commands.self.main import app as self_app
from src.utils.git_sync import post_sync, pre_sync
from src.utils.path_resolution import resolve_str

app = typer.Typer(help="Nexus - Personal learning and self-improvement CLI")

app.add_typer(learn_app, name="learn", help="Learning system commands")
app.add_typer(manage_app, name="manage", help="Personal management commands")
app.add_typer(pause_app, name="pause", help="Pause and resume subsystems")
app.add_typer(self_app, name="self", help="Self-improvement and habit tracking")


@app.command(name="resolve-path")
def resolve_path(
    relative_path: str = typer.Argument(help="Path relative to nexus project root"),
):
    """Resolve a relative path to an absolute path on this machine."""
    print(resolve_str(relative_path))


if __name__ == "__main__":
    pre_sync()
    try:
        app()
    finally:
        post_sync()
