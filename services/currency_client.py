import requests
from typing import List, Dict

API_KEY = "hOnpnuwgLeCWEwJyQQSR3Qz6ENV92sla"
RATES_URL = "https://api.apilayer.com/exchangerates_data/latest"


class CurrencyError(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status = status
        self.msg = msg


def fetch_rates(base: str = "EUR", symbols: List[str] = None, timeout=10) -> Dict:
    """
    Fetch currency rates using apilayer ExchangeRates API.
    Returns: {"base": "...", "rates": {...}}
    Raises CurrencyError on failure.
    """

    params = {"base": base}
    if symbols:
        params["symbols"] = ",".join(symbols)

    headers = {
        "apikey": API_KEY
    }

    try:
        print("Requesting rates with params:", params)
        r = requests.get(RATES_URL, params=params, headers=headers, timeout=timeout)
    except requests.exceptions.RequestException:
        raise CurrencyError(503, "Currency service unavailable (timeout)")

   
    if r.status_code == 401:
        raise CurrencyError(503, "Invalid API key (401)")

   
    if r.status_code == 429:
        raise CurrencyError(503, "Rate limit exceeded (429)")

    if r.status_code >= 500:
        raise CurrencyError(502, "Currency provider error")

    if r.status_code != 200:
        raise CurrencyError(503, f"Currency provider returned error {r.status_code}")

    data = r.json()

  
    if not data.get("success", True):
        msg = data.get("error", {}).get("info", "Unknown API error")
        raise CurrencyError(400, msg)

    if "rates" not in data or not data["rates"]:
        raise CurrencyError(400, "Invalid base currency or no rates returned")

    return {
        "base": data["base"],
        "rates": data["rates"]
    }
