# Week 3 Weather MCP Server

This project implements a local STDIO MCP server that wraps the Open-Meteo APIs.

## Prerequisites

- Python environment for this repository
- Week 3 specific packages:

```bash
pip install -r week3/requirements.txt
```

## Run

From the repository root:

```bash
conda activate cs146s
python -m week3.server.main
```

## Tools

### `search_location`

Searches for a place name and returns candidate locations with coordinates.

Inputs:
- `name: str`
- `count: int = 5`

### `get_current_weather`

Returns current weather for a latitude and longitude.

Inputs:
- `latitude: float`
- `longitude: float`

### `get_weather_forecast`

Returns a daily weather forecast for the next `days` days.

Inputs:
- `latitude: float`
- `longitude: float`
- `days: int = 3`

## Example flow

1. Call `search_location` with a city name.
2. Pick a candidate result and extract `latitude` and `longitude`.
3. Call `get_current_weather` or `get_weather_forecast`.

## Notes

- This server is intended for local STDIO transport.
- The upstream APIs used are:
  - `https://geocoding-api.open-meteo.com/v1/search`
  - `https://api.open-meteo.com/v1/forecast`
