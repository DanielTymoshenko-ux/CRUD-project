import pytest
from unittest.mock import patch

fake_geo = (52.2297, 21.0122)
fake_weather = {
    "latitude": 52.2297,
    "longitude": 21.0122,
    "forecast": [{"time": "2025-01-01T00:00", "temperature": 0}],
    "source": "open-meteo"
}

@patch("services.weather_client.geocode_city", return_value=fake_geo)
@patch("services.weather_client.fetch_weather", return_value=fake_weather)
def test_weather_happy(mock_fetch, mock_geo, client):
    res = client.get("/external/weather?city=Warsaw")
    assert res.status_code == 200
    data = res.get_json()
    
  
    assert "latitude" in data
    assert "longitude" in data
    assert "forecast" in data
    assert isinstance(data["latitude"], (float, int))
    assert isinstance(data["longitude"], (float, int))
    assert isinstance(data["forecast"], list)
