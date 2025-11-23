# routes/external_weather.py
from flask import Blueprint, request, jsonify, current_app
from services.weather_client import geocode_city, fetch_weather, WeatherError

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/weather", methods=["GET"])
@weather_bp.route("/weather_api", methods=["GET"])
def weather_api():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    try:
        if city:
            lat_f, lon_f = geocode_city(city)
        elif lat and lon:
            lat_f, lon_f = float(lat), float(lon)
        else:
            return jsonify({"timestamp": None, "status": 400, "error": "Bad Request", "message": "Provide city or lat+lon"}), 400

        data = fetch_weather(lat_f, lon_f)
        return jsonify({"location": {"lat": lat_f, "lon": lon_f}, "forecast": data["forecast"], "source": data.get("source", "open-meteo")}), 200

    except WeatherError as e:
        current_app.logger.error("WeatherError: %s", e.msg)
        return jsonify({"timestamp": None, "status": e.status, "error": "External Service", "message": e.msg}), e.status
    except Exception:
        current_app.logger.exception("Unexpected error in /weather_api")
        return jsonify({"timestamp": None, "status": 502, "error": "Bad Gateway", "message": "Unexpected error while fetching weather"}), 502
