import httpx
import pytest

from week3.server import weather_api


def make_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def test_search_location_normalizes_geocoding_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/search"
        assert request.url.params["name"] == "Hangzhou"
        assert request.url.params["count"] == "3"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "name": "Hangzhou",
                        "country": "China",
                        "latitude": 30.2741,
                        "longitude": 120.1551,
                        "timezone": "Asia/Shanghai",
                    }
                ]
            },
        )

    with make_client(handler) as client:
        result = weather_api.search_location("Hangzhou", count=3, client=client)

    assert result == {
        "query": "Hangzhou",
        "results": [
            {
                "name": "Hangzhou",
                "country": "China",
                "latitude": 30.2741,
                "longitude": 120.1551,
                "timezone": "Asia/Shanghai",
            }
        ],
    }


def test_search_location_rejects_blank_queries():
    with pytest.raises(ValueError, match="Location name must not be empty"):
        weather_api.search_location("   ")


def test_get_current_weather_normalizes_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/forecast"
        assert request.url.params["latitude"] == "30.2741"
        assert request.url.params["longitude"] == "120.1551"
        return httpx.Response(
            200,
            json={
                "latitude": 30.2741,
                "longitude": 120.1551,
                "current": {
                    "time": "2026-03-13T14:00",
                    "temperature_2m": 18.2,
                    "apparent_temperature": 17.3,
                    "wind_speed_10m": 7.4,
                    "weather_code": 2,
                },
            },
        )

    with make_client(handler) as client:
        result = weather_api.get_current_weather(30.2741, 120.1551, client=client)

    assert result == {
        "latitude": 30.2741,
        "longitude": 120.1551,
        "current_weather": {
            "time": "2026-03-13T14:00",
            "temperature": 18.2,
            "apparent_temperature": 17.3,
            "wind_speed": 7.4,
            "weather_code": 2,
        },
    }


def test_get_weather_forecast_rejects_invalid_days():
    with pytest.raises(ValueError, match="days must be between 1 and 7"):
        weather_api.get_weather_forecast(30.0, 120.0, days=0)


def test_get_weather_forecast_normalizes_daily_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/forecast"
        assert request.url.params["forecast_days"] == "2"
        return httpx.Response(
            200,
            json={
                "latitude": 30.2741,
                "longitude": 120.1551,
                "daily": {
                    "time": ["2026-03-13", "2026-03-14"],
                    "temperature_2m_max": [21.0, 19.6],
                    "temperature_2m_min": [12.3, 11.8],
                    "precipitation_sum": [0.0, 2.1],
                    "weather_code": [1, 61],
                },
            },
        )

    with make_client(handler) as client:
        result = weather_api.get_weather_forecast(30.2741, 120.1551, days=2, client=client)

    assert result == {
        "latitude": 30.2741,
        "longitude": 120.1551,
        "forecast": [
            {
                "date": "2026-03-13",
                "temperature_max": 21.0,
                "temperature_min": 12.3,
                "precipitation_sum": 0.0,
                "weather_code": 1,
            },
            {
                "date": "2026-03-14",
                "temperature_max": 19.6,
                "temperature_min": 11.8,
                "precipitation_sum": 2.1,
                "weather_code": 61,
            },
        ],
    }

