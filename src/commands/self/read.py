from datetime import date
from typing import Annotated

import typer
from src.utils.self import (
    get_reading_active_dir,
    list_active_books,
    list_completed_books,
    load_book,
    save_book,
    slugify,
)

from src.models.self.reading import BookConfig, ReadingSession

app = typer.Typer(help="Reading habit tracking")


@app.command()
def new(
    title: str,
    author: Annotated[str, typer.Option("--author")] = "",
) -> None:
    slug = slugify(title)
    path = get_reading_active_dir() / f"{slug}.toml"
    if path.exists():
        typer.echo(f"Book '{slug}' already exists.")
        raise typer.Exit(1)

    book = BookConfig(
        name=title,
        author=author,
        slug=slug,
        started=date.today(),
    )
    save_book(book)
    typer.echo(f"Created book: {title} (slug: {slug})")


@app.command("list")
def list_books() -> None:
    books = list_active_books()
    if not books:
        typer.echo(
            "No active books. Create one with: nexus self read new 'Title' --author 'Author'"
        )
        return

    for book in books:
        last_session = (
            book.sessions[-1].date.isoformat() if book.sessions else "No sessions yet"
        )
        last_read = book.sessions[-1].description if book.sessions else "Just started"
        typer.echo(
            f"  {book.name} by {book.author} (slug: {book.slug}) — last: {last_read}, sessions: {len(book.sessions)}"
        )


@app.command()
def show(slug: str) -> None:
    try:
        book = load_book(slug)
    except FileNotFoundError:
        typer.echo(f"Book '{slug}' not found.")
        raise typer.Exit(1)

    typer.echo(f"Title: {book.name}")
    typer.echo(f"Author: {book.author}")
    typer.echo(f"Started: {book.started}")
    typer.echo(f"Status: {book.status}")
    if book.sessions:
        typer.echo(f"Last read: {book.sessions[-1].description}")
    typer.echo(f"Total sessions: {len(book.sessions)}")

    if book.sessions:
        typer.echo("\nRecent sessions:")
        for session in book.sessions[-3:]:
            summary = (
                session.summary[:100] + "..."
                if len(session.summary) > 100
                else session.summary
            )
            takeaway = (
                session.takeaway[:100] + "..."
                if len(session.takeaway) > 100
                else session.takeaway
            )
            typer.echo(f"  [{session.date}] {session.description}")
            typer.echo(f"    Summary: {summary}")
            typer.echo(f"    Takeaway: {takeaway}")


@app.command()
def log(
    slug: str,
    description: Annotated[str, typer.Option("--description")],
    summary: Annotated[str, typer.Option("--summary")],
    takeaway: Annotated[str, typer.Option("--takeaway")],
    log_date: Annotated[str, typer.Option("--date", help="Backdate entry (YYYY-MM-DD)")] = "",
) -> None:
    try:
        book = load_book(slug)
    except FileNotFoundError:
        typer.echo(f"Book '{slug}' not found.")
        raise typer.Exit(1)

    session_date = date.fromisoformat(log_date) if log_date else date.today()
    session = ReadingSession(
        date=session_date,
        description=description,
        summary=summary,
        takeaway=takeaway,
    )
    book.sessions.append(session)
    save_book(book)
    typer.echo(f"Logged reading session for '{book.name}' — {description}")


@app.command()
def complete(
    slug: str,
    summary: Annotated[str, typer.Option("--summary", help="Overall summary of the book")],
    takeaway: Annotated[str, typer.Option("--takeaway", help="Key takeaways from the book")],
) -> None:
    try:
        book = load_book(slug)
    except FileNotFoundError:
        typer.echo(f"Book '{slug}' not found.")
        raise typer.Exit(1)

    if book.status == "completed":
        typer.echo(f"Book '{book.name}' is already completed.")
        raise typer.Exit(1)

    book.status = "completed"
    book.completion_summary = summary
    book.completion_takeaway = takeaway
    active_path = get_reading_active_dir() / f"{slug}.toml"
    save_book(book)
    if active_path.exists():
        active_path.unlink()

    date_range = ""
    if book.sessions:
        first = book.sessions[0].date
        last = book.sessions[-1].date
        date_range = f" ({first} to {last})"

    typer.echo(f"Completed '{book.name}' — {len(book.sessions)} sessions{date_range}")


@app.command()
def history() -> None:
    books = list_completed_books()
    if not books:
        typer.echo("No completed books yet.")
        return

    for book in books:
        last_date = book.sessions[-1].date.isoformat() if book.sessions else "unknown"
        typer.echo(
            f"  {book.name} by {book.author} — started: {book.started}, completed: {last_date}, sessions: {len(book.sessions)}"
        )
