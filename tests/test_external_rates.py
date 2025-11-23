# tests/test_external_rates.py
import pytest
from unittest.mock import patch
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    with app.app_context():
        db.drop_all(); db.create_all()
    with app.test_client() as client:
        yield client

def fake_rates_ok(base="EUR", symbols=None, timeout=5):
    return {"base": base, "rates": {"PLN": 4.5, "USD": 1.08}}

@patch("services.currency_client.fetch_rates", side_effect=fake_rates_ok)
def test_rates_happy(mock_fetch, client):
    res = client.get("/external/rates?base=EUR&symbols=PLN,USD")
    assert res.status_code == 200
    j = res.get_json()
    assert j["base"] == "EUR"
    assert isinstance(j["rates"], list)
