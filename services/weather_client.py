import requests
from typing import Tuple, Optional

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

class WeatherError(Exception):
    def __init__(self, status:int, msg:str):
        super().__init__(msg)
        self.status = status
        self.msg = msg

def geocode_city(city: str, timeout=5) -> Tuple[float,float]:
    """Return (lat, lon) for a city or raise WeatherError(400/503)."""
    if not city or not city.strip():
        raise WeatherError(400, "Missing or empty city parameter")
    try:
        r = requests.get(GEOCODING_URL, params={"name": city, "count":1}, timeout=timeout)
    except requests.exceptions.RequestException:
        raise WeatherError(503, "Geocoding service unavailable (timeout)")
    if r.status_code >= 500:
        raise WeatherError(502, "Geocoding service error")
    if r.status_code != 200:
        raise WeatherError(503, "Geocoding failed")
    data = r.json()
    if not data.get("results"):
        raise WeatherError(400, f"City not found: {city}")
    loc = data["results"][0]
    return float(loc["latitude"]), float(loc["longitude"])

def fetch_weather(lat: float, lon: float, hourly: str="temperature_2m", timezone: str="UTC", timeout=5) -> dict:
    """Call open-meteo and return parsed simplified dict or raise WeatherError."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": hourly,
        "timezone": timezone
    }
    try:
        r = requests.get(WEATHER_URL, params=params, timeout=timeout)
    except requests.exceptions.RequestException:
        raise WeatherError(503, "Weather service unavailable (timeout)")
    if r.status_code >= 500:
        raise WeatherError(502, "Weather provider error")
    if r.status_code != 200:
        raise WeatherError(503, "Weather provider returned error")
    data = r.json()
    
    hourly_data = data.get("hourly", {})
    times = hourly_data.get("time", [])
    temps = hourly_data.get("temperature_2m", [])
    forecast = []
    if times and temps:
       
        for i in range(min(4, len(times))):
            forecast.append({"time": times[i], "temperature": temps[i]})
    result = {
        "latitude": lat,
        "longitude": lon,
        "forecast": forecast,
        "source": "open-meteo"
    }
    return result
