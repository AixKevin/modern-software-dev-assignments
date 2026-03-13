from __future__ import annotations

from typing import Any

import httpx

GEOCODING_BASE_URL = "https://geocoding-api.open-meteo.com"
FORECAST_BASE_URL = "https://api.open-meteo.com"
DEFAULT_TIMEOUT = 10.0


class WeatherAPIError(RuntimeError):
    """Raised when the upstream weather API fails or returns unusable data."""


def _build_client() -> httpx.Client:
    return httpx.Client(timeout=DEFAULT_TIMEOUT)


def _get_json(
    client: httpx.Client,
    base_url: str,
    path: str,
    *,
    params: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = client.get(f"{base_url}{path}", params=params)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise WeatherAPIError("The upstream weather service timed out") from exc
    except httpx.HTTPError as exc:
        raise WeatherAPIError(f"The upstream weather service request failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise WeatherAPIError("The upstream weather service returned invalid JSON") from exc


def search_location(name: str, count: int = 5, *, client: httpx.Client | None = None) -> dict[str, Any]:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Location name must not be empty")
    if count < 1:
        raise ValueError("count must be at least 1")

    own_client = client is None
    client = client or _build_client()
    try:
        payload = _get_json(
            client,
            GEOCODING_BASE_URL,
            "/v1/search",
            params={"name": clean_name, "count": count, "language": "en", "format": "json"},
        )
    finally:
        if own_client:
            client.close()

    results = payload.get("results") or []
    normalized = [
        {
            "name": item["name"],
            "country": item.get("country", ""),
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "timezone": item.get("timezone", ""),
        }
        for item in results
    ]
    return {"query": clean_name, "results": normalized}


def get_current_weather(
    latitude: float,
    longitude: float,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    own_client = client is None
    client = client or _build_client()
    try:
        payload = _get_json(
            client,
            FORECAST_BASE_URL,
            "/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,apparent_temperature,wind_speed_10m,weather_code",
            },
        )
    finally:
        if own_client:
            client.close()

    current = payload.get("current")
    if not current:
        raise WeatherAPIError("No current weather data was returned")

    return {
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
        "current_weather": {
            "time": current["time"],
            "temperature": current["temperature_2m"],
            "apparent_temperature": current["apparent_temperature"],
            "wind_speed": current["wind_speed_10m"],
            "weather_code": current["weather_code"],
        },
    }


def get_weather_forecast(
    latitude: float,
    longitude: float,
    *,
    days: int = 3,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    if days < 1 or days > 7:
        raise ValueError("days must be between 1 and 7")

    own_client = client is None
    client = client or _build_client()
    try:
        payload = _get_json(
            client,
            FORECAST_BASE_URL,
            "/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "forecast_days": days,
            },
        )
    finally:
        if own_client:
            client.close()

    daily = payload.get("daily")
    if not daily:
        raise WeatherAPIError("No forecast data was returned")

    forecast = [
        {
            "date": day,
            "temperature_max": temperature_max,
            "temperature_min": temperature_min,
            "precipitation_sum": precipitation_sum,
            "weather_code": weather_code,
        }
        for day, temperature_max, temperature_min, precipitation_sum, weather_code in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["precipitation_sum"],
            daily["weather_code"],
        )
    ]
    return {
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
        "forecast": forecast,
    }

