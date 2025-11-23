import pytest
from unittest.mock import patch

fake_geo = (52.2297, 21.0122)
fake_weather = {
    "latitude": 52.22977,
    "longitude": 21.0122,
    "forecast": [
        {"time": "2025-11-23T00:00", "temperature": 1},
        {"time": "2025-11-23T01:00", "temperature": 2},
        {"time": "2025-11-23T02:00", "temperature": 3},
        {"time": "2025-11-23T03:00", "temperature": 4},
    ],
    "source": "open-meteo"
}

@patch("services.weather_client.geocode_city", return_value=fake_geo)
@patch("services.weather_client.fetch_weather", return_value=fake_weather)
def test_weather_happy(mock_fetch, mock_geo, client):
    res = client.get("/external/weather?city=Warsaw")
    assert res.status_code == 200
    data = res.get_json()
    
    import pytest
    # порівнюємо float із допустимою точністю
    assert data["latitude"] == pytest.approx(52.2297)
    assert data["longitude"] == pytest.approx(21.0122)
    assert len(data["forecast"]) == 4
    assert data["source"] == "open-meteo"
