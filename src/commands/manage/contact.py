"""Contact CRUD commands for the management system."""

from datetime import date

import typer

from src.models.management.contact import ContactConfig
from src.utils.management import (
    get_contacts_dir,
    load_contact,
    resolve_contact_slug,
    save_contact,
    slugify,
)

app = typer.Typer()


@app.command()
def new(
    name: str = typer.Argument(help="Contact name"),
    phone: str = typer.Option("", help="Phone number"),
    email: str = typer.Option("", help="Email address"),
    birthday: str = typer.Option("", help="Birthday (YYYY-MM-DD)"),
    relationship: str = typer.Option("", help="Relationship (e.g. friend, colleague, family)"),
):
    """Create a new contact."""
    slug = slugify(name)
    contacts_dir = get_contacts_dir()
    contacts_dir.mkdir(parents=True, exist_ok=True)

    contact_path = contacts_dir / f"{slug}.toml"
    if contact_path.exists():
        typer.echo(f"Contact already exists: {slug}")
        raise typer.Exit(1)

    birthday_date = None
    if birthday:
        try:
            birthday_date = date.fromisoformat(birthday)
        except ValueError:
            typer.echo(f"Invalid date format: '{birthday}'. Use YYYY-MM-DD")
            raise typer.Exit(1)

    contact = ContactConfig(
        name=name,
        slug=slug,
        phone=phone,
        email=email,
        birthday=birthday_date,
        relationship=relationship,
    )

    save_contact(contact_path, contact)
    typer.echo(f"Created contact: {name}")
    if birthday_date:
        typer.echo("  Birthday reminders will appear in onboard/upcoming.")


@app.command(name="list")
def list_contacts():
    """List all contacts."""
    contacts_dir = get_contacts_dir()
    if not contacts_dir.exists():
        typer.echo("No contacts yet.")
        return

    files = sorted(contacts_dir.glob("*.toml"))
    if not files:
        typer.echo("No contacts yet.")
        return

    for f in files:
        contact = load_contact(f)
        parts = [contact.name]
        if contact.relationship:
            parts.append(f"({contact.relationship})")
        if contact.birthday:
            parts.append(f"🎂 {contact.birthday.strftime('%b %d')}")
        typer.echo("  " + " ".join(parts))


@app.command()
def show(slug: str = typer.Argument(help="Contact slug or name")):
    """Show contact details."""
    path = resolve_contact_slug(slug)
    contact = load_contact(path)

    typer.echo(f"Name: {contact.name}")
    typer.echo(f"Slug: {contact.slug}")
    if contact.phone:
        typer.echo(f"Phone: {contact.phone}")
    if contact.email:
        typer.echo(f"Email: {contact.email}")
    if contact.birthday:
        typer.echo(f"Birthday: {contact.birthday}")
    if contact.relationship:
        typer.echo(f"Relationship: {contact.relationship}")
    if contact.info:
        typer.echo("\nInfo:")
        for key, value in contact.info.items():
            typer.echo(f"  {key}: {value}")


@app.command()
def edit(
    slug: str = typer.Argument(help="Contact slug or name"),
    phone: str = typer.Option("", help="New phone number"),
    email: str = typer.Option("", help="New email address"),
    birthday: str = typer.Option("", help="New birthday (YYYY-MM-DD)"),
    relationship: str = typer.Option("", help="New relationship"),
    info_key: str = typer.Option("", help="Info key to add/update"),
    info_value: str = typer.Option("", help="Info value (used with --info-key)"),
    remove_info_key: str = typer.Option("", help="Info key to remove"),
):
    """Edit contact fields."""
    path = resolve_contact_slug(slug)
    contact = load_contact(path)

    changed = False

    if phone:
        contact.phone = phone
        changed = True
    if email:
        contact.email = email
        changed = True
    if birthday:
        try:
            contact.birthday = date.fromisoformat(birthday)
            changed = True
        except ValueError:
            typer.echo(f"Invalid date format: '{birthday}'. Use YYYY-MM-DD")
            raise typer.Exit(1)
    if relationship:
        contact.relationship = relationship
        changed = True
    if info_key and info_value:
        contact.info[info_key] = info_value
        changed = True
    if remove_info_key:
        if remove_info_key in contact.info:
            del contact.info[remove_info_key]
            changed = True

    if not changed:
        typer.echo("No changes specified.")
        return

    save_contact(path, contact)
    typer.echo(f"Updated: {contact.name}")


@app.command()
def delete(slug: str = typer.Argument(help="Contact slug or name")):
    """Delete a contact."""
    path = resolve_contact_slug(slug)
    contact = load_contact(path)

    typer.confirm(f"Delete contact '{contact.name}'?", abort=True)

    path.unlink()
    typer.echo(f"Deleted: {contact.name}")
