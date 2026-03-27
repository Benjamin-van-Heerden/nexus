import typer

from src.commands.learn.main import app as learn_app
from src.utils.path_resolution import resolve_str

app = typer.Typer(help="Nexus - Personal learning and self-improvement CLI")

app.add_typer(learn_app, name="learn", help="Learning system commands")


@app.command(name="resolve-path")
def resolve_path(relative_path: str = typer.Argument(help="Path relative to nexus project root")):
    """Resolve a relative path to an absolute path on this machine."""
    print(resolve_str(relative_path))


if __name__ == "__main__":
    app()
