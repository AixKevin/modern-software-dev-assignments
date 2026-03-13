from week3.server import main


def test_search_location_tool_delegates_to_weather_api(monkeypatch):
    captured = {}

    def fake_search_location(name: str, count: int = 5):
        captured["name"] = name
        captured["count"] = count
        return {"query": name, "results": []}

    monkeypatch.setattr(main.weather_api, "search_location", fake_search_location)

    result = main.search_location("Hangzhou", count=2)

    assert captured == {"name": "Hangzhou", "count": 2}
    assert result == {"query": "Hangzhou", "results": []}


def test_get_current_weather_tool_delegates_to_weather_api(monkeypatch):
    captured = {}

    def fake_get_current_weather(latitude: float, longitude: float):
        captured["latitude"] = latitude
        captured["longitude"] = longitude
        return {"latitude": latitude, "longitude": longitude, "current_weather": {}}

    monkeypatch.setattr(main.weather_api, "get_current_weather", fake_get_current_weather)

    result = main.get_current_weather(30.2741, 120.1551)

    assert captured == {"latitude": 30.2741, "longitude": 120.1551}
    assert result["latitude"] == 30.2741
    assert result["longitude"] == 120.1551


def test_get_weather_forecast_tool_delegates_to_weather_api(monkeypatch):
    captured = {}

    def fake_get_weather_forecast(latitude: float, longitude: float, days: int = 3):
        captured["latitude"] = latitude
        captured["longitude"] = longitude
        captured["days"] = days
        return {"latitude": latitude, "longitude": longitude, "forecast": []}

    monkeypatch.setattr(main.weather_api, "get_weather_forecast", fake_get_weather_forecast)

    result = main.get_weather_forecast(30.2741, 120.1551, days=4)

    assert captured == {"latitude": 30.2741, "longitude": 120.1551, "days": 4}
    assert result["forecast"] == []
