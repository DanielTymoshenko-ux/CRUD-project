import pytest
from unittest.mock import patch

fake_rates_ok = {"base": "EUR", "rates": {"PLN": 4.5, "USD": 1.1}}

@pytest.mark.parametrize("base,symbols", [("EUR", "PLN,USD")])
@patch("services.currency_client.fetch_rates", return_value=fake_rates_ok)
def test_rates_happy(mock_fetch, client, base, symbols):
    res = client.get(f"/external/rates?base={base}&symbols={symbols}")
    assert res.status_code == 200
    data = res.get_json()
    assert data == fake_rates_ok
