# tests/test_external_weather.py
import json
import pytest
from unittest.mock import patch
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client

def fake_geocode_ok(name, timeout=5):
    class R: pass
    return (52.23, 21.01)

def fake_fetch_ok(lat, lon, hourly="temperature_2m", timezone="UTC", timeout=5):
    return {"forecast":[{"time":"2025-10-30T10:00","temperature":10},{"time":"2025-10-30T11:00","temperature":11}] , "source":"open-meteo"}

@patch("services.weather_client.geocode_city", side_effect=fake_geocode_ok)
@patch("services.weather_client.fetch_weather", side_effect=fake_fetch_ok)
def test_weather_happy(mock_fetch, mock_geo, client):
    res = client.get("/external/weather?city=Warsaw")
    assert res.status_code == 200
    j = res.get_json()
    assert "forecast" in j
    assert isinstance(j["forecast"], list)

@patch("services.weather_client.geocode_city", side_effect=Exception("boom"))
def test_weather_geo_fail(mock_geo, client):
    res = client.get("/external/weather?city=NonExist")
    # our route catches generic Exception as 502
    assert res.status_code in (400, 502)
