"""Weather utilities for the manage system.

Uses Open-Meteo API (free, no API key required) with httpx.
"""

import asyncio
from pathlib import Path

import httpx
import tomllib
import tomli_w
from pydantic import BaseModel

from src.utils.paths import get_manage_dir

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Dense drizzle",
    56: "Freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Heavy thunderstorm with hail",
}


class WeatherConfig(BaseModel):
    latitude: float
    longitude: float
    name: str = ""
    timezone: str = "auto"


class WeatherData(BaseModel):
    location: str
    current_temp: float
    feels_like: float
    high: float
    low: float
    condition: str
    sunrise: str
    sunset: str
    wind_speed: float
    precipitation: float


def _get_weather_config_path() -> Path:
    return get_manage_dir() / "weather.toml"


def load_weather_config() -> WeatherConfig | None:
    path = _get_weather_config_path()
    if not path.exists():
        return None
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return WeatherConfig(**data)


def save_weather_config(config: WeatherConfig) -> None:
    path = _get_weather_config_path()
    data = config.model_dump()
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


async def geocode(name: str) -> list[dict]:
    """Look up a location by name using Open-Meteo geocoding."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(GEOCODING_URL, params={"name": name, "count": 5})
        resp.raise_for_status()
        data = resp.json()
    return data.get("results", [])


async def fetch_weather(config: WeatherConfig) -> WeatherData:
    """Fetch current weather and daily forecast from Open-Meteo."""
    params = {
        "latitude": config.latitude,
        "longitude": config.longitude,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,sunrise,sunset",
        "timezone": config.timezone,
        "forecast_days": 1,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data["current"]
    daily = data["daily"]

    code = current.get("weather_code", 0)
    condition = WMO_CODES.get(code, f"Code {code}")

    sunrise_raw = daily["sunrise"][0]
    sunset_raw = daily["sunset"][0]
    sunrise = sunrise_raw.split("T")[1] if "T" in sunrise_raw else sunrise_raw
    sunset = sunset_raw.split("T")[1] if "T" in sunset_raw else sunset_raw

    return WeatherData(
        location=config.name or f"{config.latitude}, {config.longitude}",
        current_temp=current["temperature_2m"],
        feels_like=current["apparent_temperature"],
        high=daily["temperature_2m_max"][0],
        low=daily["temperature_2m_min"][0],
        condition=condition,
        sunrise=sunrise,
        sunset=sunset,
        wind_speed=current["wind_speed_10m"],
        precipitation=current["precipitation"],
    )


def fetch_weather_sync(config: WeatherConfig) -> WeatherData:
    """Synchronous wrapper for fetch_weather."""
    return asyncio.run(fetch_weather(config))


def format_weather(weather: WeatherData) -> str:
    """Format weather data for display."""
    lines = [
        f"☀ {weather.location}: {weather.condition}, {weather.current_temp:.0f}°C (feels like {weather.feels_like:.0f}°C)",
        f"   High {weather.high:.0f}°C / Low {weather.low:.0f}°C | Wind {weather.wind_speed:.0f} km/h | Sunrise {weather.sunrise} / Sunset {weather.sunset}",
    ]
    return "\n".join(lines)
