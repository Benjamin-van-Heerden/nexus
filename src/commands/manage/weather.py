"""Weather command for the manage system."""

import typer

from src.utils.weather import (
    WeatherConfig,
    fetch_weather_sync,
    format_weather,
    load_weather_config,
    save_weather_config,
)


def weather(
    latlon: str = typer.Option("", help="Coordinates as 'lat,lon' (e.g. '-25.7,28.2')"),
    name: str = typer.Option("", help="Location name (e.g. 'Pretoria')"),
):
    """Configure weather location or show current weather.

    Set location:
      nexus manage weather --latlon "-25.7,28.2" --name "Pretoria"

    Show weather (uses saved location):
      nexus manage weather
    """
    if latlon or name:
        if not latlon or not name:
            typer.echo("Both --latlon and --name are required to configure weather.")
            raise typer.Exit(1)
        try:
            parts = latlon.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
        except (ValueError, IndexError):
            typer.echo(f"Invalid coordinates: '{latlon}'. Use 'lat,lon' format.")
            raise typer.Exit(1)

        config = WeatherConfig(latitude=lat, longitude=lon, name=name)
        save_weather_config(config)
        typer.echo(f"Weather location set: {name} ({lat}, {lon})")
        return

    config = load_weather_config()
    if not config:
        typer.echo("No weather location configured.")
        typer.echo(
            "Set one with: nexus manage weather --latlon 'lat,lon' --name 'City'"
        )
        raise typer.Exit(1)

    weather_data = fetch_weather_sync(config)
    typer.echo(format_weather(weather_data))
