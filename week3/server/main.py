from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from week3.server import weather_api

app = FastMCP(
    name="weather-tools",
    instructions=(
        "Use these tools to search for a place, then fetch current weather or a short forecast. "
        "Always search for a location before guessing coordinates."
    ),
)


@app.tool(description="Search for a place name and return candidate locations with coordinates.")
def search_location(name: str, count: int = 5) -> dict:
    return weather_api.search_location(name=name, count=count)


@app.tool(description="Get the current weather for a known latitude and longitude.")
def get_current_weather(latitude: float, longitude: float) -> dict:
    return weather_api.get_current_weather(latitude=latitude, longitude=longitude)


@app.tool(description="Get a short daily forecast for a known latitude and longitude.")
def get_weather_forecast(latitude: float, longitude: float, days: int = 3) -> dict:
    return weather_api.get_weather_forecast(latitude=latitude, longitude=longitude, days=days)


def main() -> None:
    app.run(transport="stdio")


if __name__ == "__main__":
    main()

